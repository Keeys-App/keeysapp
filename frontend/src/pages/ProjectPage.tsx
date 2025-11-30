import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@apollo/client";
import { GET_PROJECT, type GetProjectData } from "@/graphql/projects";
import { PATHS } from "@/constants/paths";
import { useAuth, useBreadcrumbs } from "@/contexts";
import { useEffect, type FC } from "react";
import { LoadingState, ErrorState, NotFoundState } from "@/components/blocks";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { 
  FileText, 
  Languages, 
  Users, 
  Calendar,
  Edit,
  FileDown,
  FileUp,
  Key,
  ArrowRight,
  Download
} from "lucide-react";
import { COMMON_LANGUAGES } from "@/types/project";
import { toast } from "sonner";
import { useSaving } from "@/stores";

export const ProjectPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { setBreadcrumbs } = useBreadcrumbs();
  const withSaving = useSaving();

  const { data, loading, error } = useQuery<GetProjectData>(GET_PROJECT, {
    variables: { id },
    skip: !id || !isAuthenticated || authLoading,
    fetchPolicy: 'cache-and-network', // Always fetch fresh data, show cached while loading
  });

  const project = data?.project;

  useEffect(() => {
    if (project) {
      setBreadcrumbs([
        { label: "Dashboard", href: PATHS.DASHBOARD },
        { label: project.name },
      ]);
    } else {
      setBreadcrumbs([
        { label: "Dashboard", href: PATHS.DASHBOARD },
        { label: "Project" },
      ]);
    }
  }, [project, setBreadcrumbs]);

  const handleBackClick = () => {
    navigate(PATHS.DASHBOARD);
  };

  const handleExportProject = async () => {
    if (!id) {
      return;
    }

    await withSaving(
      async () => {
        try {
          const token = localStorage.getItem("authToken");
          if (!token) {
            toast("Authentication required");
            return;
          }

          const API_BASE_URL =
            import.meta.env.VITE_API_URL || "http://localhost:8000";
          const response = await fetch(
            `${API_BASE_URL}/api/projects/${id}/export`,
            {
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (!response.ok) {
            throw new Error("Failed to export project");
          }

          const data = await response.json();
          const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: "application/json",
          });

          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `${data.name
            .replace(/\s+/g, "_")
            .toLowerCase()}_export.json`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);

          toast("Project exported successfully");
        } catch (error) {
          console.error("Export error:", error);
          toast("Failed to export project");
        }
      },
      "Exporting project..."
    );
  };

  if (loading) {
    return <LoadingState message="Loading project..." />;
  }

  if (error) {
    return (
      <ErrorState
        message={`Error loading project: ${error.message}`}
        onBack={handleBackClick}
        backLabel="Back to Dashboard"
      />
    );
  }

  if (!project) {
    return (
      <NotFoundState
        message="Project not found"
        onBack={handleBackClick}
        backLabel="Back to Dashboard"
      />
    );
  }

  const totalTranslations = project.keysCount * (project.languages?.length || 0);
  const completedTranslations = Math.round((totalTranslations * project.translationProgress) / 100);
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header Section */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: project.color }}
            />
            <h1 className="text-3xl font-bold">{project.name}</h1>
            <Badge variant="outline" className="capitalize">
              {project.status}
            </Badge>
          </div>
          {project.description ? (
            <p className="text-muted-foreground">{project.description}</p>
          ) : null}
        </div>
        <div className="flex gap-2">
          <Button
            onClick={handleExportProject}
            variant="outline"
          >
            <Download className="h-4 w-4" />
            Export Project
          </Button>
          {project.canEdit ? (
            <Button
              onClick={() => navigate(PATHS.PROJECT_EDIT.replace(':id', id!))}
              variant="outline"
            >
              <Edit className="h-4 w-4" />
              Edit Project
            </Button>
          ) : null}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="cursor-pointer hover:bg-accent transition-colors" onClick={() => navigate(PATHS.PROJECT_KEYS.replace(':id', id!))}>
          <CardContent className="flex items-center justify-between p-6">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Translation Keys</p>
              <p className="text-2xl font-bold">{project.keysCount}</p>
            </div>
            <div className="flex items-center gap-2">
              <Key className="h-8 w-8 text-muted-foreground" />
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:bg-accent transition-colors" onClick={() => navigate(PATHS.EXPORT.replace(':id', id!))}>
          <CardContent className="flex items-center justify-between p-6">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Export</p>
              <p className="text-sm">Download translations</p>
            </div>
            <div className="flex items-center gap-2">
              <FileDown className="h-8 w-8 text-muted-foreground" />
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:bg-accent transition-colors" onClick={() => navigate(PATHS.IMPORT.replace(':id', id!))}>
          <CardContent className="flex items-center justify-between p-6">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Import</p>
              <p className="text-sm">Upload translations</p>
            </div>
            <div className="flex items-center gap-2">
              <FileUp className="h-8 w-8 text-muted-foreground" />
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Translation Progress */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Translation Progress
            </CardTitle>
            <CardDescription>
              Overall completion status of your translations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Overall Progress</span>
                <span className="text-2xl font-bold">{project.translationProgress}%</span>
              </div>
              <Progress value={project.translationProgress} className="h-3" />
              <p className="text-sm text-muted-foreground">
                {completedTranslations} of {totalTranslations} translations completed
              </p>
            </div>

            <Separator />

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Total Keys</p>
                <p className="text-2xl font-bold">{project.keysCount}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Languages</p>
                <p className="text-2xl font-bold">{project.languages?.length || 0}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold text-green-600">{completedTranslations}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Remaining</p>
                <p className="text-2xl font-bold text-orange-600">{totalTranslations - completedTranslations}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Languages */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Languages className="h-5 w-5" />
              Languages
            </CardTitle>
            <CardDescription>
              {project.languages?.length || 0} language{(project.languages?.length || 0) !== 1 ? 's' : ''} configured
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {project.languages && project.languages.length > 0 ? (
              project.languages.map((langConfig) => {
                const language = COMMON_LANGUAGES.find(l => {
                  return l.code === langConfig.code;
                });
                const isDefault = langConfig.code === project.defaultLanguage;
                const langProgress = project.languageProgress?.find(lp => {
                  return lp.code === langConfig.code;
                });
                const progress = langProgress?.progress || 0;
                const completed = langProgress?.completed || 0;
                const total = langProgress?.total || 0;
                
                return (
                  <div key={langConfig.code} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{language?.flag || '🏳️'}</span>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-medium">{language?.name || langConfig.code}</p>
                            {isDefault ? (
                              <Badge variant="secondary" className="text-xs">
                                Default
                              </Badge>
                            ) : null}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {langConfig.code} · <code className="px-1 py-0.5 bg-muted rounded text-xs">{langConfig.locale}</code>
                          </p>
                        </div>
                      </div>
                      <span className="text-sm font-bold">{progress}%</span>
                    </div>
                    <div className="space-y-1">
                      <Progress value={progress} className="h-2" />
                      <p className="text-xs text-muted-foreground">
                        {completed} of {total} translations
                      </p>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-sm text-muted-foreground text-center py-4">
                No languages configured
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Team Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Team
          </CardTitle>
          <CardDescription>
            Project owner and members
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Owner */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Avatar>
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    {getInitials(project.owner.username)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium">{project.owner.username}</p>
                  <p className="text-xs text-muted-foreground">{project.owner.email}</p>
                </div>
              </div>
              <Badge>Owner</Badge>
            </div>

            {/* Members */}
            {project.accessMembers && project.accessMembers.length > 0 ? (
              <>
                <Separator />
                {project.accessMembers.map((member) => (
                  <div key={member.user.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarFallback>
                          {getInitials(member.user.username)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{member.user.username}</p>
                        <p className="text-xs text-muted-foreground">{member.user.email}</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="capitalize">
                      {member.role}
                    </Badge>
                  </div>
                ))}
              </>
            ) : null}
          </div>
        </CardContent>
      </Card>

      {/* Project Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Project Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Created</span>
            <span className="text-sm font-medium">{formatDate(project.createdAt)}</span>
          </div>
          {project.updatedAt ? (
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Last Updated</span>
              <span className="text-sm font-medium">{formatDate(project.updatedAt)}</span>
            </div>
          ) : null}
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Project ID</span>
            <span className="text-sm font-mono">{project.id}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
