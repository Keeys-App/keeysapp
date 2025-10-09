import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ApolloProvider } from '@apollo/client'
import { Theme } from '@radix-ui/themes'
import './index.css'
import App from './App.tsx'
import { apolloClient } from './lib/apollo'
import { ThemeProvider, useTheme } from './contexts/ThemeContext'

function ThemedApp() {
  const { theme } = useTheme()
  
  return (
    <Theme 
      appearance={theme} 
      accentColor="blue" 
      grayColor="gray" 
      radius="medium"
    >
      <App />
    </Theme>
  )
}

function AppWithProviders() {
  return (
    <ThemeProvider>
      <ThemedApp />
    </ThemeProvider>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ApolloProvider client={apolloClient}>
      <AppWithProviders />
    </ApolloProvider>
  </StrictMode>,
)
