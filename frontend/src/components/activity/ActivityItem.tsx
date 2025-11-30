import { type FC } from 'react';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { PATHS } from '@/constants/paths';
import {
  History,
  FileText,
  Languages,
  Trash,
  Plus,
  Edit,
  FileDown,
  Sparkles,
  MessageSquareHeart,
  MessageSquareX,
  MessageSquareOff,
  Users,
  UserPlus,
  UserMinus,
  Settings,
  Palette,
  Flag,
  Globe,
  FileUp,
  Mail,
} from 'lucide-react';
import type { ActivityLog } from '@/types/activity';
import {
  ReviewContent,
  ColorChangeContent,
  DiffContent,
  SimpleValueContent,
  LanguageInfoContent,
} from './content';

interface ActivityItemProps {
  log: ActivityLog;
  isLast: boolean;
  showProject?: boolean;
  showDiff?: boolean;
}

const actionLabels: Record<string, string> = {
  // Team lifecycle
  TEAM_CREATE: 'Team created',
  TEAM_UPDATE_NAME: 'Team renamed',
  TEAM_UPDATE_DESCRIPTION: 'Team description updated',
  TEAM_DELETE: 'Team deleted',
  // Project actions
  PROJECT_CREATE: 'Project created',
  PROJECT_UPDATE_NAME: 'Project renamed',
  PROJECT_UPDATE_DESCRIPTION: 'Description updated',
  PROJECT_UPDATE_LANGUAGES: 'Languages updated',
  PROJECT_UPDATE_DEFAULT_LANGUAGE: 'Default language changed',
  PROJECT_UPDATE_COLOR: 'Color changed',
  PROJECT_UPDATE_STATUS: 'Status changed',
  PROJECT_DELETE: 'Project deleted',
  PROJECT_EXPORT: 'Project exported',
  PROJECT_IMPORT: 'Project imported',
  // Team management
  MEMBER_ADD: 'Member added',
  MEMBER_REMOVE: 'Member removed',
  MEMBER_ROLE_CHANGE: 'Role changed',
  TEAM_INVITE: 'Invited',
  // Key actions
  KEY_CREATE: 'Key created',
  KEY_UPDATE: 'Key renamed',
  KEY_UPDATE_DESCRIPTION: 'Description updated',
  KEY_DELETE: 'Key deleted',
  // Translation actions
  TRANSLATION_UPDATE: 'Translation updated',
  TRANSLATION_AI_UPDATE: 'AI translation',
  TRANSLATION_DELETE: 'Translation deleted',
  TRANSLATION_IMPORT: 'Imported',
  // Review actions
  REVIEW_APPROVE: 'Approved',
  REVIEW_REJECT: 'Rejected',
  REVIEW_DELETE: 'Review revoked',
};

const actionIcons: Record<string, typeof History> = {
  // Team lifecycle
  TEAM_CREATE: Plus,
  TEAM_UPDATE_NAME: Edit,
  TEAM_UPDATE_DESCRIPTION: FileText,
  TEAM_DELETE: Trash,
  // Project actions
  PROJECT_CREATE: Plus,
  PROJECT_UPDATE_NAME: Edit,
  PROJECT_UPDATE_DESCRIPTION: FileText,
  PROJECT_UPDATE_LANGUAGES: Globe,
  PROJECT_UPDATE_DEFAULT_LANGUAGE: Globe,
  PROJECT_UPDATE_COLOR: Palette,
  PROJECT_UPDATE_STATUS: Flag,
  PROJECT_DELETE: Trash,
  PROJECT_EXPORT: FileDown,
  PROJECT_IMPORT: FileUp,
  // Team management
  MEMBER_ADD: UserPlus,
  MEMBER_REMOVE: UserMinus,
  MEMBER_ROLE_CHANGE: Users,
  TEAM_INVITE: Mail,
  // Key actions
  KEY_CREATE: Plus,
  KEY_UPDATE: Edit,
  KEY_UPDATE_DESCRIPTION: FileText,
  KEY_DELETE: Trash,
  // Translation actions
  TRANSLATION_UPDATE: Languages,
  TRANSLATION_AI_UPDATE: Sparkles,
  TRANSLATION_DELETE: Trash,
  TRANSLATION_IMPORT: FileDown,
  // Review actions
  REVIEW_APPROVE: MessageSquareHeart,
  REVIEW_REJECT: MessageSquareX,
  REVIEW_DELETE: MessageSquareOff,
};

