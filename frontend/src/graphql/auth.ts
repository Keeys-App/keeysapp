import { gql } from '@apollo/client';

export const REGISTER_MUTATION = gql`
  mutation Register($input: RegisterInput!) {
    register(input: $input) {
      accessToken
      tokenType
      user {
        id
        email
        username
        isActive
        isSuperuser
        onboardingCompleted
      }
    }
  }
`;

export const LOGIN_MUTATION = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      accessToken
      tokenType
      user {
        id
        email
        username
        isActive
        isSuperuser
        onboardingCompleted
      }
    }
  }
`;

export const ME_QUERY = gql`
  query Me {
    me {
      id
      email
      username
      isActive
      isSuperuser
      onboardingCompleted
    }
  }
`;

export const COMPLETE_ONBOARDING_MUTATION = gql`
  mutation CompleteOnboarding {
    completeOnboarding {
      id
      email
      username
      isActive
      isSuperuser
      onboardingCompleted
    }
  }
`;

