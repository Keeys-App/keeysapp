# GitHub Localization Agent

> [!info] Feature Overview
> AI-powered agent that connects to GitHub repositories, analyzes code using Claude AI, finds hardcoded strings, transforms code to use i18n, and automatically creates Pull Requests.

## 🎯 Vision

### The Problem

Developers often write code with hardcoded strings:

```tsx
<button>Submit</button>
<h1>Welcome Back</h1>
<input placeholder="Enter your email" />
```

Internationalizing an existing codebase is tedious, error-prone, and time-consuming. Developers must:
1. Manually find all user-facing strings
2. Create meaningful key names
3. Replace strings with i18n function calls
4. Create translation files
5. Ensure nothing breaks

### The Solution

**Keeys GitHub Agent** automates the entire process:

1. **Connect** your GitHub repository
2. **Scan** — Claude AI analyzes your code and finds all strings
3. **Review** — You approve/edit suggested keys
4. **Transform** — Claude rewrites code with i18n
5. **PR** — Agent creates a Pull Request with all changes

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   GitHub    │ ───▶ │  Claude AI  │ ───▶ │   Review    │ ───▶ │  Pull       │
│   Repo      │      │  Analysis   │      │   & Edit    │      │  Request    │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
```

## 🏗️ Architecture

### Core Principle: Claude Does Everything

Instead of building complex parsers for each language/framework, we leverage Claude's ability to understand and transform code. This gives us:

| Benefit | Description |
|---------|-------------|
| **Universal** | Works with any language: React, Vue, Svelte, Angular, Python, etc. |
| **Context-Aware** | Understands what's user-facing vs technical |
| **High Quality** | Produces idiomatic, clean code |
| **Simple Backend** | Minimal code to maintain |

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KEEYS PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         GitHub Integration Layer                        │ │
│  │                                                                         │ │
│  │   ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐  │ │
│  │   │    OAuth     │   │  Repository  │   │     Webhook Handler      │  │ │
│  │   │    Flow      │   │   Browser    │   │   (PR status updates)    │  │ │
│  │   └──────────────┘   └──────────────┘   └──────────────────────────┘  │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         Claude AI Agent                                 │ │
│  │                                                                         │ │
│  │   ┌──────────────────────────────────────────────────────────────────┐ │ │
│  │   │                     Single Powerful Prompt                        │ │ │
│  │   │                                                                   │ │ │
│  │   │  INPUT:  Source code file                                        │ │ │
│  │   │  OUTPUT: • Transformed code with i18n                            │ │ │
│  │   │          • List of found strings with keys                       │ │ │
│  │   │          • Translation file entries                              │ │ │
│  │   │          • Change summary                                        │ │ │
│  │   │                                                                   │ │ │
│  │   └──────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         Review & Approval UI                            │ │
│  │                                                                         │ │
│  │   • View found strings                    • Upload screenshots         │ │
│  │   • Edit suggested keys                   • Add context for Claude     │ │
│  │   • Approve/skip strings                  • Preview changes            │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         PR Generation                                   │ │
│  │                                                                         │ │
│  │   • Create feature branch                 • Commit transformed files   │ │
│  │   • Generate PR description               • Link to Keeys project      │ │
│  │   • Update translation files              • Track PR status            │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WORKFLOW                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEP 1: CONNECT                                                            │
│  ════════════════                                                           │
│  User connects GitHub account via OAuth                                     │
│  User selects repository to analyze                                         │
│  User configures i18n framework (react-i18next, vue-i18n, etc.)            │
│                                                                              │
│                                    ▼                                         │
│                                                                              │
│  STEP 2: SCAN                                                               │
│  ════════════                                                               │
│  Agent fetches file list from repository                                    │
│  Agent filters files by pattern (*.tsx, *.vue, etc.)                        │
│  For each file:                                                             │
│    → Send to Claude for analysis                                            │
│    → Claude returns: found strings + suggested keys + transformed code     │
│    → Store results in database                                              │
│                                                                              │
│                                    ▼                                         │
│                                                                              │
│  STEP 3: REVIEW                                                             │
│  ══════════════                                                             │
│  User sees list of all found strings                                        │
│  User can:                                                                  │
│    → Approve strings (include in PR)                                        │
│    → Skip strings (exclude from PR)                                         │
│    → Edit key names                                                         │
│    → Upload screenshots for better context                                  │
│    → Request re-analysis with more context                                  │
│                                                                              │
│                                    ▼                                         │
│                                                                              │
│  STEP 4: TRANSFORM                                                          │
│  ═════════════════                                                          │
│  For approved strings:                                                      │
│    → Claude generates final transformed code                                │
│    → Generate translation file entries                                      │
│    → Preview diff before commit                                             │
│                                                                              │
│                                    ▼                                         │
│                                                                              │
│  STEP 5: CREATE PR                                                          │
│  ═════════════════                                                          │
│  Create feature branch (e.g., feat/i18n-auth-module)                        │
│  Commit all transformed files                                               │
│  Commit translation files (en.json, etc.)                                   │
│  Create PR with auto-generated description                                  │
│  Link PR to Keeys project for translation tracking                          │
│                                                                              │
│                                    ▼                                         │
│                                                                              │
│  STEP 6: TRANSLATE & MERGE                                                  │
│  ═════════════════════════                                                  │
│  Translations sync to Keeys project                                         │
│  Team translates keys in Keeys UI                                           │
│  When ready, translations push back to PR                                   │
│  Developer merges PR                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🤖 Claude AI Agent

### Why Claude?

| Feature | Benefit |
|---------|---------|
| **Code Understanding** | Claude excels at reading and writing code |
| **Context Window** | 200K tokens — can process large files |
| **Instruction Following** | Reliably outputs structured JSON |
| **Multi-language** | Understands React, Vue, Angular, Python, etc. |
| **Quality** | Produces clean, idiomatic code |

### What Claude Does

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLAUDE'S RESPONSIBILITIES                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📥 INPUT                                                        │
│  ──────                                                         │
│  • Source code file                                             │
│  • i18n framework configuration                                 │
│  • Optional: screenshots for UI context                         │
│  • Optional: existing keys from project                         │
│                                                                  │
│                          ▼                                       │
│                                                                  │
│  🧠 ANALYSIS                                                     │
│  ──────────                                                     │
│  • Parse code structure                                         │
│  • Identify user-facing strings                                 │
│  • Distinguish from technical strings (URLs, classes, IDs)      │
│  • Understand component context                                 │
│  • Generate semantic key names                                  │
│                                                                  │
│                          ▼                                       │
│                                                                  │
│  📤 OUTPUT                                                       │
│  ────────                                                       │
│  • Transformed source code                                      │
│  • List of found strings with metadata                          │
│  • Translation file entries                                     │
│  • Summary of changes                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### String Classification

Claude automatically classifies strings:

| Category | Examples | Action |
|----------|----------|--------|
| **UI Text** | "Submit", "Welcome Back" | ✅ Localize |
| **Placeholders** | "Enter your email" | ✅ Localize |
| **Error Messages** | "Invalid password" | ✅ Localize |
| **Tooltips** | "Click to save" | ✅ Localize |
| **URLs** | "https://api.com" | ❌ Skip |
| **CSS Classes** | "flex items-center" | ❌ Skip |
| **Technical IDs** | "user-avatar-img" | ❌ Skip |
| **Console Logs** | "Debug: value=" | ❌ Skip |
| **Already i18n** | "t('key')" | ❌ Skip |

### Key Generation Strategy

Claude generates keys following best practices:

```
namespace.component.element

