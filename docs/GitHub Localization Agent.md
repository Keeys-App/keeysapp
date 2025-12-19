# GitHub Localization Agent

> [!info] Feature Overview
> AI-powered agent that connects to GitHub repositories, finds hardcoded strings, and automatically creates localization PRs.

## 🎯 Vision

Transform any codebase into a properly localized application by:
1. **Connecting** to GitHub repositories via OAuth
2. **Scanning** code for hardcoded strings using AST analysis
3. **Generating** meaningful translation keys automatically
4. **Transforming** code to use i18n functions
5. **Creating** Pull Requests with all changes
6. **Enhancing** context with screenshots for better translations

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        KEEYS PLATFORM                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐   │
│  │   GitHub     │───▶│  Code Analysis   │───▶│  Key Generator  │   │
│  │  Connector   │    │     Agent        │    │   + i18n Setup  │   │
│  └──────────────┘    └──────────────────┘    └─────────────────┘   │
│         │                    │                        │             │
│         ▼                    ▼                        ▼             │
│  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐   │
│  │ Repository   │    │   Screenshot     │    │   Translation   │   │
│  │   Browser    │    │    Analyzer      │    │    + Review     │   │
│  └──────────────┘    └──────────────────┘    └─────────────────┘   │
│         │                    │                        │             │
│         └────────────────────┴────────────────────────┘             │
│                              │                                       │
│                              ▼                                       │
│                    ┌──────────────────┐                             │
│                    │   PR Generator   │                             │
│                    │  + Code Commits  │                             │
│                    └──────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND SERVICES                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    GitHub Service                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │ OAuth Flow   │  │ API Client   │  │ Webhook Handler  │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  Localization Agent                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │ Code Scanner │  │ Transformer  │  │ PR Generator     │  │    │
│  │  │ (tree-sitter)│  │ (AST rewrite)│  │ (Git operations) │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │ Key Generator│  │ Context AI   │  │ Vision Analyzer  │  │    │
│  │  │ (GPT-4)      │  │ (GPT-4)      │  │ (GPT-4 Vision)   │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   Background Tasks                           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │ Scan Queue   │  │ Transform Q  │  │ Webhook Queue    │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 📊 Database Schema

### New Models

#### GitHubConnection
Stores OAuth tokens for GitHub access.

```python
class GitHubConnection(Base):
    __tablename__ = "github_connections"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # OAuth tokens (encrypted)
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=True)
    token_expires_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # GitHub user info
    github_user_id: Mapped[str] = mapped_column(nullable=False)
    github_username: Mapped[str] = mapped_column(nullable=False)
    github_avatar_url: Mapped[str] = mapped_column(nullable=True)
    
    # Metadata
    scopes: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    connected_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    last_used_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="github_connections")
    repositories: Mapped[List["Repository"]] = relationship(back_populates="connection")
```

#### Repository
Connected GitHub repository linked to a Keeys project.

```python
class Repository(Base):
    __tablename__ = "repositories"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    github_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey("github_connections.id"), nullable=False
    )
    
    # Repository info
    repo_owner: Mapped[str] = mapped_column(nullable=False)
    repo_name: Mapped[str] = mapped_column(nullable=False)
    repo_full_name: Mapped[str] = mapped_column(nullable=False)  # "owner/repo"
    default_branch: Mapped[str] = mapped_column(default="main")
    repo_url: Mapped[str] = mapped_column(nullable=False)
    
    # i18n configuration
    i18n_framework: Mapped[str] = mapped_column(nullable=True)  # auto-detected or manual
    translation_files_path: Mapped[str] = mapped_column(default="src/locales")
    source_patterns: Mapped[List[str]] = mapped_column(
        ARRAY(String), 
        default=["src/**/*.tsx", "src/**/*.ts", "src/**/*.jsx", "src/**/*.js"]
    )
    
    # Scan settings
    ignore_patterns: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        default=["node_modules/**", "dist/**", "*.test.*", "*.spec.*"]
    )
    auto_scan_enabled: Mapped[bool] = mapped_column(default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    last_scan_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="repositories")
    connection: Mapped["GitHubConnection"] = relationship(back_populates="repositories")
    scans: Mapped[List["ScanSession"]] = relationship(back_populates="repository")
```

#### ScanSession
Track scanning sessions and their results.

