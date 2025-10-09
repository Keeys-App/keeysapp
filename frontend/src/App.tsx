import { Box, Button, Card, Flex, Heading, Text, TextField, IconButton } from '@radix-ui/themes'
import { SunIcon, MoonIcon } from '@radix-ui/react-icons'
import { useTheme } from './contexts/ThemeContext'

function App() {
  const { theme, toggleTheme } = useTheme()

  return (
    <Box p="6" style={{ minHeight: '100vh' }}>
      <Flex direction="column" gap="6" align="center">
        <Flex align="center" gap="4" style={{ width: '100%', maxWidth: 600 }}>
          <Heading size="8" style={{ flex: 1 }}>React + GraphQL + Radix UI</Heading>
          <IconButton 
            variant="ghost" 
            size="3"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
          >
            {theme === 'light' ? <MoonIcon /> : <SunIcon />}
          </IconButton>
        </Flex>
        
        <Card size="3" style={{ maxWidth: 600, width: '100%' }}>
          <Flex direction="column" gap="4">
            <Heading size="5">Welcome!</Heading>
            <Text size="3" color="gray">
              Your application is ready for development with Radix UI components.
            </Text>
            <Text size="2" color="gray">
              GraphQL endpoint: <code>http://localhost:8000/graphql</code>
            </Text>
            
            <Flex direction="column" gap="3" mt="4">
              <TextField.Root size="3" placeholder="Enter your email" />
              <Button size="3" style={{ width: '100%' }}>
                Get Started
              </Button>
            </Flex>
          </Flex>
        </Card>
      </Flex>
    </Box>
  )
}

export default App
