import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ApolloProvider } from '@apollo/client';
import './index.css';
import App from './App.tsx';
import { apolloClient } from './lib/apollo';
import { ThemeProvider } from './contexts/ThemeContext';

function AppWithProviders() {
  return (
    <ApolloProvider client={apolloClient}>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </ApolloProvider>
  );
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppWithProviders />
  </StrictMode>
);