```python
class ScanStatus(str, Enum):
    PENDING = "PENDING"
    SCANNING = "SCANNING"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ScanSession(Base):
    __tablename__ = "scan_sessions"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    repository_id: Mapped[UUID] = mapped_column(ForeignKey("repositories.id"), nullable=False)
    
    # Scan info
    status: Mapped[ScanStatus] = mapped_column(default=ScanStatus.PENDING)
    branch: Mapped[str] = mapped_column(nullable=False)
    commit_sha: Mapped[str] = mapped_column(nullable=True)
    
    # Results
    files_scanned: Mapped[int] = mapped_column(default=0)
    strings_found: Mapped[int] = mapped_column(default=0)
    strings_skipped: Mapped[int] = mapped_column(default=0)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Error tracking
    error_message: Mapped[str] = mapped_column(nullable=True)
    
    # Relationships
    repository: Mapped["Repository"] = relationship(back_populates="scans")
    found_strings: Mapped[List["FoundString"]] = relationship(back_populates="scan")
```

#### FoundString
Individual hardcoded string found during scanning.

```python
class StringStatus(str, Enum):
    PENDING = "PENDING"      # Awaiting review
    APPROVED = "APPROVED"    # Will be included in PR
    SKIPPED = "SKIPPED"      # Manually skipped
    EXCLUDED = "EXCLUDED"    # Auto-excluded (version, URL, etc.)
    COMMITTED = "COMMITTED"  # Already in a PR

class FoundString(Base):
    __tablename__ = "found_strings"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    scan_id: Mapped[UUID] = mapped_column(ForeignKey("scan_sessions.id"), nullable=False)
    
    # Location
    file_path: Mapped[str] = mapped_column(nullable=False)
    line_number: Mapped[int] = mapped_column(nullable=False)
    column_start: Mapped[int] = mapped_column(nullable=False)
    column_end: Mapped[int] = mapped_column(nullable=False)
    
    # Content
    original_text: Mapped[str] = mapped_column(nullable=False)
    context_before: Mapped[str] = mapped_column(nullable=True)  # 2-3 lines before
    context_after: Mapped[str] = mapped_column(nullable=True)   # 2-3 lines after
    
    # Analysis
    string_type: Mapped[str] = mapped_column(nullable=True)  # button, label, error, etc.
    component_name: Mapped[str] = mapped_column(nullable=True)
    suggested_key: Mapped[str] = mapped_column(nullable=True)
    ai_context: Mapped[str] = mapped_column(nullable=True)  # AI-generated context
    
    # Status
    status: Mapped[StringStatus] = mapped_column(default=StringStatus.PENDING)
    final_key: Mapped[str] = mapped_column(nullable=True)  # User-approved key name
    
    # Relationships
    scan: Mapped["ScanSession"] = relationship(back_populates="found_strings")
    screenshots: Mapped[List["Screenshot"]] = relationship(back_populates="found_string")
```

#### Screenshot
Screenshots uploaded for context enhancement.

```python
class Screenshot(Base):
    __tablename__ = "screenshots"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    repository_id: Mapped[UUID] = mapped_column(ForeignKey("repositories.id"), nullable=False)
    found_string_id: Mapped[UUID] = mapped_column(
        ForeignKey("found_strings.id"), nullable=True
    )
    
    # File info
    filename: Mapped[str] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)  # Storage path
    file_size: Mapped[int] = mapped_column(nullable=False)
    mime_type: Mapped[str] = mapped_column(nullable=False)
    
    # AI analysis
    ai_description: Mapped[str] = mapped_column(nullable=True)
    detected_ui_elements: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Metadata
    uploaded_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    uploaded_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    repository: Mapped["Repository"] = relationship()
    found_string: Mapped["FoundString"] = relationship(back_populates="screenshots")
```

#### PullRequest
Track created PRs.