const actionColors: Record<string, string> = {
  // Team lifecycle
  TEAM_CREATE: 'bg-green-500/10 text-green-600',
  TEAM_UPDATE_NAME: 'bg-blue-500/10 text-blue-600',
  TEAM_UPDATE_DESCRIPTION: 'bg-blue-500/10 text-blue-600',
  TEAM_DELETE: 'bg-red-500/10 text-red-600',
  // Project actions
  PROJECT_CREATE: 'bg-green-500/10 text-green-600',
  PROJECT_UPDATE_NAME: 'bg-blue-500/10 text-blue-600',
  PROJECT_UPDATE_DESCRIPTION: 'bg-blue-500/10 text-blue-600',
  PROJECT_UPDATE_LANGUAGES: 'bg-purple-500/10 text-purple-600',
  PROJECT_UPDATE_DEFAULT_LANGUAGE: 'bg-purple-500/10 text-purple-600',
  PROJECT_UPDATE_COLOR: 'bg-pink-500/10 text-pink-600',
  PROJECT_UPDATE_STATUS: 'bg-orange-500/10 text-orange-600',
  PROJECT_DELETE: 'bg-red-500/10 text-red-600',
  PROJECT_EXPORT: 'bg-cyan-500/10 text-cyan-600',
  PROJECT_IMPORT: 'bg-cyan-500/10 text-cyan-600',
  // Team management
  MEMBER_ADD: 'bg-green-500/10 text-green-600',
  MEMBER_REMOVE: 'bg-red-500/10 text-red-600',
  MEMBER_ROLE_CHANGE: 'bg-blue-500/10 text-blue-600',
  TEAM_INVITE: 'bg-cyan-500/10 text-cyan-600',
  // Key actions
  KEY_CREATE: 'bg-green-500/10 text-green-600',
  KEY_UPDATE: 'bg-blue-500/10 text-blue-600',
  KEY_UPDATE_DESCRIPTION: 'bg-blue-500/10 text-blue-600',
  KEY_DELETE: 'bg-red-500/10 text-red-600',
  // Translation actions
  TRANSLATION_UPDATE: 'bg-purple-500/10 text-purple-600',
  TRANSLATION_AI_UPDATE: 'bg-indigo-500/10 text-indigo-600',
  TRANSLATION_DELETE: 'bg-red-500/10 text-red-600',
  TRANSLATION_IMPORT: 'bg-cyan-500/10 text-cyan-600',
  // Review actions
  REVIEW_APPROVE: 'bg-green-500/10 text-green-600',
  REVIEW_REJECT: 'bg-red-500/10 text-red-600',
  REVIEW_DELETE: 'bg-gray-500/10 text-gray-600',
};

/**
 * Single activity item component for displaying one log entry
 */
export const ActivityItem: FC<ActivityItemProps> = ({ log, isLast, showProject = false, showDiff = true }) => {
  const Icon = actionIcons[log.action] || History;
  const colorClass = actionColors[log.action] || 'bg-gray-500/10 text-gray-600';
  const label = actionLabels[log.action] || log.action;

  return (
    <div className="relative flex gap-3 pl-0">
      {/* Timeline line */}
      {!isLast ? (
        <div className="absolute left-3 top-6 bottom-[-1rem] w-px bg-border" />
      ) : null}

      {/* Icon */}
      <div
        className={`flex-shrink-0 w-6 h-6 rounded-full ${colorClass} flex items-center justify-center z-3 relative`}
      >
        <Icon className="w-3.5 h-3.5" />
      </div>

      {/* Content */}
      <div className="flex-1 w-full pb-2">
        <div className="flex items-center justify-between gap-2 mb-1 pt-0.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-sm">{label}</span>
              {showProject && log.project ? (
                <span className="text-muted-foreground">
                  in{' '}
                  <Link 
                    to={PATHS.PROJECT.replace(':id', log.project.id)}
                    className="font-medium text-sm text-foreground hover:underline"
                  >
                    {log.project.name}
                  </Link>
                </span>
              ) : null}
            {log.user ? (
              <span className="text-xs text-muted-foreground">
                by {log.user.username || log.user.email}
              </span>
            ) : null}
            {log.affectedUser && (log.action === 'MEMBER_ADD' || log.action === 'MEMBER_REMOVE' || log.action === 'MEMBER_ROLE_CHANGE') ? (
              <span className="text-xs text-muted-foreground">
                → {log.affectedUser.username || log.affectedUser.email}
              </span>
            ) : null}
          </div>
          <span className="text-xs text-muted-foreground whitespace-nowrap">
            {formatDistanceToNow(new Date(log.createdAt), { addSuffix: true })}
          </span>
        </div>

        {/* Action details */}
        <div className="text-sm text-muted-foreground space-y-1">
          {/* Review actions */}
          {(log.action === 'REVIEW_APPROVE' ||
            log.action === 'REVIEW_REJECT' ||
            log.action === 'REVIEW_DELETE') ? (
            <ReviewContent
              action={log.action}
              language={log.language || undefined}
              newValue={log.newValue || undefined}
            />
          ) : log.action === 'PROJECT_UPDATE_COLOR' && (log.oldValue || log.newValue) ? (
            <ColorChangeContent
              oldValue={log.oldValue || undefined}
              newValue={log.newValue || undefined}
            />
          ) : showDiff && (log.oldValue || log.newValue) ? (
            <DiffContent
              oldValue={log.oldValue || undefined}
              newValue={log.newValue || undefined}
              language={log.language || undefined}
            />
          ) : !showDiff && (log.oldValue || log.newValue) ? (
            <SimpleValueContent
              oldValue={log.oldValue || undefined}
              newValue={log.newValue || undefined}
            />
          ) : null}

          {/* Language info if no values */}
          {!log.oldValue && !log.newValue && log.language ? (
            <LanguageInfoContent language={log.language} />
          ) : null}
        </div>
      </div>
    </div>
  );
};

