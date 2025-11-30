import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { ApolloError } from '@apollo/client';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Get user-friendly error message from GraphQL error.
 * IMPORTANT: Never expose technical error details to end users.
 * 
 * @param error - Apollo/GraphQL error
 * @param fallbackMessage - User-friendly fallback message
 * @returns User-friendly error message
 */
export function getUserFriendlyErrorMessage(
  error: ApolloError | Error,
  fallbackMessage: string = 'An error occurred. Please try again.'
): string {
  // Log technical error for developers
  console.error('GraphQL Error:', error);

  // Check if it's an ApolloError with GraphQL errors
  if (error instanceof ApolloError) {
    const firstError = error.graphQLErrors?.[0];
    
    if (firstError) {
      const extensions = firstError.extensions;
      
      // Handle specific error codes with user-friendly messages
      if (extensions?.code) {
        switch (extensions.code) {
          case 'UNAUTHENTICATED':
            return 'You need to be logged in to perform this action.';
          case 'FORBIDDEN':
            return 'You do not have permission to perform this action.';
          case 'BAD_USER_INPUT':
            return 'Please check your input and try again.';
          case 'NOT_FOUND':
            return 'The requested resource was not found.';
          default:
            // Don't expose the error code to users
            break;
        }
      }
      
      // Check for known safe messages that we can show to users
      const message = firstError.message;
      if (message) {
        // List of safe user-facing error patterns
        const safeErrorPatterns = [
          'already exists',
          'already registered',
          'already taken',
          'not found',
          'required',
          'invalid',
          'too short',
          'too long',
          'must be',
          'cannot be',
          'does not match',
          'incorrect',
          'failed',
          'Authentication required',
          'Permission denied',
        ];
        
        // Check if the message contains any safe error pattern
        const isSafeMessage = safeErrorPatterns.some(pattern => 
          message.toLowerCase().includes(pattern.toLowerCase())
        );
        
        if (isSafeMessage) {
          // Sanitize the message - remove technical details like variable paths
          let cleanMessage = message
            .replace(/Variable.*?;/, '')
            .replace(/\$\w+/, '')
            .replace(/input\.\w+:?/, '')
            .trim();
          
          // Ensure first letter is capitalized and message ends with period
          if (cleanMessage) {
            cleanMessage = cleanMessage.charAt(0).toUpperCase() + cleanMessage.slice(1);
            if (!cleanMessage.endsWith('.') && !cleanMessage.endsWith('!') && !cleanMessage.endsWith('?')) {
              cleanMessage += '.';
            }
            return cleanMessage;
          }
        }
      }
    }
    
    // Check for network errors
    if (error.networkError) {
      return 'Unable to connect to the server. Please check your internet connection.';
    }
  }
  
  // For any other error, return the generic fallback message
  return fallbackMessage;
}
