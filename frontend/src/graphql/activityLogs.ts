import { gql } from '@apollo/client';

export const GET_TEAM_ACTIVITY = gql`
  query GetTeamActivity($teamId: String!, $limit: Int) {
    teamActivity(teamId: $teamId, limit: $limit) {
      id
      projectId
      keyId
      userId
      affectedUserId
      user {
        id
        email
        username
      }
      affectedUser {
        id
        email
        username
      }
      project {
        id
        name
        color
      }
      action
      fieldName
      language
      oldValue
      newValue
      createdAt
    }
  }
`;

export const GET_PROJECT_ACTIVITY = gql`
  query GetProjectActivity($projectId: String!, $limit: Int) {
    projectActivity(projectId: $projectId, limit: $limit) {
      id
      projectId
      keyId
      userId
      affectedUserId
      user {
        id
        email
        username
      }
      affectedUser {
        id
        email
        username
      }
      action
      fieldName
      language
      oldValue
      newValue
      createdAt
    }
  }
`;

