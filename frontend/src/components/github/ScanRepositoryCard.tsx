import { useState, useEffect, type FC } from 'react';
import { useMutation, useQuery } from '@apollo/client';
import { 
  Search, 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  FileCode,
  ChevronDown,
  ChevronUp,
  Check,
  X,
  FolderOpen,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  PROJECT_SCAN_SESSIONS_QUERY,
  SCAN_SESSION_QUERY,
  START_REPOSITORY_SCAN_MUTATION,
  CANCEL_SCAN_MUTATION,
  UPDATE_FOUND_STRING_STATUS_MUTATION,
  CONVERT_FOUND_STRINGS_TO_KEYS_MUTATION,
  type ScanSession,
  type FoundString,
  ScanStatus,
  FoundStringStatus,
} from '@/graphql/scanner';
import { DirectoryPicker } from './DirectoryPicker';

interface ScanRepositoryCardProps {
  projectId: string;
  hasRepository: boolean;
  canManage?: boolean;
  className?: string;
}

export const ScanRepositoryCard: FC<ScanRepositoryCardProps> = ({
  projectId,
  hasRepository,
  canManage = false,
  className,
}) => {
  const [currentScanId, setCurrentScanId] = useState<string | null>(null);
  const [isResultsOpen, setIsResultsOpen] = useState(false);
  const [scanPath, setScanPath] = useState<string>('');
  const [scanPathError, setScanPathError] = useState<string | null>(null);
  
  // Query for scan sessions
  const { data: sessionsData, loading: sessionsLoading, refetch: refetchSessions } = useQuery<{
    projectScanSessions: ScanSession[];
  }>(PROJECT_SCAN_SESSIONS_QUERY, {
    variables: { projectId, limit: 5 },
    skip: !hasRepository,
    fetchPolicy: 'cache-and-network',
  });
  
  // Query for current scan session (polling when scanning)
  const { data: currentScanData, startPolling, stopPolling } = useQuery<{
    scanSession: ScanSession | null;
  }>(SCAN_SESSION_QUERY, {
    variables: { scanSessionId: currentScanId },
    skip: !currentScanId,
    fetchPolicy: 'network-only',
  });
  
  // Mutations
  const [startScan, { loading: startingScan }] = useMutation(START_REPOSITORY_SCAN_MUTATION);
  const [cancelScan, { loading: cancellingScan }] = useMutation(CANCEL_SCAN_MUTATION);
  const [updateStatus] = useMutation(UPDATE_FOUND_STRING_STATUS_MUTATION);
  const [convertToKeys, { loading: converting }] = useMutation(CONVERT_FOUND_STRINGS_TO_KEYS_MUTATION);
  
  const sessions = sessionsData?.projectScanSessions ?? [];
  const currentScan = currentScanData?.scanSession ?? (sessions.length > 0 ? sessions[0] : null);
  
  // Auto-select most recent scan on load (any status)
  useEffect(() => {
    if (sessions.length > 0 && !currentScanId) {
      // Always select the latest scan to load its details
      setCurrentScanId(sessions[0].id);
    }
  }, [sessions, currentScanId]);
  
  // Poll for updates when scanning
  useEffect(() => {
    if (currentScan?.status === ScanStatus.SCANNING || currentScan?.status === ScanStatus.PENDING) {
      startPolling(2000);
    } else {
      stopPolling();
    }
    
    return () => {
      stopPolling();
    };
  }, [currentScan?.status, startPolling, stopPolling]);
  
  const handleStartScan = async () => {
    // Clear previous error
    setScanPathError(null);
    
    try {
      const result = await startScan({
        variables: { 
          projectId,
          scanPath: scanPath.trim() || null,
        },
      });
      
      const { success, message, scanSession } = result.data?.startRepositoryScan ?? {};
      
      if (success && scanSession) {
        setCurrentScanId(scanSession.id);
        const scanDescription = scanPath 
          ? `Scanning directory "${scanPath}" for hardcoded strings...`
          : 'Scanning repository for hardcoded strings...';
        toast('Scan started', { description: scanDescription });
        refetchSessions();
      } else {
        // Check if error is about directory not found
        if (message?.includes('not found in repository')) {
          setScanPathError(message);
        } else {
          toast('Failed to start scan', { description: message });
        }
      }
    } catch (error) {
      toast('Error', { description: 'Failed to start scan. Please try again.' });
    }
  };
  
  const handleCancelScan = async () => {
    if (!currentScanId) {
      return;
    }
    
    try {
      const result = await cancelScan({
        variables: { scanSessionId: currentScanId },
      });
      
      const { success, message } = result.data?.cancelScan ?? {};
      
      if (success) {
        toast('Scan cancelled');
        refetchSessions();
      } else {
        toast('Failed to cancel scan', { description: message });
      }
    } catch (error) {
      toast('Error', { description: 'Failed to cancel scan. Please try again.' });
    }
  };
  
  const handleUpdateStatus = async (foundStringId: string, status: FoundStringStatus) => {
    try {
      await updateStatus({
        variables: { foundStringId, status },
        refetchQueries: [{ query: SCAN_SESSION_QUERY, variables: { scanSessionId: currentScanId } }],
      });
    } catch (error) {
      toast('Error', { description: 'Failed to update status.' });
    }
  };
  
  const handleConvertToKeys = async () => {
    if (!currentScanId) {
      return;
    }
    
    try {
      const result = await convertToKeys({
        variables: { scanSessionId: currentScanId },
        refetchQueries: [{ query: SCAN_SESSION_QUERY, variables: { scanSessionId: currentScanId } }],
      });
      
      const { success, message, keysCreated } = result.data?.convertFoundStringsToKeys ?? {};
      
      if (success) {
        toast('Keys created', { description: `Created ${keysCreated} translation keys` });
      } else {
        toast('Failed to create keys', { description: message });
      }
    } catch (error) {
      toast('Error', { description: 'Failed to create keys. Please try again.' });
    }
  };
  
  const getStatusIcon = (status: ScanStatus) => {
    switch (status) {
      case ScanStatus.PENDING:
      case ScanStatus.SCANNING:
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case ScanStatus.COMPLETED:
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case ScanStatus.FAILED:
        return <XCircle className="h-4 w-4 text-red-500" />;
      case ScanStatus.CANCELLED:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return null;
    }
  };
  
  const getStatusBadge = (status: ScanStatus) => {
    const variants: Record<ScanStatus, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      [ScanStatus.PENDING]: 'secondary',
      [ScanStatus.SCANNING]: 'default',
      [ScanStatus.COMPLETED]: 'default',
      [ScanStatus.FAILED]: 'destructive',
      [ScanStatus.CANCELLED]: 'outline',
    };
    
    return (
      <Badge variant={variants[status]} className="gap-1">
        {getStatusIcon(status)}
        {status}
      </Badge>
    );
  };
  
  const approvedCount = currentScan?.foundStrings.filter(s => s.status === FoundStringStatus.APPROVED).length ?? 0;
  const pendingCount = currentScan?.foundStrings.filter(s => s.status === FoundStringStatus.PENDING).length ?? 0;
  
  if (!hasRepository) {
    return null;
  }
  
  const isScanning = currentScan?.status === ScanStatus.SCANNING || currentScan?.status === ScanStatus.PENDING;
  const progress = currentScan?.filesTotal ? (currentScan.filesScanned / currentScan.filesTotal) * 100 : 0;
  
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Search className="h-5 w-5" />
            <CardTitle>Find Hardcoded Strings</CardTitle>
          </div>
          {currentScan ? getStatusBadge(currentScan.status) : null}
        </div>
        <CardDescription>
          Scan your repository to find user-facing strings that need localization.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Scanning Progress */}
        {isScanning ? (
          <div className="space-y-2">
            {/* Scanned directory info */}
            {currentScan?.scanPath ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FolderOpen className="h-4 w-4" />
                <span>Scanning:</span>
                <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                  /{currentScan.scanPath}
                </code>
              </div>
            ) : null}
            <div className="flex items-center justify-between text-sm">
              <span>Scanning files...</span>
              <span>{currentScan?.filesScanned ?? 0} / {currentScan?.filesTotal ?? 0}</span>
            </div>
            <Progress value={progress} className="h-2" />
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                {currentScan?.stringsFound ?? 0} strings found
              </span>
              {canManage ? (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleCancelScan}
                  disabled={cancellingScan}
                >
                  Cancel
                </Button>
              ) : null}
            </div>
          </div>
        ) : null}
        
        {/* Completed Scan Results */}
        {currentScan?.status === ScanStatus.COMPLETED && currentScan.foundStrings.length > 0 ? (
          <Collapsible open={isResultsOpen} onOpenChange={setIsResultsOpen}>
            {/* Scanned directory info */}
            {currentScan.scanPath ? (
              <div className="mb-3 flex items-center gap-2 text-sm text-muted-foreground">
                <FolderOpen className="h-4 w-4" />
                <span>Scanned directory:</span>
                <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                  /{currentScan.scanPath}
                </code>
              </div>
            ) : null}
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCode className="h-4 w-4" />
                <span className="font-medium">{currentScan.stringsFound} strings found</span>
                <Badge variant="secondary">{approvedCount} approved</Badge>
                <Badge variant="outline">{pendingCount} pending</Badge>
              </div>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" size="sm">
                  {isResultsOpen ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </CollapsibleTrigger>
            </div>
            
            <CollapsibleContent className="mt-4">
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[200px]">Key</TableHead>
                      <TableHead>Text</TableHead>
                      <TableHead className="w-[150px]">File</TableHead>
                      <TableHead className="w-[100px]">Status</TableHead>
                      {canManage ? <TableHead className="w-[100px]">Actions</TableHead> : null}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {currentScan.foundStrings.map((fs) => (
                      <TableRow key={fs.id}>
                        <TableCell className="font-mono text-xs">{fs.suggestedKey}</TableCell>
                        <TableCell className="max-w-[300px] truncate">{fs.originalText}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {fs.filePath.split('/').pop()}:{fs.lineNumber}
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={
                              fs.status === FoundStringStatus.APPROVED ? 'default' :
                              fs.status === FoundStringStatus.CONVERTED ? 'default' :
                              fs.status === FoundStringStatus.SKIPPED ? 'secondary' :
                              'outline'
                            }
                            className={cn(
                              fs.status === FoundStringStatus.APPROVED && 'bg-green-500',
                              fs.status === FoundStringStatus.CONVERTED && 'bg-blue-500',
                            )}
                          >
                            {fs.status}
                          </Badge>
                        </TableCell>
                        {canManage ? (
                          <TableCell>
                            {fs.status === FoundStringStatus.PENDING ? (
                              <div className="flex gap-1">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7"
                                  onClick={() => { handleUpdateStatus(fs.id, FoundStringStatus.APPROVED); }}
                                  title="Approve"
                                >
                                  <Check className="h-4 w-4 text-green-500" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7"
                                  onClick={() => { handleUpdateStatus(fs.id, FoundStringStatus.SKIPPED); }}
                                  title="Skip"
                                >
                                  <X className="h-4 w-4 text-red-500" />
                                </Button>
                              </div>
                            ) : null}
                          </TableCell>
                        ) : null}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              {canManage && approvedCount > 0 ? (
                <div className="mt-4 flex justify-end">
                  <Button onClick={handleConvertToKeys} disabled={converting}>
                    {converting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Create {approvedCount} Keys
                  </Button>
                </div>
              ) : null}
            </CollapsibleContent>
          </Collapsible>
        ) : null}
        
        {/* Error State */}
        {currentScan?.status === ScanStatus.FAILED ? (
          <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
            <XCircle className="h-4 w-4" />
            <span className="text-sm">{currentScan.errorMessage ?? 'Scan failed'}</span>
          </div>
        ) : null}
        
        {/* Directory Selection and Start Button */}
        {!isScanning && canManage ? (
          <div className="space-y-4">
            {/* Directory Picker */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <FolderOpen className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Scan Directory</span>
              </div>
              <DirectoryPicker
                projectId={projectId}
                value={scanPath}
                onChange={(value) => {
                  setScanPath(value);
                  setScanPathError(null);
                }}
                error={scanPathError}
                placeholder="Enter directory path or select from list"
                disabled={startingScan || sessionsLoading}
              />
            </div>
            
            {/* Start Button */}
            <Button 
              onClick={handleStartScan} 
              disabled={startingScan || sessionsLoading}
              className="w-full"
            >
              {startingScan ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Search className="mr-2 h-4 w-4" />
              )}
              {currentScan ? 'Start New Scan' : 'Find Keys'}
            </Button>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
};

