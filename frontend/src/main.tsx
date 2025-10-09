import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ApolloProvider } from '@apollo/client';
import '@fontsource/geist-sans/400.css';
import '@fontsource/geist-sans/500.css';
import '@fontsource/geist-sans/600.css';
import '@fontsource/geist-sans/700.css';
import '@fontsource/geist-mono/400.css';
import '@fontsource/geist-mono/700.css';
import './index.css';
import App from './App.tsx';
import { apolloClient } from './lib/apollo';
import { ThemeProvider } from './contexts/ThemeContext';
import { BreadcrumbProvider } from './contexts';

function AppWithProviders() {
  return (
    <ApolloProvider client={apolloClient}>
      <ThemeProvider>
        <BreadcrumbProvider>
          <App />
        </BreadcrumbProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppWithProviders />
  </StrictMode>
);
