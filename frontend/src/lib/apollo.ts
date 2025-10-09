import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { PATHS } from '../constants/paths';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const httpLink = createHttpLink({
  uri: `${API_BASE_URL}/graphql`,
});

const authLink = setContext((_, { headers }) => {
  // Get the authentication token from local storage if it exists
  const token = localStorage.getItem('authToken');
  
  // Return the headers to the context so httpLink can read them
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  };
});

// Error handling link to catch authentication errors
const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    for (const err of graphQLErrors) {
      // Check for authentication/authorization errors
      if (
        err.extensions?.code === 'UNAUTHENTICATED' ||
        err.message.includes('Authentication required') ||
        err.message.includes('Not authenticated') ||
        err.message.includes('Invalid token') ||
        err.message.includes('Token expired')
      ) {
        // Clear auth data and redirect to login
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
        window.location.href = PATHS.AUTH;
        return;
      }
    }
  }

  if (networkError) {
    // Check for 401/403 HTTP errors
    if ('statusCode' in networkError) {
      const statusCode = networkError.statusCode;
      if (statusCode === 401 || statusCode === 403) {
        // Clear auth data and redirect to login
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
        window.location.href = PATHS.AUTH;
        return;
      }
    }
  }
});

export const apolloClient = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
    },
    query: {
      errorPolicy: 'all',
    },
    mutate: {
      errorPolicy: 'none', // Throw errors for mutations
    },
  },
});