```python
class PRStatus(str, Enum):
    CREATING = "CREATING"
    OPEN = "OPEN"
    MERGED = "MERGED"
    CLOSED = "CLOSED"

class PullRequest(Base):
    __tablename__ = "pull_requests"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    repository_id: Mapped[UUID] = mapped_column(ForeignKey("repositories.id"), nullable=False)
    
    # GitHub info
    github_pr_id: Mapped[int] = mapped_column(nullable=True)
    github_pr_number: Mapped[int] = mapped_column(nullable=True)
    github_pr_url: Mapped[str] = mapped_column(nullable=True)
    
    # Branch info
    source_branch: Mapped[str] = mapped_column(nullable=False)
    target_branch: Mapped[str] = mapped_column(nullable=False)
    
    # Content
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    
    # Stats
    files_changed: Mapped[int] = mapped_column(default=0)
    keys_added: Mapped[int] = mapped_column(default=0)
    
    # Status
    status: Mapped[PRStatus] = mapped_column(default=PRStatus.CREATING)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    merged_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Relationships
    repository: Mapped["Repository"] = relationship()
    included_strings: Mapped[List["FoundString"]] = relationship()
```

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Project     │       │      Team       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │       │ id              │
│ email           │──────▶│ name            │◀──────│ name            │
│ ...             │       │ team_id         │       │ ...             │
└────────┬────────┘       └────────┬────────┘       └─────────────────┘
         │                         │
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│ GitHubConnection│       │   Repository    │
├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │
│ user_id         │──────▶│ project_id      │
│ access_token    │       │ github_conn_id  │◀──────┐
│ github_username │       │ repo_full_name  │       │
└─────────────────┘       │ i18n_framework  │       │
                          └────────┬────────┘       │
                                   │                │
         ┌─────────────────────────┼────────────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   ScanSession   │       │   Screenshot    │       │   PullRequest   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │       │ id              │
│ repository_id   │       │ repository_id   │       │ repository_id   │
│ status          │       │ found_string_id │       │ github_pr_id    │
│ strings_found   │       │ ai_description  │       │ status          │
└────────┬────────┘       └─────────────────┘       └─────────────────┘
         │                         ▲
         │                         │
         ▼                         │
┌─────────────────┐                │
│   FoundString   │────────────────┘
├─────────────────┤
│ id              │
│ scan_id         │
│ original_text   │
│ suggested_key   │
│ status          │
└─────────────────┘
```

## 🔐 GitHub OAuth Flow

### Setup Requirements

1. **GitHub OAuth App** (Settings → Developer settings → OAuth Apps)
   - Application name: `Keeys Localization`
   - Homepage URL: `https://keeys.app` (or ngrok URL for dev)
   - Authorization callback URL: `https://keeys.app/api/github/callback`

2. **Environment Variables**
   ```env
   # GitHub OAuth
   GITHUB_CLIENT_ID=Iv1.xxxxxxxxxxxx
   GITHUB_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxx
   GITHUB_CALLBACK_URL=https://your-ngrok-url.ngrok.io/api/github/callback
   
   # Token encryption
   GITHUB_TOKEN_ENCRYPTION_KEY=your-32-byte-key-here
   ```

### OAuth Flow Diagram

```
┌──────────┐          ┌──────────┐          ┌──────────┐
│  User    │          │  Keeys   │          │  GitHub  │
│ Browser  │          │ Backend  │          │   API    │
└────┬─────┘          └────┬─────┘          └────┬─────┘
     │                     │                     │
     │  1. Click "Connect  │                     │
     │     GitHub"         │                     │
     │────────────────────▶│                     │
     │                     │                     │
     │  2. Redirect to     │                     │
     │     GitHub OAuth    │                     │
     │◀────────────────────│                     │
     │                     │                     │
     │  3. Authorize App   │                     │
     │─────────────────────────────────────────▶│
     │                     │                     │
     │  4. Redirect with   │                     │
     │     code            │                     │
     │◀────────────────────────────────────────│
     │                     │                     │
     │  5. Send code to    │                     │
     │     backend         │                     │
     │────────────────────▶│                     │
     │                     │                     │
     │                     │  6. Exchange code   │
     │                     │     for tokens      │
     │                     │────────────────────▶│
     │                     │                     │
     │                     │  7. Return tokens   │
     │                     │◀────────────────────│
     │                     │                     │
     │                     │  8. Store encrypted │
     │                     │     tokens in DB    │
     │                     │                     │
     │  9. Success!        │                     │
     │◀────────────────────│                     │
     │                     │                     │
```

### Required Scopes

```python
GITHUB_SCOPES = [
    "repo",           # Full control of private repositories
    "read:user",      # Read user profile data
    "user:email",     # Access user email addresses
]
```

