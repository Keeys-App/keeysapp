import { Box, Button, Card, Flex, Heading, Text, TextField } from '@radix-ui/themes'

function App() {
  return (
    <Box p="6" style={{ minHeight: '100vh' }}>
      <Flex direction="column" gap="6" align="center">
        <Heading size="8">React + GraphQL + Radix UI</Heading>
        
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
              <TextField.Root placeholder="Enter your email" />
              <Button size="3" style={{ width: '100%' }}>
                Get Started
              </Button>
            </Flex>
          </Flex>
        </Card>

        <Flex gap="3" wrap="wrap" justify="center">
          <Button variant="solid">Solid Button</Button>
          <Button variant="soft">Soft Button</Button>
          <Button variant="outline">Outline Button</Button>
          <Button variant="ghost">Ghost Button</Button>
        </Flex>
      </Flex>
    </Box>
  )
}

export default App
