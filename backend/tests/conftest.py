"""
Integration test fixtures.

Tests run against a real server at http://localhost:8000/graphql
Server must be running before executing tests.
"""
import pytest
import httpx
from dataclasses import dataclass
from typing import Optional


# Server URL
BASE_URL = "http://localhost:8000"
GRAPHQL_URL = f"{BASE_URL}/graphql"


@dataclass
class GraphQLResponse:
    """GraphQL response wrapper."""
    data: Optional[dict]
    errors: Optional[list]


class GraphQLClient:
    """
    HTTP client for GraphQL requests.
    Works exactly like frontend - sends POST to /graphql.
    """
    def __init__(self):
        self._token: Optional[str] = None
    
    def set_token(self, token: str):
        """Set authorization token."""
        self._token = token
    
    def clear_token(self):
        """Clear authorization token."""
        self._token = None
    
    def _get_headers(self) -> dict:
        """Build HTTP headers."""
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers
    
    async def execute_async(self, query: str, variables: dict = None) -> GraphQLResponse:
        """Execute GraphQL query/mutation via HTTP POST."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GRAPHQL_URL,
                json=payload,
                headers=self._get_headers(),
                timeout=30.0
            )
        
        json_data = response.json()
        return GraphQLResponse(
            data=json_data.get("data"),
            errors=json_data.get("errors")
        )


@pytest.fixture
def graphql_client():
    """GraphQL client without authentication."""
    return GraphQLClient()


@pytest.fixture
def unauthenticated_graphql_client():
    """Alias for graphql_client."""
    return GraphQLClient()


import pytest_asyncio


@pytest_asyncio.fixture
async def authenticated_graphql_client(graphql_client):
    """
    GraphQL client authenticated with a test user.
    Creates a test user and logs in.
    """
    import uuid
    
    # Generate unique credentials for this test
    unique_id = uuid.uuid4().hex[:8]
    email = f"test_{unique_id}@example.com"
    username = f"testuser_{unique_id}"
    password = "TestPassword123!"
    
    # Register user
    register_query = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                accessToken
                user {
                    id
                    email
                    username
                }
            }
        }
    """
    register_variables = {
        "input": {
            "email": email,
            "username": username,
            "password": password
        }
    }
    
    result = await graphql_client.execute_async(register_query, register_variables)
    
    if result.errors:
        pytest.fail(f"Failed to register test user: {result.errors}")
    
    token = result.data["register"]["accessToken"]
    graphql_client.set_token(token)
    
    # Store user info on client for tests that need it
    graphql_client.test_user = result.data["register"]["user"]
    graphql_client.test_user["email"] = email
    graphql_client.test_user["username"] = username
    
    return graphql_client