## 🔍 Code Scanner

### Supported Languages & Frameworks

| Language | Parser | i18n Frameworks |
|----------|--------|-----------------|
| TypeScript/TSX | tree-sitter-typescript | react-i18next, next-intl |
| JavaScript/JSX | tree-sitter-javascript | react-i18next, i18next |
| Vue | tree-sitter-vue | vue-i18n |
| Svelte | tree-sitter-svelte | svelte-i18n |
| Python | tree-sitter-python | gettext, babel |

### String Detection Rules

#### What to Extract

```typescript
// ✅ JSX text content
<button>Submit</button>

// ✅ String literals in JSX attributes
<input placeholder="Enter your email" />
<img alt="User avatar" />
<button title="Click to submit" />
<span aria-label="Close dialog" />

// ✅ Template literals with static content
const message = `Welcome to our app`;

// ✅ String arguments to certain functions
console.log("User logged in");  // Configurable
alert("Are you sure?");
confirm("Delete this item?");

// ✅ Object properties (configurable)
const errors = {
  required: "This field is required",
  invalid: "Invalid email format"
};
```

#### What to Skip

```typescript
// ❌ Import/export paths
import { Button } from "./Button";

// ❌ CSS class names
<div className="container flex items-center" />

// ❌ Technical identifiers
const API_ENDPOINT = "https://api.example.com";
const eventName = "user_logged_in";

// ❌ Regex patterns
const pattern = /^[a-z]+$/;

// ❌ Version strings
const version = "1.2.3";

// ❌ Already localized strings
<span>{t('common.submit')}</span>

// ❌ Console.log in development (configurable)
console.log("Debug:", value);

// ❌ Test files
describe("Button component", () => {});
```

### AST Analysis Example

```typescript
// Input code
function LoginForm() {
  return (
    <form>
      <h1>Welcome Back</h1>
      <input placeholder="Email address" />
      <input placeholder="Password" type="password" />
      <button type="submit">Sign In</button>
      <a href="/forgot">Forgot password?</a>
    </form>
  );
}

// Scanner output
[
  {
    "text": "Welcome Back",
    "type": "jsx_text",
    "file": "src/components/LoginForm.tsx",
    "line": 4,
    "component": "LoginForm",
    "suggested_key": "auth.login.title"
  },
  {
    "text": "Email address",
    "type": "jsx_attribute",
    "attribute": "placeholder",
    "file": "src/components/LoginForm.tsx",
    "line": 5,
    "component": "LoginForm",
    "suggested_key": "auth.login.emailPlaceholder"
  },
  // ... etc
]
```

## 🤖 AI Key Generator

### Key Naming Strategy

The AI generates meaningful, hierarchical key names based on:

1. **Component context** - Where the string appears
2. **Element type** - Button, label, error, etc.
3. **Semantic meaning** - What the string represents
4. **Project conventions** - Existing key patterns

### Prompt Template

```python
KEY_GENERATION_PROMPT = """
You are a localization expert. Generate a meaningful i18n key name for the following string.

Context:
- File: {file_path}
- Component: {component_name}
- Element type: {element_type} (e.g., button, label, placeholder, error)
- Surrounding code:
```
{context_code}
```

String to localize: "{original_text}"

Existing keys in project (for reference):
{existing_keys_sample}

Requirements:
1. Use dot notation: namespace.component.element
2. Use camelCase for each segment
3. Be descriptive but concise
4. Follow existing project conventions if present
5. Common namespaces: common, auth, errors, validation, nav, etc.

Return ONLY the key name, nothing else.
"""
```

### Key Deduplication

```python
class KeyDeduplicator:
    """Ensures unique keys and handles duplicates."""
    
    def process(self, found_strings: List[FoundString]) -> List[FoundString]:
        # Group by original text
        text_groups = defaultdict(list)
        for fs in found_strings:
            text_groups[fs.original_text].append(fs)
        
        # For identical texts, use same key
        for text, strings in text_groups.items():
            if len(strings) > 1:
                # Use first suggested key for all
                canonical_key = strings[0].suggested_key
                for s in strings:
                    s.final_key = canonical_key
        
        return found_strings
```

## 🔄 Code Transformer