Examples:
─────────
auth.login.title           → "Welcome Back"
auth.login.submitButton    → "Sign In"
auth.login.emailPlaceholder → "Enter your email"
common.buttons.save        → "Save"
common.buttons.cancel      → "Cancel"
errors.validation.required → "This field is required"
```

## 📸 Screenshot Enhancement

Screenshots provide visual context for better analysis.

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCREENSHOT ENHANCEMENT                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. User uploads screenshot of the UI                           │
│                                                                  │
│     ┌─────────────────────────────────────────┐                 │
│     │  ┌─────────────────────────────────┐    │                 │
│     │  │        Welcome Back             │    │                 │
│     │  │  ┌───────────────────────────┐  │    │                 │
│     │  │  │ Email address             │  │    │                 │
│     │  │  └───────────────────────────┘  │    │                 │
│     │  │  ┌───────────────────────────┐  │    │                 │
│     │  │  │ ●●●●●●●●                  │  │    │                 │
│     │  │  └───────────────────────────┘  │    │                 │
│     │  │  ┌───────────────────────────┐  │    │                 │
│     │  │  │        Sign In            │  │    │                 │
│     │  │  └───────────────────────────┘  │    │                 │
│     │  └─────────────────────────────────┘    │                 │
│     └─────────────────────────────────────────┘                 │
│                                                                  │
│  2. Claude Vision analyzes the screenshot                       │
│     → Identifies UI components                                  │
│     → Understands context (login form)                          │
│     → Maps strings to visual elements                           │
│                                                                  │
│  3. Better key names and context                                │
│     → "Welcome Back" clearly a page title                       │
│     → "Sign In" is a primary action button                      │
│     → Better translation hints for translators                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Benefits

- **Better Key Names** — Visual context helps generate meaningful keys
- **Translation Context** — Translators see where text appears
- **Fewer Errors** — Less ambiguity about string purpose

## 🔐 GitHub Integration

### OAuth Flow

```
┌──────────┐          ┌──────────┐          ┌──────────┐
│   User   │          │  Keeys   │          │  GitHub  │
│ Browser  │          │ Backend  │          │   API    │
└────┬─────┘          └────┬─────┘          └────┬─────┘
     │                     │                     │
     │ 1. Click "Connect"  │                     │
     │────────────────────▶│                     │
     │                     │                     │
     │ 2. Redirect to      │                     │
     │    GitHub           │                     │
     │◀────────────────────│                     │
     │                     │                     │
     │ 3. Authorize        │                     │
     │─────────────────────────────────────────▶│
     │                     │                     │
     │ 4. Callback with    │                     │
     │    code             │                     │
     │◀────────────────────────────────────────│
     │                     │                     │
     │ 5. Exchange code    │                     │
     │────────────────────▶│                     │
     │                     │ 6. Get tokens       │
     │                     │────────────────────▶│
     │                     │                     │
     │                     │ 7. Access token     │
     │                     │◀────────────────────│
     │                     │                     │
     │ 8. Connected!       │ 9. Store encrypted  │
     │◀────────────────────│                     │
     │                     │                     │
