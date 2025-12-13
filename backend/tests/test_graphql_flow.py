"""
End-to-End Integration Test Flow.

Tests the complete user journey through the application:
1. Registration → Login → Profile → Password change
2. Team creation → Project creation
3. Invite flow (invite → accept)
4. Key management (create → translate → review → delete)
5. Cleanup (delete project → delete team)

Run against http://localhost:8000/graphql
"""
import pytest
import uuid
from tests.conftest import GraphQLClient, GRAPHQL_URL


class TestCompleteUserFlow:
    """
    Complete E2E test that follows a realistic user journey.
    Tests are ordered and share state via class attributes.
    """
    
    # Shared state between tests
    user_email: str = None
    user_password: str = None
    user_token: str = None
    user_id: str = None
    
    second_user_email: str = None
    second_user_token: str = None
    second_user_id: str = None
    
    team_id: str = None
    project_id: str = None
    key_id: str = None
    invitation_code: str = None

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup client for each test."""
        self.client = GraphQLClient()

    # =========================================================================
    # PHASE 1: User Registration & Authentication
    # =========================================================================

    @pytest.mark.asyncio
    async def test_01_register_user(self):
        """Step 1: Register a new user."""
        unique_id = uuid.uuid4().hex[:8]
        TestCompleteUserFlow.user_email = f"flow_user_{unique_id}@example.com"
        TestCompleteUserFlow.user_password = "FlowPassword123!"
        
        query = """
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
        
        result = await self.client.execute_async(query, {
            "input": {
                "email": TestCompleteUserFlow.user_email,
                "username": f"flowuser_{unique_id}",
                "password": TestCompleteUserFlow.user_password
            }
        })
        
        assert result.errors is None, f"Registration failed: {result.errors}"
        assert result.data["register"]["accessToken"] is not None
        
        TestCompleteUserFlow.user_token = result.data["register"]["accessToken"]
        TestCompleteUserFlow.user_id = result.data["register"]["user"]["id"]
        
        print(f"✓ User registered: {TestCompleteUserFlow.user_email}")

    @pytest.mark.asyncio
    async def test_02_login_user(self):
        """Step 2: Login with registered credentials."""
        query = """
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    accessToken
                    user {
                        email
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "email": TestCompleteUserFlow.user_email,
                "password": TestCompleteUserFlow.user_password
            }
        })
        
        assert result.errors is None, f"Login failed: {result.errors}"
        assert result.data["login"]["accessToken"] is not None
        assert result.data["login"]["user"]["email"] == TestCompleteUserFlow.user_email
        
        # Update token (login gives new token)
        TestCompleteUserFlow.user_token = result.data["login"]["accessToken"]
        
        print(f"✓ User logged in: {TestCompleteUserFlow.user_email}")

    @pytest.mark.asyncio
    async def test_03_get_profile(self):
        """Step 3: Get current user profile."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            query Me {
                me {
                    id
                    email
                    username
                    onboardingCompleted
                }
            }
        """
        
        result = await self.client.execute_async(query)
        
        assert result.errors is None, f"Get profile failed: {result.errors}"
        assert result.data["me"]["email"] == TestCompleteUserFlow.user_email
        
        print(f"✓ Profile retrieved: {result.data['me']['username']}")

    @pytest.mark.asyncio
    async def test_04_update_profile(self):
        """Step 4: Update user profile."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        new_username = f"updated_flow_{uuid.uuid4().hex[:6]}"
        
        query = """
            mutation UpdateProfile($input: UpdateProfileInput!) {
                updateProfile(input: $input) {
                    success
                    user {
                        username
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {"username": new_username}
        })
        
        assert result.errors is None, f"Update profile failed: {result.errors}"
        assert result.data["updateProfile"]["success"] is True
        assert result.data["updateProfile"]["user"]["username"] == new_username
        
        print(f"✓ Profile updated: {new_username}")

    @pytest.mark.asyncio
    async def test_05_change_password(self):
        """Step 5: Change password."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        new_password = "NewFlowPassword456!"
        
        query = """
            mutation ChangePassword($input: ChangePasswordInput!) {
                changePassword(input: $input) {
                    success
                    message
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "currentPassword": TestCompleteUserFlow.user_password,
                "newPassword": new_password
            }
        })
        
        assert result.errors is None, f"Change password failed: {result.errors}"
        assert result.data["changePassword"]["success"] is True
        
        TestCompleteUserFlow.user_password = new_password
        
        print("✓ Password changed")

    @pytest.mark.asyncio
    async def test_06_login_with_new_password(self):
        """Step 6: Verify login works with new password."""
        query = """
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    accessToken
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "email": TestCompleteUserFlow.user_email,
                "password": TestCompleteUserFlow.user_password
            }
        })
        
        assert result.errors is None, f"Login with new password failed: {result.errors}"
        assert result.data["login"]["accessToken"] is not None
        
        TestCompleteUserFlow.user_token = result.data["login"]["accessToken"]
        
        print("✓ Login with new password successful")

    @pytest.mark.asyncio
    async def test_07_complete_onboarding(self):
        """Step 7: Complete user onboarding."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation CompleteOnboarding {
                completeOnboarding {
                    id
                    onboardingCompleted
                }
            }
        """
        
        result = await self.client.execute_async(query)
        
        assert result.errors is None, f"Complete onboarding failed: {result.errors}"
        assert result.data["completeOnboarding"]["onboardingCompleted"] is True
        
        print("✓ Onboarding completed")

    # =========================================================================
    # PHASE 2: Team & Project Management
    # =========================================================================

    @pytest.mark.asyncio
    async def test_08_create_team(self):
        """Step 8: Create a team."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        unique_id = uuid.uuid4().hex[:8]
        
        query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) {
                    id
                    name
                    owner {
                        id
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "name": f"Flow Team {unique_id}",
                "description": "Team created during E2E flow test"
            }
        })
        
        assert result.errors is None, f"Create team failed: {result.errors}"
        assert result.data["createTeam"]["owner"]["id"] == TestCompleteUserFlow.user_id
        
        TestCompleteUserFlow.team_id = result.data["createTeam"]["id"]
        
        print(f"✓ Team created: {result.data['createTeam']['name']}")

    @pytest.mark.asyncio
    async def test_09_create_project(self):
        """Step 9: Create a project in the team."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        unique_id = uuid.uuid4().hex[:8]
        
        query = """
            mutation CreateProject($input: CreateProjectInput!) {
                createProject(input: $input) {
                    id
                    name
                    languages {
                        code
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "name": f"Flow Project {unique_id}",
                "description": "Project created during E2E flow test",
                "teamId": TestCompleteUserFlow.team_id,
                "languages": [
                    {"code": "en", "locale": "en-US", "direction": "ltr"},
                    {"code": "ru", "locale": "ru-RU", "direction": "ltr"},
                    {"code": "de", "locale": "de-DE", "direction": "ltr"}
                ],
                "defaultLanguage": "en",
                "color": "#6366f1",
                "status": "active"
            }
        })
        
        assert result.errors is None, f"Create project failed: {result.errors}"
        
        TestCompleteUserFlow.project_id = result.data["createProject"]["id"]
        
        print(f"✓ Project created: {result.data['createProject']['name']}")

    # =========================================================================
    # PHASE 3: Team Invitation Flow
    # =========================================================================

    @pytest.mark.asyncio
    async def test_10_register_second_user(self):
        """Step 10: Register a second user (to invite)."""
        unique_id = uuid.uuid4().hex[:8]
        TestCompleteUserFlow.second_user_email = f"flow_invited_{unique_id}@example.com"
        
        query = """
            mutation Register($input: RegisterInput!) {
                register(input: $input) {
                    accessToken
                    user {
                        id
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "email": TestCompleteUserFlow.second_user_email,
                "username": f"invited_{unique_id}",
                "password": "InvitedUser123!"
            }
        })
        
        assert result.errors is None, f"Register second user failed: {result.errors}"
        
        TestCompleteUserFlow.second_user_token = result.data["register"]["accessToken"]
        TestCompleteUserFlow.second_user_id = result.data["register"]["user"]["id"]
        
        print(f"✓ Second user registered: {TestCompleteUserFlow.second_user_email}")

    @pytest.mark.asyncio
    async def test_11_invite_user_to_team(self):
        """Step 11: Invite second user to team."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation AddTeamMember($input: AddTeamMemberInput!) {
                addTeamMember(input: $input) {
                    id
                    members {
                        user {
                            email
                        }
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "teamId": TestCompleteUserFlow.team_id,
                "userEmail": TestCompleteUserFlow.second_user_email,
                "role": "editor"
            }
        })
        
        assert result.errors is None, f"Invite user failed: {result.errors}"
        
        print(f"✓ User invited to team")

    @pytest.mark.asyncio
    async def test_12_check_pending_invites(self):
        """Step 12: Second user checks pending invites."""
        self.client.set_token(TestCompleteUserFlow.second_user_token)
        
        query = """
            query MyPendingInvites {
                myPendingInvites {
                    id
                    teamName
                    role
                }
            }
        """
        
        result = await self.client.execute_async(query)
        
        assert result.errors is None, f"Get pending invites failed: {result.errors}"
        assert len(result.data["myPendingInvites"]) >= 1
        
        # Find our invitation
        invite = next(
            (i for i in result.data["myPendingInvites"] if i["role"] == "editor"),
            None
        )
        assert invite is not None, "Invitation not found"
        
        # id is used as code for acceptInvite
        TestCompleteUserFlow.invitation_code = invite["id"]
        
        print(f"✓ Found pending invite: {invite['teamName']}")

    @pytest.mark.asyncio
    async def test_13_accept_invite(self):
        """Step 13: Second user accepts invitation."""
        self.client.set_token(TestCompleteUserFlow.second_user_token)
        
        query = """
            mutation AcceptInvite($code: String!) {
                acceptInvite(code: $code) {
                    id
                    name
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "code": TestCompleteUserFlow.invitation_code
        })
        
        assert result.errors is None, f"Accept invite failed: {result.errors}"
        
        print(f"✓ Invitation accepted, joined team: {result.data['acceptInvite']['name']}")

    # =========================================================================
    # PHASE 4: Key & Translation Management
    # =========================================================================

    @pytest.mark.asyncio
    async def test_14_create_key(self):
        """Step 14: Create a translation key."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        unique_id = uuid.uuid4().hex[:8]
        
        query = """
            mutation CreateKey($input: CreateKeyInput!) {
                createKey(input: $input) {
                    id
                    key
                    translations {
                        language
                        value
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "projectId": TestCompleteUserFlow.project_id,
                "key": f"flow.button.submit.{unique_id}",
                "description": "Submit button text",
                "tags": ["ui", "button"],
                "translations": {"en": "Submit"}
            }
        })
        
        assert result.errors is None, f"Create key failed: {result.errors}"
        
        TestCompleteUserFlow.key_id = result.data["createKey"]["id"]
        
        print(f"✓ Key created: {result.data['createKey']['key']}")

    @pytest.mark.asyncio
    async def test_15_create_key_with_autopilot(self):
        """Step 15: Create key with AI autopilot translation."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        unique_id = uuid.uuid4().hex[:8]
        
        query = """
            mutation CreateKey($input: CreateKeyInput!) {
                createKey(input: $input) {
                    id
                    key
                    translations {
                        language
                        value
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "projectId": TestCompleteUserFlow.project_id,
                "key": f"flow.welcome.message.{unique_id}",
                "description": "Welcome message for new users",
                "translations": {"en": "Welcome to our application!"},
                "autopilot": True
            }
        })
        
        assert result.errors is None, f"Create key with autopilot failed: {result.errors}"
        
        translations = result.data["createKey"]["translations"]
        languages = [t["language"] for t in translations]
        
        # Autopilot should generate Russian and German translations
        assert "en" in languages
        assert "ru" in languages or "de" in languages, "Autopilot should generate translations"
        
        print(f"✓ Key created with autopilot: {len(translations)} translations generated")

    @pytest.mark.asyncio
    async def test_16_add_translation(self):
        """Step 16: Add a translation to existing key."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation SetTranslation($input: SetTranslationInput!) {
                setTranslation(input: $input) {
                    language
                    value
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "keyId": TestCompleteUserFlow.key_id,
                "language": "ru",
                "value": "Enviar"
            }
        })
        
        assert result.errors is None, f"Set translation failed: {result.errors}"
        assert result.data["setTranslation"]["value"] == "Enviar"
        
        print("✓ Russian translation added")

    @pytest.mark.asyncio
    async def test_17_add_german_translation(self):
        """Step 17: Add German translation."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation SetTranslation($input: SetTranslationInput!) {
                setTranslation(input: $input) {
                    language
                    value
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "keyId": TestCompleteUserFlow.key_id,
                "language": "de",
                "value": "Absenden"
            }
        })
        
        assert result.errors is None, f"Set German translation failed: {result.errors}"
        
        print("✓ German translation added")

    @pytest.mark.asyncio
    async def test_18_approve_translation(self):
        """Step 18: Approve a translation."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation ApproveTranslation($input: ApproveTranslationInput!) {
                approveTranslation(input: $input) {
                    id
                    translations {
                        language
                        reviewStatus
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "keyId": TestCompleteUserFlow.key_id,
                "language": "en"
            }
        })
        
        assert result.errors is None, f"Approve translation failed: {result.errors}"
        
        translations = result.data["approveTranslation"]["translations"]
        en_translation = next((t for t in translations if t["language"] == "en"), None)
        assert en_translation["reviewStatus"] == "APPROVED"
        
        print("✓ English translation approved")

    @pytest.mark.asyncio
    async def test_19_reject_translation(self):
        """Step 19: Reject a translation with comment."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation RejectTranslation($input: RejectTranslationInput!) {
                rejectTranslation(input: $input) {
                    id
                    translations {
                        language
                        reviewStatus
                    }
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "keyId": TestCompleteUserFlow.key_id,
                "language": "de",
                "comment": "Please use more formal language"
            }
        })
        
        assert result.errors is None, f"Reject translation failed: {result.errors}"
        
        translations = result.data["rejectTranslation"]["translations"]
        de_translation = next((t for t in translations if t["language"] == "de"), None)
        assert de_translation["reviewStatus"] == "REJECTED"
        
        print("✓ German translation rejected")

    @pytest.mark.asyncio
    async def test_20_view_key_history(self):
        """Step 20: View key change history."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            query KeyLogs($keyId: String!) {
                keyLogs(keyId: $keyId) {
                    id
                    action
                    fieldName
                    oldValue
                    newValue
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "keyId": TestCompleteUserFlow.key_id
        })
        
        assert result.errors is None, f"Get key logs failed: {result.errors}"
        assert len(result.data["keyLogs"]) >= 1
        
        print(f"✓ Key history retrieved: {len(result.data['keyLogs'])} entries")

    # =========================================================================
    # PHASE 5: AI Features
    # =========================================================================

    @pytest.mark.asyncio
    async def test_21_ai_translate(self):
        """Step 21: Use AI translation."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation AITranslate($input: TranslateInput!) {
                aiTranslate(input: $input) {
                    text
                    success
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "text": "Welcome to our platform",
                "targetLanguage": "French",
                "sourceLanguage": "English"
            }
        })
        
        assert result.errors is None, f"AI translate failed: {result.errors}"
        assert result.data["aiTranslate"]["success"] is True
        assert len(result.data["aiTranslate"]["text"]) > 0
        
        print(f"✓ AI translated: '{result.data['aiTranslate']['text']}'")

    @pytest.mark.asyncio
    async def test_22_ai_suggest_variants(self):
        """Step 22: Get AI variant suggestions."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation AISuggestVariants($input: SuggestVariantsInput!) {
                aiSuggestVariants(input: $input) {
                    variants
                    success
                }
            }
        """
        
        result = await self.client.execute_async(query, {
            "input": {
                "text": "Submit",
                "language": "English",
                "count": 3
            }
        })
        
        assert result.errors is None, f"AI suggest variants failed: {result.errors}"
        assert result.data["aiSuggestVariants"]["success"] is True
        assert len(result.data["aiSuggestVariants"]["variants"]) >= 1
        
        print(f"✓ AI suggested {len(result.data['aiSuggestVariants']['variants'])} variants")

    # =========================================================================
    # PHASE 6: Cleanup
    # =========================================================================

    @pytest.mark.asyncio
    async def test_23_delete_key(self):
        """Step 23: Delete the translation key."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation DeleteKey($id: String!) {
                deleteKey(id: $id)
            }
        """
        
        result = await self.client.execute_async(query, {
            "id": TestCompleteUserFlow.key_id
        })
        
        assert result.errors is None, f"Delete key failed: {result.errors}"
        assert result.data["deleteKey"] is True
        
        print("✓ Key deleted")

    @pytest.mark.asyncio
    async def test_24_delete_project(self):
        """Step 24: Delete the project."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation DeleteProject($id: String!) {
                deleteProject(id: $id)
            }
        """
        
        result = await self.client.execute_async(query, {
            "id": TestCompleteUserFlow.project_id
        })
        
        assert result.errors is None, f"Delete project failed: {result.errors}"
        assert result.data["deleteProject"] is True
        
        print("✓ Project deleted")

    @pytest.mark.asyncio
    async def test_25_delete_team(self):
        """Step 25: Delete the team."""
        self.client.set_token(TestCompleteUserFlow.user_token)
        
        query = """
            mutation DeleteTeam($id: String!) {
                deleteTeam(id: $id)
            }
        """
        
        result = await self.client.execute_async(query, {
            "id": TestCompleteUserFlow.team_id
        })
        
        assert result.errors is None, f"Delete team failed: {result.errors}"
        assert result.data["deleteTeam"] is True
        
        print("✓ Team deleted")
        print("\n🎉 Complete E2E flow test finished successfully!")

