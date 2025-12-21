"""
Anthropic AI Service for code analysis using Claude API.
"""
from typing import Optional, TypedDict
import logging
import json
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class TokenUsageInfo(TypedDict):
    """Type definition for token usage information."""
    input_tokens: int
    output_tokens: int
    total_tokens: int


class FoundStringInfo(TypedDict):
    """Type definition for a found string in code."""
    text: str
    line: int
    suggested_key: str
    context: str
    confidence: float


class AnalysisResult(TypedDict):
    """Type definition for file analysis result."""
    strings: list[FoundStringInfo]
    token_usage: TokenUsageInfo


class AnthropicService:
    """Service for code analysis operations using Anthropic Claude API."""
    
    ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
    
    def __init__(self):
        """Initialize Anthropic client."""
        if not settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            self.api_key = None
        else:
            self.api_key = settings.anthropic_api_key
    
    def _is_available(self) -> bool:
        """Check if Anthropic service is available."""
        return self.api_key is not None
    
    async def analyze_file_for_strings(
        self,
        file_content: str,
        file_path: str,
        i18n_framework: Optional[str] = None,
        existing_keys: Optional[list[str]] = None,
        model: Optional[str] = None,
        key_naming_style: Optional[str] = None,
        key_naming_delimiter: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Analyze a source file to find hardcoded strings that need localization.
        
        Args:
            file_content: Content of the source file
            file_path: Path to the file (for context)
            i18n_framework: Optional i18n framework name (react-i18next, vue-i18n, etc.)
            existing_keys: Optional list of existing translation keys to avoid duplicates
            model: Optional model override (defaults to settings.anthropic_model)
            key_naming_style: Key naming style (UPPERCASE, snake_case, camelCase)
            key_naming_delimiter: Delimiter for key segments (_, ., :, ::)
            
        Returns:
            AnalysisResult with found strings and token usage
            
        Raises:
            Exception: If service is not available or API error occurs
        """
        if not self._is_available():
            raise Exception("Anthropic service is not configured")
        
        use_model = model or settings.anthropic_model
        
        # Build the system prompt
        system_prompt = self._build_analysis_system_prompt(
            i18n_framework, existing_keys, key_naming_style, key_naming_delimiter
        )
        
        # Build the user prompt
        user_prompt = self._build_analysis_user_prompt(file_content, file_path)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ANTHROPIC_API_URL,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": use_model,
                        "max_tokens": 4096,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": user_prompt}
                        ],
                    },
                    timeout=120.0,
                )
                
                if response.status_code != 200:
                    logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                    raise Exception("Failed to analyze file. Please try again.")
                
                data = response.json()
                
                # Extract token usage
                usage = data.get("usage", {})
                token_usage: TokenUsageInfo = {
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                }
                
                # Extract response content
                content = data.get("content", [])
                if not content:
                    return {"strings": [], "token_usage": token_usage}
                
                response_text = content[0].get("text", "")
                
                # Strip markdown code blocks if present
                response_text = response_text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]  # Remove ```json
                elif response_text.startswith("```"):
                    response_text = response_text[3:]  # Remove ```
                if response_text.endswith("```"):
                    response_text = response_text[:-3]  # Remove trailing ```
                response_text = response_text.strip()
                
                # Parse JSON response
                try:
                    result = json.loads(response_text)
                    
                    # Handle both formats: {"strings": [...]} and direct array [...]
                    if isinstance(result, list):
                        strings = result
                    elif isinstance(result, dict):
                        strings = result.get("strings", [])
                    else:
                        strings = []
                    
                    # Validate and normalize strings
                    validated_strings: list[FoundStringInfo] = []
                    for s in strings:
                        if isinstance(s, dict) and "text" in s and "suggested_key" in s:
                            validated_strings.append({
                                "text": str(s.get("text", "")),
                                "line": int(s.get("line", 0)),
                                "suggested_key": str(s.get("suggested_key", "")),
                                "context": str(s.get("context", "")),
                                "confidence": float(s.get("confidence", 0.8)),
                            })
                    
                    logger.info(f"Found {len(validated_strings)} strings in {file_path}")
                    return {"strings": validated_strings, "token_usage": token_usage}
                    
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {response_text[:500]}")
                    return {"strings": [], "token_usage": token_usage}
                    
        except httpx.TimeoutException:
            logger.error("Anthropic API timeout")
            raise Exception("Analysis timed out. Please try again.")
        except Exception as e:
            logger.error(f"Anthropic API error: {type(e).__name__}: {str(e)}")
            raise Exception("Failed to analyze file. Please try again.")
    
    def _build_analysis_system_prompt(
        self,
        i18n_framework: Optional[str] = None,
        existing_keys: Optional[list[str]] = None,
        key_naming_style: Optional[str] = None,
        key_naming_delimiter: Optional[str] = None,
    ) -> str:
        """Build the system prompt for file analysis."""
        framework_context = ""
        if i18n_framework:
            framework_context = f"""
The project uses {i18n_framework} for internationalization.
When generating keys, follow the conventions typical for {i18n_framework}.
"""
        
        existing_keys_context = ""
        if existing_keys:
            keys_sample = existing_keys[:50]  # Limit to avoid huge prompts
            existing_keys_context = f"""
Existing translation keys in the project (sample):
{', '.join(keys_sample)}

Try to follow the existing naming conventions and avoid duplicating these keys.
"""
        
        # Build key naming convention based on style and delimiter
        naming_convention = self._build_key_naming_convention(key_naming_style, key_naming_delimiter)
        
        return f"""You are an expert code analyzer specializing in internationalization (i18n).
Your task is to analyze source code files and identify user-facing strings that should be localized.

{framework_context}
{existing_keys_context}

RULES FOR IDENTIFYING STRINGS TO LOCALIZE:
1. INCLUDE (should be localized):
   - UI text: button labels, headings, descriptions, placeholders
   - Error messages shown to users
   - Tooltips and help text
   - Form labels and validation messages
   - Navigation items and menu text
   - Notification and toast messages

2. EXCLUDE (do NOT localize):
   - Technical strings: URLs, API endpoints, file paths
   - CSS class names and IDs
   - Console.log messages and debug output
   - Variable names and code identifiers
   - Strings already wrapped in i18n functions (t(), $t(), etc.)
   - HTML attributes like "type", "name", "id"
   - Empty strings or whitespace-only strings
   - Single characters or punctuation

{naming_convention}

RESPONSE FORMAT:
You MUST respond with valid JSON only, no other text. Use this exact format:
{{
  "strings": [
    {{
      "text": "The exact string found in code",
      "line": 24,
      "suggested_key": "namespace{key_naming_delimiter or '.'}component{key_naming_delimiter or '.'}element",
      "context": "Brief description of where/how this string is used",
      "confidence": 0.95
    }}
  ]
}}

If no strings need localization, return: {{"strings": []}}
"""

    def _build_key_naming_convention(
        self,
        style: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> str:
        """Build key naming convention section based on style and delimiter."""
        # Default values
        style = style or "camelCase"
        delimiter = delimiter or "."
        
        # Style descriptions and examples
        style_configs = {
            "UPPERCASE": {
                "case_desc": "UPPERCASE for each segment",
                "example_component": "APP_SIDEBAR",
                "example_section": "BRAND",
                "example_element": "NAME",
            },
            "snake_case": {
                "case_desc": "snake_case for each segment (all lowercase with underscores within segment)",
                "example_component": "app_sidebar",
                "example_section": "brand",
                "example_element": "name",
            },
            "camelCase": {
                "case_desc": "camelCase for each segment",
                "example_component": "appSidebar",
                "example_section": "brand",
                "example_element": "name",
            },
        }
        
        config = style_configs.get(style, style_configs["camelCase"])
        
        # Build examples
        d = delimiter  # shorthand
        comp = config["example_component"]
        sect = config["example_section"]
        elem = config["example_element"]
        
        # Generate examples for different contexts
        examples = f"""
EXAMPLES:
- AppSidebar brand name: "{comp}{d}{sect}{d}{elem}" ✓
- Login page title: "{"LOGIN_PAGE" if style == "UPPERCASE" else "login_page" if style == "snake_case" else "loginPage"}{d}{"TITLE" if style == "UPPERCASE" else "title"}" ✓
- Login form submit button: "{"LOGIN_PAGE" if style == "UPPERCASE" else "login_page" if style == "snake_case" else "loginPage"}{d}{"FORM" if style == "UPPERCASE" else "form"}{d}{"SUBMIT_BUTTON" if style == "UPPERCASE" else "submit_button" if style == "snake_case" else "submitButton"}" ✓
- Navigation home link: "{"NAVIGATION" if style == "UPPERCASE" else "navigation"}{d}{"HOME" if style == "UPPERCASE" else "home"}{d}{"LABEL" if style == "UPPERCASE" else "label"}" ✓
- Error validation required: "{"ERRORS" if style == "UPPERCASE" else "errors"}{d}{"VALIDATION" if style == "UPPERCASE" else "validation"}{d}{"REQUIRED" if style == "UPPERCASE" else "required"}" ✓
"""

        # Build wrong format examples based on current style
        wrong_examples = self._build_wrong_format_examples(style, delimiter)
        
        return f"""KEY NAMING CONVENTIONS (STRICTLY FOLLOW THIS FORMAT):
- Format: component{d}entity{d}block{d}textDescription
- Use {config["case_desc"]}
- Use "{d}" as the ONLY separator between segments
- Structure: [component]{d}[entity/section]{d}[element]{d}[description]

NAMING RULES:
1. Component name from file/folder: AppSidebar.tsx -> "{comp}"
2. Entity/section describes the area: "{sect}", "{"NAVIGATION" if style == "UPPERCASE" else "navigation"}", "{"HEADER" if style == "UPPERCASE" else "header"}", "{"FOOTER" if style == "UPPERCASE" else "footer"}"
3. Element (optional) for nested items: "{"ITEM" if style == "UPPERCASE" else "item"}", "{"BUTTON" if style == "UPPERCASE" else "button"}", "{"LINK" if style == "UPPERCASE" else "link"}", "{"INPUT" if style == "UPPERCASE" else "input"}"
4. Description of the text purpose: "{"TITLE" if style == "UPPERCASE" else "title"}", "{"LABEL" if style == "UPPERCASE" else "label"}", "{"PLACEHOLDER" if style == "UPPERCASE" else "placeholder"}", "{"DESCRIPTION" if style == "UPPERCASE" else "description"}"

{examples}

{wrong_examples}"""

    def _build_wrong_format_examples(self, style: str, delimiter: str) -> str:
        """Build wrong format examples based on current style."""
        wrong = []
        
        # Always wrong: mixing styles
        if style != "UPPERCASE":
            wrong.append('- "APP_SIDEBAR_BRAND" ✗ (UPPERCASE not allowed)')
        if style != "camelCase":
            wrong.append('- "appSidebar.brandName" ✗ (camelCase not allowed)' if delimiter != "." else '- "appSidebarBrandName" ✗ (camelCase segments not allowed)')
        if style != "snake_case":
            wrong.append('- "app_sidebar_brand" ✗ (snake_case not allowed)' if "_" not in delimiter else '')
        
        # Wrong delimiters
        if delimiter != ".":
            wrong.append('- "app.sidebar.brand" ✗ (dots not allowed as delimiter)')
        if delimiter != "_":
            wrong.append('- "app_sidebar_brand" ✗ (underscores not allowed as delimiter)')
        if delimiter != ":":
            wrong.append('- "app:sidebar:brand" ✗ (single colon not allowed as delimiter)')
        if delimiter != "::":
            wrong.append('- "app::sidebar::brand" ✗ (double colon not allowed as delimiter)')
        
        # Always wrong
        wrong.append('- "app-sidebar-brand" ✗ (dashes never allowed)')
        
        # Filter empty strings and limit
        wrong = [w for w in wrong if w][:6]
        
        return "WRONG FORMATS (NEVER USE):\n" + "\n".join(wrong)

    def _build_analysis_user_prompt(self, file_content: str, file_path: str) -> str:
        """Build the user prompt for file analysis."""
        # Determine file type from path
        file_type = "unknown"
        if file_path.endswith((".tsx", ".jsx")):
            file_type = "React component"
        elif file_path.endswith(".vue"):
            file_type = "Vue component"
        elif file_path.endswith(".svelte"):
            file_type = "Svelte component"
        elif file_path.endswith((".ts", ".js")):
            file_type = "JavaScript/TypeScript"
        elif file_path.endswith(".py"):
            file_type = "Python"
        
        return f"""Analyze this {file_type} file and find all user-facing strings that need localization.

File path: {file_path}

```
{file_content}
```

Remember: Return ONLY valid JSON with the found strings. Do not include any explanations or markdown formatting."""


# Global instance
anthropic_service = AnthropicService()