```

### Required Permissions

| Scope | Purpose |
|-------|---------|
| `repo` | Read/write repository content, create branches and PRs |
| `read:user` | Get user profile information |
| `user:email` | Access user email for notifications |

### Security Measures

- **Token Encryption** — OAuth tokens encrypted at rest
- **Minimal Permissions** — Only request necessary scopes
- **Audit Logging** — All operations logged
- **Token Refresh** — Automatic token refresh handling

## 📝 Pull Request Generation

### Branch Strategy

```
main
  │
  └── feat/i18n-{module}-{timestamp}
        │
        ├── 📄 src/components/LoginForm.tsx
        ├── 📄 src/components/RegisterForm.tsx
        ├── 📄 src/components/Header.tsx
        └── 📄 src/locales/en.json
```

### Auto-Generated PR Description

```markdown
## 🌐 Internationalization: Auth Module

This PR adds i18n support generated by [Keeys](https://keeys.app).

### Summary
- **Files modified:** 3
- **Strings localized:** 24
- **New translation keys:** 24

### Changes by File

| File | Strings | Status |
|------|---------|--------|
| `LoginForm.tsx` | 8 | ✅ Ready |
| `RegisterForm.tsx` | 12 | ✅ Ready |
| `Header.tsx` | 4 | ✅ Ready |

### Translation Status

| Language | Progress |
|----------|----------|
| 🇺🇸 English | ✅ 24/24 (100%) |
| 🇷🇺 Russian | ⏳ 0/24 (0%) |
| 🇩🇪 German | ⏳ 0/24 (0%) |

### New Keys

<details>
<summary>View all 24 keys</summary>

| Key | English |
|-----|---------|
| `auth.login.title` | Welcome Back |
| `auth.login.subtitle` | Sign in to continue |
| ... | ... |

</details>

---
*Generated by [Keeys Localization Agent](https://keeys.app)*
```

## 💾 Database Schema

### New Entities

```
┌─────────────────────────────────────────────────────────────────┐
│                       NEW MODELS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GitHubConnection                                               │
│  ═══════════════                                                │
│  Stores OAuth tokens for GitHub access                          │
│  • user_id → links to User                                      │
│  • access_token (encrypted)                                     │
│  • github_username                                              │
│  • connected_at                                                 │
│                                                                  │
│  Repository                                                      │
│  ══════════                                                     │
│  Connected GitHub repository                                    │
│  • project_id → links to Keeys Project                          │
│  • github_connection_id                                         │
│  • repo_owner, repo_name                                        │
│  • i18n_framework (react-i18next, vue-i18n, etc.)              │
│  • source_patterns (["src/**/*.tsx"])                           │
│                                                                  │
│  ScanSession                                                     │
│  ═══════════                                                    │
│  Tracks a scanning operation                                    │
│  • repository_id                                                │
│  • status (pending, scanning, completed, failed)                │
│  • files_scanned, strings_found                                 │
│  • started_at, completed_at                                     │
│                                                                  │
│  FoundString                                                     │
│  ═══════════                                                    │
│  Individual string found during scan                            │
│  • scan_id                                                      │
│  • file_path, line_number                                       │
│  • original_text                                                │
│  • suggested_key, final_key                                     │
│  • status (pending, approved, skipped)                          │
│  • ai_context (Claude's explanation)                            │
│                                                                  │
│  Screenshot                                                      │
│  ══════════                                                     │
│  Uploaded UI screenshots                                        │
│  • repository_id                                                │
│  • file_path (storage)                                          │
│  • ai_description (Claude Vision analysis)                      │
│                                                                  │
│  PullRequest                                                     │
│  ═══════════                                                    │
│  Created GitHub PRs                                             │
│  • repository_id                                                │
│  • github_pr_number, github_pr_url                              │
│  • status (creating, open, merged, closed)                      │
│  • source_branch, target_branch                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Entity Relationships

```
User
  │
  ├──▶ GitHubConnection (1:many)
  │         │
  │         └──▶ Repository (1:many)
  │                   │
  │                   ├──▶ ScanSession (1:many)
  │                   │         │
  │                   │         └──▶ FoundString (1:many)
  │                   │
  │                   ├──▶ Screenshot (1:many)
  │                   │
  │                   └──▶ PullRequest (1:many)
  │
  └──▶ Project
            │
            └──▶ Repository (1:many, same as above)
```

## 🖥️ User Interface

### Main Screen

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Keeys › My Project › GitHub Agent                              [User] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  🔗 GitHub Connection                                               ││
│  │                                                                     ││
│  │  ✅ Connected as @username                         [Disconnect]    ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  📁 Repositories                              [+ Add Repository]   ││
│  │                                                                     ││
│  │  ┌─────────────────────────────────────────────────────────────┐   ││
│  │  │  📦 myorg/frontend-app                                      │   ││
│  │  │  Branch: main │ Framework: react-i18next │ Last: 2h ago     │   ││
│  │  │                                                             │   ││
│  │  │  ┌──────────┐ ┌──────────────┐ ┌──────────┐               │   ││
│  │  │  │ 🔍 Scan  │ │ 📊 Results   │ │ ⚙️ Config │               │   ││
│  │  │  └──────────┘ └──────────────┘ └──────────┘               │   ││
│  │  └─────────────────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  🔎 Scan Results                                                    ││
│  │                                                                     ││
│  │  Found 47 strings in 12 files                    [Create PR]       ││
│  │                                                                     ││
│  │  ┌────┬─────────────────────┬──────────────────┬──────────────┐   ││
│  │  │ ✓  │ String              │ Key              │ File         │   ││
│  │  ├────┼─────────────────────┼──────────────────┼──────────────┤   ││
│  │  │ ☑️ │ "Welcome Back"      │ auth.login.title │ LoginForm    │   ││
│  │  │ ☑️ │ "Sign In"           │ auth.login.submit│ LoginForm    │   ││
│  │  │ ☑️ │ "Email address"     │ auth.login.email │ LoginForm    │   ││
│  │  │ ☐  │ "v1.2.3"           │ [skip]           │ Footer       │   ││
│  │  │ ...│ ...                 │ ...              │ ...          │   ││
│  │  └────┴─────────────────────┴──────────────────┴──────────────┘   ││
│  │                                                                     ││
│  │  [📸 Add Screenshots]   [Preview Changes]   [🚀 Create PR]        ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### String Review Dialog

```
┌─────────────────────────────────────────────────────────────────┐
│  Review String                                              [X] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Original Text                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  "Welcome Back"                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Location                                                       │
│  📄 src/components/LoginForm.tsx : line 24                      │
│                                                                  │
│  Context (from Claude)                                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Main heading of the login form. Displayed when user      │ │
│  │  navigates to the login page.                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Translation Key                                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  auth.login.title                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Screenshot (optional)                                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  [📷 Drop image or click to upload]                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐   │
│  │   Skip     │  │   Cancel   │  │   ✓ Approve & Next     │   │
│  └────────────┘  └────────────┘  └────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📅 Implementation Phases

### Phase 1: GitHub Integration (Week 1-2)

**Goal:** Connect GitHub accounts and browse repositories

**Backend:**
- Create `GitHubConnection` model
- Create `Repository` model
- Implement OAuth flow (authorize, callback, token storage)
- Implement GitHub API client (list repos, get files)
- GraphQL mutations: `connectGitHub`, `addRepository`

**Frontend:**
- GitHub connection UI
- Repository selection dialog
- Repository list component
- i18n framework configuration

**Deliverable:** Users can connect GitHub and add repositories

---

### Phase 2: Claude Agent — Scanning (Week 3-4)

**Goal:** Analyze code and find strings using Claude

**Backend:**
- Create `ScanSession` model
- Create `FoundString` model
- Implement Claude integration service
- Create scanning prompt templates
- Background task for file processing
- GraphQL: `startScan`, `getScanResults`

**Frontend:**
- Scan progress UI
- Found strings list
- String filtering and search

**Deliverable:** Users can scan repos and see found strings

---

### Phase 3: Review & Edit (Week 5)

**Goal:** Users review and approve strings for localization

**Backend:**
- Update `FoundString` with status handling
- Implement key validation
- Batch update operations
- GraphQL: `updateFoundString`, `batchUpdateStrings`

**Frontend:**
- String review dialog
- Inline key editing
- Bulk actions (approve all, skip all)
- Diff preview

**Deliverable:** Users can review and approve strings

---

### Phase 4: Screenshot Enhancement (Week 6)

**Goal:** Use screenshots to improve context

**Backend:**
- Create `Screenshot` model
- File upload handling
- Claude Vision integration
- Context enhancement logic

**Frontend:**
- Screenshot upload component
- Image preview
- AI analysis display

**Deliverable:** Users can upload screenshots for better context

---

### Phase 5: Code Transformation (Week 7-8)

**Goal:** Generate transformed code using Claude

**Backend:**
- Transformation prompt templates
- Code generation service
- Translation file generation
- File diff generation

**Frontend:**
- Transformation preview
- Side-by-side diff view
- Translation file preview

**Deliverable:** Users can preview transformed code

---

### Phase 6: PR Generation (Week 9)

**Goal:** Create Pull Requests with changes

**Backend:**
- Create `PullRequest` model
- Git operations (branch, commit)
- GitHub PR API integration
- PR description generation
- Webhook handler for PR status

**Frontend:**
- Create PR dialog
- PR configuration options
- PR status tracking
- Link to GitHub

**Deliverable:** Users can create PRs with localized code

---

### Phase 7: Integration & Polish (Week 10)

**Goal:** End-to-end testing and polish

**Tasks:**
- Integration testing
- Error handling improvements
- Performance optimization
- Documentation
- User onboarding flow

**Deliverable:** Production-ready feature

---

# 🛠️ Step-by-Step Implementation Guide

## Step 1: GitHub Account Connection

### 1.1 Overview

First, we need to allow users to connect their GitHub accounts to Keeys via OAuth 2.0.

```
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 1: CONNECT GITHUB                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User clicks "Connect GitHub"                                   │
│           │                                                      │
│           ▼                                                      │
│  Keeys redirects to GitHub OAuth                                │
│           │                                                      │
│           ▼                                                      │
│  User authorizes Keeys app                                      │
│           │                                                      │
│           ▼                                                      │
│  GitHub redirects back with code                                │
│           │                                                      │
│           ▼                                                      │
│  Keeys exchanges code for access token                          │
│           │                                                      │
│           ▼                                                      │
│  Token encrypted and stored in DB                               │
│           │                                                      │
│           ▼                                                      │
│  User sees "Connected as @username"                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Prerequisites

Before starting implementation:

1. **Create GitHub OAuth App**
   - Go to GitHub → Settings → Developer settings → OAuth Apps
   - Click "New OAuth App"
   - Fill in:
     - Application name: `Keeys Localization`
     - Homepage URL: `https://keeys.app` (or ngrok URL for dev)
     - Authorization callback URL: `{BACKEND_URL}/api/github/callback`
   - Save Client ID and Client Secret

2. **Environment Variables**
   ```
   GITHUB_CLIENT_ID=Ov23li...
   GITHUB_CLIENT_SECRET=...
   GITHUB_CALLBACK_URL=https://xxx.ngrok.io/api/github/callback
   ```

### 1.3 Backend Tasks

#### Task 1.3.1: Create GitHubConnection Model

Create new model to store OAuth connections.

**File:** `backend/app/models/github_connection.py`

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users table |
| access_token | String | Encrypted GitHub token |
| token_type | String | Usually "bearer" |
| scope | String | Granted scopes |
| github_user_id | String | GitHub user ID |
| github_username | String | GitHub username |
| github_avatar_url | String | Avatar URL |
| connected_at | DateTime | When connected |
| updated_at | DateTime | Last update |

**Relationships:**
- `user` → User (many-to-one)
- `repositories` → Repository (one-to-many)

#### Task 1.3.2: Create Migration

**File:** `backend/migrations/create_github_connections.py`

- Create `github_connections` table
- Add indexes on `user_id` and `github_user_id`
- Add unique constraint on `(user_id, github_user_id)`

#### Task 1.3.3: Create GitHub Service

**File:** `backend/app/services/github_service.py`

**Methods:**
| Method | Description |
|--------|-------------|
| `get_authorization_url()` | Generate OAuth URL with state |
| `exchange_code_for_token(code)` | Exchange auth code for access token |
| `get_user_info(token)` | Fetch GitHub user profile |
| `encrypt_token(token)` | Encrypt token for storage |
| `decrypt_token(encrypted)` | Decrypt token for use |

#### Task 1.3.4: Create GitHub Router

**File:** `backend/app/routers/github_router.py`

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/github/auth` | GET | Redirect to GitHub OAuth |
| `/api/github/callback` | GET | Handle OAuth callback |

#### Task 1.3.5: Create GraphQL Schema

**File:** `backend/app/schemas/github.py`

**Types:**
- `GitHubConnectionType` — Connection info (id, username, avatar, etc.)

**Queries:**
- `myGitHubConnections` — List user's GitHub connections

**Mutations:**
- `disconnectGitHub(connectionId)` — Remove a connection

### 1.4 Frontend Tasks

#### Task 1.4.1: Create GitHub Context

**File:** `frontend/src/contexts/GitHubContext.tsx`

**State:**
- `connections` — List of GitHubConnection
- `isConnecting` — Loading state
- `error` — Error state

**Actions:**
- `connectGitHub()` — Initiate OAuth flow
- `disconnectGitHub(id)` — Remove connection
- `refreshConnections()` — Reload from server

#### Task 1.4.2: Create ConnectGitHubCard Component

**File:** `frontend/src/components/github/ConnectGitHubCard.tsx`

**UI States:**

Not connected:
```
┌─────────────────────────────────────────────────┐
│  🔗 GitHub Integration                          │
│                                                 │
│  Connect your GitHub account to enable          │
│  automatic code localization.                   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  🐙 Connect GitHub                       │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  We'll request access to:                       │
│  • Read repository contents                     │
│  • Create branches and pull requests            │
│                                                 │
└─────────────────────────────────────────────────┘
```

Connected:
```
┌─────────────────────────────────────────────────┐
│  🔗 GitHub Integration                          │
│                                                 │
│  ┌─────┐                                        │
│  │ 👤  │  Connected as @username               │
│  └─────┘  Connected 2 days ago                 │
│                                                 │
│           [Disconnect]                          │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Task 1.4.3: Create GitHub Settings Page

**File:** `frontend/src/pages/GitHubSettingsPage.tsx`

**Route:** `/project/:id/github`

**Sections:**
1. GitHub Connection Card
2. Connected Repositories List (empty for now)
3. Add Repository Button (disabled for now)

#### Task 1.4.4: Add Navigation

Update sidebar/navigation to include GitHub Agent link.

#### Task 1.4.5: Handle OAuth Callback

**File:** `frontend/src/pages/GitHubCallbackPage.tsx`

**Route:** `/github/callback`

**Flow:**
1. Extract `code` and `state` from URL
2. Send to backend
3. Show success/error
4. Redirect to GitHub settings page

### 1.5 Testing Checklist

#### Backend Tests

- [ ] `test_github_connection_model.py`
  - [ ] Create connection
  - [ ] Encrypt/decrypt token
  - [ ] Delete cascades properly

- [ ] `test_github_service.py`
  - [ ] Generate auth URL with state
  - [ ] Exchange code for token (mock GitHub API)
  - [ ] Handle invalid code
  - [ ] Handle expired code

- [ ] `test_github_router.py`
  - [ ] Auth endpoint redirects correctly
  - [ ] Callback handles success
  - [ ] Callback handles errors
  - [ ] State validation works

- [ ] `test_github_graphql.py`
  - [ ] Query connections (authenticated)
  - [ ] Query connections (unauthenticated → error)
  - [ ] Disconnect mutation works
  - [ ] Cannot disconnect other user's connection

#### Frontend Tests

- [ ] ConnectGitHubCard renders correctly
- [ ] Connect button opens OAuth
- [ ] Disconnect shows confirmation
- [ ] Loading states work
- [ ] Error states display properly

### 1.6 Security Considerations

| Concern | Solution |
|---------|----------|
| Token storage | Encrypt with Fernet before storing |
| State parameter | Use random UUID, verify on callback |
| CSRF protection | State parameter validates request origin |
| Token exposure | Never send token to frontend |
| Scope creep | Request minimal required scopes |

### 1.7 Acceptance Criteria

- [ ] User can click "Connect GitHub" and complete OAuth flow
- [ ] User sees their GitHub username and avatar after connecting
- [ ] User can disconnect their GitHub account
- [ ] Multiple users can connect the same GitHub account (different Keeys accounts)
- [ ] One user can connect multiple GitHub accounts
- [ ] Tokens are encrypted in database
- [ ] Invalid/expired tokens are handled gracefully
- [ ] All operations are logged for audit

### 1.8 Estimated Time

| Task | Time |
|------|------|
| Backend model + migration | 2h |
| GitHub service | 4h |
| Router + endpoints | 2h |
| GraphQL schema | 2h |
| Frontend context | 2h |
| UI components | 4h |
| Callback page | 2h |
| Testing | 4h |
| **Total** | **~22h (3 days)** |

---

## Step 2: Repository Selection

*Coming after Step 1 is complete...*

### 2.1 Overview

After connecting GitHub, users need to:
1. Browse their repositories
2. Select a repository to connect
3. Configure i18n settings

### 2.2 Backend Tasks

- Create `Repository` model
- GitHub API: list user repositories
- GitHub API: get repository details
- GraphQL: `listGitHubRepos`, `addRepository`

### 2.3 Frontend Tasks

- Repository browser dialog
- Repository card component
- i18n framework selector
- Source file patterns configuration

---

## Step 3: File Scanning with Claude

*Coming after Step 2 is complete...*

---

## Step 4: String Review & Editing

*Coming after Step 3 is complete...*

---

## Step 5: Screenshot Enhancement

*Coming after Step 4 is complete...*

---

## Step 6: Code Transformation

*Coming after Step 5 is complete...*

---

## Step 7: Pull Request Creation

*Coming after Step 6 is complete...*

---

## 🔧 Setup & Deployment

### Requirements

| Component | Purpose |
|-----------|---------|
| **Redis** | Job queue for background file analysis |
| **arq** | Async Redis queue library (Python) |

### Architecture: Background Job Processing

File scanning uses a distributed job queue for parallel processing:

```
┌─────────────────┐     ┌─────────────┐     ┌─────────────────┐
│  FastAPI        │     │             │     │  arq Worker     │
│  (main process) │     │    Redis    │     │  (separate      │
│                 │     │   (queue)   │     │   process)      │
├─────────────────┤     ├─────────────┤     ├─────────────────┤
│                 │     │             │     │                 │
│  startScan()    │────▶│  Job Queue  │◀────│  analyze_file() │
│                 │     │             │     │                 │
│  Collects       │◀────│  Results    │─────│  Claude API     │
│  results        │     │             │     │                 │
│                 │     │             │     │                 │
│  Writes to DB   │     │             │     │  Returns:       │
│  (strings,      │     │             │     │  - strings[]    │
│   token usage)  │     │             │     │  - token_usage  │
│                 │     │             │     │                 │
└─────────────────┘     └─────────────┘     └─────────────────┘
```

### Environment Variables

Add to your `.env`:

```env
# Redis (for background job queue)
REDIS_URL=redis://localhost:6379

# Scanner configuration
SCANNER_MAX_CONCURRENT_JOBS=5
SCANNER_JOB_TIMEOUT=300
```

### Running Locally

**Terminal 1 — Backend API:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 — Worker:**
```bash
cd backend
source venv/bin/activate
arq worker.WorkerSettings
```

### Railway Deployment

Deploy **two services** from the same repository:

#### Service 1: API
- **Root Directory:** `backend`
- **Start Command:** `python main.py`
- **Environment:** Add all env vars

#### Service 2: Worker
- **Root Directory:** `backend`
- **Start Command:** `arq worker.WorkerSettings`
- **Environment:** Same env vars as API

#### Service 3: Redis
- Add Redis from Railway marketplace
- Copy `REDIS_URL` to both services

```
┌─────────────────────────────────────────────────────┐
│                    Railway Project                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │   API    │  │  Worker  │  │      Redis       │  │
│  │ Service  │  │ Service  │  │     (addon)      │  │
│  │          │  │          │  │                  │  │
│  │ python   │  │ arq      │  │ redis://...      │  │
│  │ main.py  │  │ worker   │  │                  │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │             │                 │            │
│       └─────────────┴────────────────►│            │
│                   REDIS_URL                        │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Scaling Workers

Need more throughput? Scale horizontally:

```bash
# Run multiple workers
arq worker.WorkerSettings --workers 3
```

Or deploy multiple worker instances on Railway.

---

## 💰 Cost Estimation

### Claude API Costs

| Model | Input | Output |
|-------|-------|--------|
| Claude Sonnet | $3/1M tokens | $15/1M tokens |
| Claude Opus | $15/1M tokens | $75/1M tokens |

### Typical Usage

| Operation | Tokens | Cost (Sonnet) |
|-----------|--------|---------------|
| Scan 1 file | ~2,500 | ~$0.03 |
| Scan 100 files | ~250,000 | ~$3 |
| Screenshot analysis | ~1,500 | ~$0.02 |
| Full repo scan (500 files) | ~1,250,000 | ~$15 |

### Cost Optimization

- **File filtering** — Only scan relevant files (*.tsx, not *.test.tsx)
- **Caching** — Cache results, don't rescan unchanged files
- **Batching** — Send multiple small files in one request
- **Model selection** — Use Sonnet for scanning, Opus only for complex cases

## 🔐 Security Considerations

### Data Protection

| Concern | Mitigation |
|---------|------------|
| OAuth tokens | Encrypted at rest (Fernet) |
| Source code | Never stored permanently, processed in memory |
| API keys | Environment variables only |
| User data | Standard Keeys security practices |

### GitHub Permissions

- Request minimal necessary scopes
- Users can revoke access anytime
- Clear permission explanation in UI

### Audit Trail

- Log all GitHub operations
- Track who initiated scans/PRs
- Maintain activity history

## 📚 Supported Frameworks

### Currently Planned

| Framework | Language | i18n Library |
|-----------|----------|--------------|
| React | TypeScript/JavaScript | react-i18next |
| Next.js | TypeScript/JavaScript | next-intl |
| Vue | TypeScript/JavaScript | vue-i18n |
| Svelte | TypeScript/JavaScript | svelte-i18n |
| Angular | TypeScript | @ngx-translate |

### Future (Claude supports, just need prompts)

- Python (gettext, babel)
- Ruby on Rails (i18n gem)
- Swift (NSLocalizedString)
- Kotlin (Android strings.xml)
- Flutter (intl)

## 🔗 Related Documentation

- [[AI Autopilot Feature]] — Existing AI translation features
- [[Project Export Import]] — File handling patterns
- [[Authentication Setup]] — OAuth implementation reference
- [[Security Best Practices]] — Security guidelines

---

*Document created: 2024-12-19*
*Last updated: 2024-12-20*