### Transformation Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSFORMATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Parse File                                                  │
│     └─▶ Generate AST from source file                          │
│                                                                  │
│  2. Identify Replacements                                       │
│     └─▶ Map found strings to AST nodes                         │
│                                                                  │
│  3. Check Imports                                               │
│     └─▶ Detect if useTranslation/t is imported                 │
│                                                                  │
│  4. Add Hook (if needed)                                        │
│     └─▶ Add const { t } = useTranslation()                     │
│                                                                  │
│  5. Replace Strings                                             │
│     ├─▶ JSX text: "Hello" → {t('key')}                         │
│     ├─▶ Attributes: placeholder="x" → placeholder={t('key')}   │
│     └─▶ Variables: const x = "y" → const x = t('key')          │
│                                                                  │
│  6. Add Import (if needed)                                      │
│     └─▶ import { useTranslation } from 'react-i18next'         │
│                                                                  │
│  7. Generate Output                                             │
│     └─▶ Serialize AST back to code                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Before & After Example

**Before:**
```tsx
import { useState } from 'react';

export function ContactForm() {
  const [error, setError] = useState('');
  
  return (
    <form>
      <h2>Contact Us</h2>
      <input placeholder="Your name" />
      <input placeholder="Your email" />
      <textarea placeholder="Your message" />
      <button type="submit">Send Message</button>
      {error && <span className="error">{error}</span>}
    </form>
  );
}
```

**After:**
```tsx
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export function ContactForm() {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  
  return (
    <form>
      <h2>{t('contact.title')}</h2>
      <input placeholder={t('contact.namePlaceholder')} />
      <input placeholder={t('contact.emailPlaceholder')} />
      <textarea placeholder={t('contact.messagePlaceholder')} />
      <button type="submit">{t('contact.submitButton')}</button>
      {error && <span className="error">{error}</span>}
    </form>
  );
}
```

### Translation File Generation

**en.json:**
```json
{
  "contact": {
    "title": "Contact Us",
    "namePlaceholder": "Your name",
    "emailPlaceholder": "Your email", 
    "messagePlaceholder": "Your message",
    "submitButton": "Send Message"
  }
}
```

## 📸 Screenshot Enhancement

### Vision AI Analysis

Screenshots provide visual context for better translations.

```python
SCREENSHOT_ANALYSIS_PROMPT = """
Analyze this UI screenshot to provide context for localization.

Identify:
1. What type of screen/page is this? (login, settings, dashboard, etc.)
2. What UI elements contain text?
3. What is the purpose/action of each text element?
4. Any specific tone or style? (formal, casual, technical)
5. Target audience hints?

Provide a structured analysis that will help translators understand the context.
"""
```

### Context Enhancement Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Screenshot    │────▶│   GPT-4 Vision  │────▶│ Enhanced Context│
│   Upload        │     │   Analysis      │     │ for Translation │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                              │
         │                                              ▼
         │                                   ┌─────────────────┐
         │                                   │ Better Key Names│
         │                                   │ Better Translations│
         └──────────────────────────────────▶│ Contextual Notes │
                                             └─────────────────┘
```

## 📝 PR Generation

### Branch & Commit Strategy

```
main
  │
  └── feat/i18n-auth-module
        │
        ├── 🔧 chore: add i18n setup and configuration
        │     - Add react-i18next dependency
        │     - Create i18n configuration file
        │     - Add translation file structure
        │
        ├── 🌐 feat: localize LoginForm component
        │     - Extract 5 strings to translation keys
        │     - Add useTranslation hook
        │
        ├── 🌐 feat: localize RegisterForm component
        │     - Extract 8 strings to translation keys
        │     - Add useTranslation hook
        │
        └── 📝 docs: add localization notes
              - Document new translation keys
              - Add context for translators
```

### PR Description Template

```markdown
## 🌐 Localization: {module_name}

This PR adds internationalization support to the {module_name} module.

### Changes Summary

- **Files modified:** {files_count}
- **Strings localized:** {strings_count}
- **New translation keys:** {keys_count}

### Modified Files

| File | Strings | Keys Added |
|------|---------|------------|
| `src/components/LoginForm.tsx` | 5 | 5 |
| `src/components/RegisterForm.tsx` | 8 | 8 |

### New Translation Keys

<details>
<summary>View all {keys_count} keys</summary>

| Key | Default (EN) |
|-----|--------------|
| `auth.login.title` | Welcome Back |
| `auth.login.emailPlaceholder` | Email address |
| ... | ... |

