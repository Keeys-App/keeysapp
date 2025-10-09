import { gql } from '@apollo/client';

export interface User {
  id: number;
  name: string;
  email: string;
}

// Demo queries
export const HELLO_QUERY = gql`
  query Hello {
    hello
  }
`;

export const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
      email
    }
  }
`;

// Demo mutations
export const CREATE_USER = gql`
  mutation CreateUser($name: String!, $email: String!) {
    createUser(name: $name, email: $email) {
      id
      name
      email
    }
  }
`;