</details>

### Translation Status

| Language | Status |
|----------|--------|
| 🇺🇸 English | ✅ Complete |
| 🇷🇺 Russian | ⏳ Pending |
| 🇩🇪 German | ⏳ Pending |

### How to Review

1. Check that all user-facing strings are properly extracted
2. Verify key naming follows project conventions
3. Ensure no hardcoded strings were missed
4. Review translation file structure

---

*Generated by [Keeys Localization Agent](https://keeys.app)*
*Linked Project: [{project_name}]({project_url})*
```

## 📡 GraphQL API

### Queries

```graphql
# Get user's GitHub connections
query myGitHubConnections {
  myGitHubConnections {
    id
    githubUsername
    githubAvatarUrl
    connectedAt
    repositories {
      id
      repoFullName
    }
  }
}

# Get repository details
query repository($id: ID!) {
  repository(id: $id) {
    id
    repoFullName
    repoUrl
    defaultBranch
    i18nFramework
    translationFilesPath
    sourcePatterns
    lastScanAt
    project {
      id
      name
    }
  }
}

# Get scan results
query scanSession($id: ID!) {
  scanSession(id: $id) {
    id
    status
    branch
    commitSha
    filesScanned
    stringsFound
    startedAt
    completedAt
    foundStrings {
      id
      originalText
      filePath
      lineNumber
      stringType
      suggestedKey
      status
    }
  }
}

# Get repository PRs
query repositoryPRs($repositoryId: ID!) {
  repositoryPRs(repositoryId: $repositoryId) {
    id
    githubPrNumber
    githubPrUrl
    title
    status
    filesChanged
    keysAdded
    createdAt
  }
}
```

### Mutations

```graphql
# Start GitHub OAuth flow
mutation initiateGitHubOAuth {
  initiateGitHubOAuth {
    authorizationUrl
    state
  }
}

# Complete OAuth and store connection
mutation completeGitHubOAuth($code: String!, $state: String!) {
  completeGitHubOAuth(code: $code, state: $state) {
    connection {
      id
      githubUsername
    }
    success
    error
  }
}

# Add repository to project
mutation addRepository($input: AddRepositoryInput!) {
  addRepository(input: $input) {
    repository {
      id
      repoFullName
    }
    success
    error
  }
}

input AddRepositoryInput {
  projectId: ID!
  githubConnectionId: ID!
  repoOwner: String!
  repoName: String!
  i18nFramework: String
  translationFilesPath: String
  sourcePatterns: [String!]
}

# Start code scan
mutation startScan($repositoryId: ID!, $branch: String) {
  startScan(repositoryId: $repositoryId, branch: $branch) {
    scanSession {
      id
      status
    }
    success
    error
  }
}

# Update found string status
mutation updateFoundString($id: ID!, $input: UpdateFoundStringInput!) {
  updateFoundString(id: $id, input: $input) {
    foundString {
      id
      status
      finalKey
    }
    success
  }
}

input UpdateFoundStringInput {
  status: StringStatus
  finalKey: String
}

# Upload screenshot for context
mutation uploadScreenshot($input: UploadScreenshotInput!) {
  uploadScreenshot(input: $input) {
    screenshot {
      id
      aiDescription
    }
    success
  }
}

# Create localization PR
mutation createLocalizationPR($input: CreatePRInput!) {
  createLocalizationPR(input: $input) {
    pullRequest {
      id
      githubPrNumber
      githubPrUrl
    }
    success
    error
  }
}

input CreatePRInput {
  repositoryId: ID!
  foundStringIds: [ID!]!
  targetBranch: String
  prTitle: String
  prDescription: String
}
```

### Subscriptions (Future)

```graphql
# Real-time scan progress
subscription scanProgress($scanId: ID!) {
  scanProgress(scanId: $scanId) {
    status
    filesScanned
    stringsFound
    currentFile
    progress
  }
}
```

## 🖥️ Frontend Components

### Page Structure

```
/project/:id/github
├── GitHubIntegrationPage.tsx       # Main page
├── components/
│   ├── ConnectGitHubCard.tsx       # OAuth connection UI
│   ├── RepositoryList.tsx          # List of connected repos
│   ├── RepositoryCard.tsx          # Individual repo card
│   ├── AddRepositoryDialog.tsx     # Add new repo modal
│   ├── ScanResultsPanel.tsx        # Scan results view
│   ├── FoundStringsList.tsx        # List of found strings
│   ├── FoundStringRow.tsx          # Individual string row
│   ├── StringPreviewDialog.tsx     # Preview string in context
│   ├── ScreenshotUploader.tsx      # Screenshot upload UI
│   ├── CreatePRDialog.tsx          # PR creation modal
│   └── PRStatusCard.tsx            # PR tracking card
└── hooks/
    ├── useGitHubConnection.ts      # OAuth flow hook
    ├── useRepositories.ts          # Repository CRUD
    ├── useScanSession.ts           # Scan operations
    └── useCreatePR.ts              # PR creation
```

### UI Mockup

```
┌─────────────────────────────────────────────────────────────────────┐
│  Keeys › My Project › GitHub Integration                    [User] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  🔗 GitHub Connection                                          │ │
│  │                                                                │ │
│  │  Connected as: @username                    [Disconnect]       │ │
│  │  ──────────────────────────────────────────────────────────── │ │
│  │                                                                │ │
│  │  📁 Connected Repositories                 [+ Add Repository]  │ │
│  │                                                                │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  📦 myorg/frontend-app                                   │ │ │
│  │  │  Branch: main │ Framework: react-i18next                 │ │ │
│  │  │  Last scan: 2h ago │ 47 strings found                    │ │ │
│  │  │                                                          │ │ │
│  │  │  [🔍 Scan Now] [📊 View Results] [⚙️ Settings]           │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  🔎 Scan Results                                    [Refresh]  │ │
│  │                                                                │ │
│  │  Status: ✅ Completed │ Files: 24 │ Strings: 47               │ │
│  │                                                                │ │
│  │  ┌────┬─────────────────────┬──────────────────┬────────────┐ │ │
│  │  │ ☑️ │ String              │ Suggested Key    │ File       │ │ │
│  │  ├────┼─────────────────────┼──────────────────┼────────────┤ │ │
│  │  │ ☑️ │ "Submit"            │ common.submit    │ Button.tsx │ │ │
│  │  │ ☑️ │ "Loading..."        │ common.loading   │ Loader.tsx │ │ │
│  │  │ ☑️ │ "Welcome back!"     │ auth.welcome     │ Login.tsx  │ │ │
│  │  │ ☐  │ "v1.2.3"            │ [excluded]       │ Footer.tsx │ │ │
│  │  │ ...│ ...                 │ ...              │ ...        │ │ │
│  │  └────┴─────────────────────┴──────────────────┴────────────┘ │ │
│  │                                                                │ │
│  │  Selected: 45 strings                                         │ │
│  │                                                                │ │
│  │  [📸 Add Screenshots] [🚀 Create Pull Request]                │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  📋 Pull Requests                                              │ │
│  │                                                                │ │
│  │  #42 feat: i18n for auth module          🟢 Open    2h ago    │ │
│  │      +156 -89 │ 8 files │ 23 keys                             │ │
│  │      [View on GitHub] [Sync Translations]                     │ │
│  │                                                                │ │
│  │  #38 feat: i18n for common components    ✅ Merged  3d ago    │ │
│  │      +89 -45 │ 5 files │ 15 keys                              │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 📅 Implementation Phases

### Phase 1: GitHub Integration Foundation (Week 1-2)

**Backend:**
- [ ] Create `GitHubConnection` model
- [ ] Create `Repository` model
- [ ] Implement GitHub OAuth service
- [ ] Add OAuth routes (`/api/github/auth`, `/api/github/callback`)
- [ ] Implement token encryption/decryption
- [ ] Add GraphQL queries/mutations for connections
- [ ] Write unit tests

**Frontend:**
- [ ] Create GitHub integration page
- [ ] Implement OAuth flow UI
- [ ] Create `ConnectGitHubCard` component
- [ ] Create `AddRepositoryDialog` component
- [ ] Add repository list view

**DevOps:**
- [ ] Set up GitHub OAuth App
- [ ] Configure ngrok for local testing
- [ ] Add environment variables

### Phase 2: Code Scanner (Week 3-4)

**Backend:**
- [ ] Install tree-sitter and language grammars
- [ ] Create `ScanSession` model
- [ ] Create `FoundString` model
- [ ] Implement `CodeScanner` service
- [ ] Add string detection rules
- [ ] Implement false positive filtering
- [ ] Add background task for scanning
- [ ] Add GraphQL API for scans
- [ ] Write unit tests

**Frontend:**
- [ ] Create `ScanResultsPanel` component
- [ ] Create `FoundStringsList` component
- [ ] Add scan progress indicator
- [ ] Implement string filtering/search
- [ ] Add bulk selection UI

### Phase 3: AI Key Generator (Week 5)

**Backend:**
- [ ] Create key generation prompts
- [ ] Implement `KeyGenerator` service
- [ ] Add context extraction logic
- [ ] Implement key deduplication
- [ ] Integrate with existing AI service
- [ ] Write unit tests

**Frontend:**
- [ ] Show AI-suggested keys
- [ ] Allow key editing
- [ ] Add key validation
- [ ] Show existing keys for reference

### Phase 4: Code Transformer (Week 6-7)

**Backend:**
- [ ] Implement `CodeTransformer` service
- [ ] Add import injection logic
- [ ] Add hook injection logic
- [ ] Implement string replacement
- [ ] Generate translation files
- [ ] Add preview mode
- [ ] Write unit tests

**Frontend:**
- [ ] Create diff preview dialog
- [ ] Show before/after comparison
- [ ] Allow selective changes
- [ ] Add translation file preview

### Phase 5: PR Workflow (Week 8)

**Backend:**
- [ ] Create `PullRequest` model
- [ ] Implement `PRGenerator` service
- [ ] Add Git operations (branch, commit)
- [ ] Implement PR creation via GitHub API
- [ ] Add PR description generator
- [ ] Set up webhook handling
- [ ] Write unit tests

**Frontend:**
- [ ] Create `CreatePRDialog` component
- [ ] Add PR configuration options
- [ ] Create `PRStatusCard` component
- [ ] Add PR sync functionality

### Phase 6: Screenshot Enhancement (Week 9)

**Backend:**
- [ ] Create `Screenshot` model
- [ ] Implement file upload handling
- [ ] Add GPT-4 Vision integration
- [ ] Implement context enhancement
- [ ] Write unit tests

**Frontend:**
- [ ] Create `ScreenshotUploader` component
- [ ] Add drag-and-drop support
- [ ] Show AI analysis results
- [ ] Link screenshots to strings

### Phase 7: Polish & Testing (Week 10)

- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Documentation
- [ ] User guide

## 🔧 Technical Considerations

### Security

1. **Token Storage**
   - Encrypt GitHub tokens at rest using Fernet
   - Never log tokens
   - Implement token refresh flow

2. **Repository Access**
   - Validate user has access to repository
   - Respect GitHub permissions
   - Audit log all operations

3. **Code Handling**
   - Clone to temporary directories
   - Clean up after operations
   - Never store full code in DB

### Performance

1. **Scanning**
   - Use streaming for large repos
   - Implement pagination for results
   - Cache parsed ASTs

2. **Background Jobs**
   - Use async tasks for long operations
   - Implement progress tracking
   - Add timeout handling

### Error Handling

1. **GitHub API**
   - Handle rate limiting
   - Graceful degradation
   - User-friendly error messages

2. **Parsing**
   - Handle malformed code
   - Skip unparseable files
   - Report issues clearly

## 📚 Dependencies

### Backend (Python)

```txt
# GitHub
PyGithub>=2.1.0
httpx>=0.25.0
cryptography>=41.0.0  # Token encryption

# Code Parsing
tree-sitter>=0.20.0
tree-sitter-javascript>=0.20.0
tree-sitter-typescript>=0.20.0

# Git Operations
GitPython>=3.1.0

# Background Tasks (optional)
celery>=5.3.0
redis>=5.0.0
```

### Frontend (npm)

```json
{
  "dependencies": {
    "@octokit/rest": "^20.0.0"  // Optional: client-side GitHub API
  }
}
```

## 🔗 Related Documentation

- [[AI Autopilot Feature]] - Existing AI integration
- [[Project Export Import]] - File handling patterns
- [[Authentication Setup]] - OAuth patterns
- [[Security Best Practices]] - Security guidelines

---

*Document created: 2024-12-19*
*Last updated: 2024-12-19*

