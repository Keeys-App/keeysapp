"""
Email template service for parsing and rendering Markdown email templates.
"""
import os
import logging
from typing import Optional
from dataclasses import dataclass

import frontmatter
import markdown

logger = logging.getLogger(__name__)

# Path to email templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates", "emails")


@dataclass
class EmailTemplate:
    """Rendered email template with all parts."""
    subject: str
    text_content: str
    html_content: str


class EmailTemplateService:
    """
    Service for loading and rendering Markdown email templates.
    
    Templates are stored as .md files with YAML frontmatter:
    ---
    subject: Email subject with {variables}
    description: Plain text fallback with {variables}
    ---
    
    # Markdown content with {variables}
    """
    
    _instance: Optional["EmailTemplateService"] = None
    _templates_cache: dict[str, frontmatter.Post] = {}
    
    def __init__(self):
        """Initialize the template service."""
        self._md = markdown.Markdown(
            extensions=[
                'extra',  # Tables, fenced code, etc.
                'nl2br',  # Newlines to <br>
                'sane_lists',  # Better list handling
            ]
        )
        logger.info(f"Email template service initialized. Templates dir: {TEMPLATES_DIR}")
    
    @classmethod
    def get_instance(cls) -> "EmailTemplateService":
        """Get singleton instance of EmailTemplateService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_template(self, template_name: str) -> Optional[frontmatter.Post]:
        """
        Load a template file from disk.
        
        Args:
            template_name: Name of the template (without .md extension)
            
        Returns:
            Parsed frontmatter Post object or None if not found
        """
        # Check cache first
        if template_name in self._templates_cache:
            return self._templates_cache[template_name]
        
        template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.md")
        
        if not os.path.exists(template_path):
            logger.error(f"Email template not found: {template_path}")
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                self._templates_cache[template_name] = post
                logger.info(f"Loaded email template: {template_name}")
                return post
        except Exception as e:
            logger.error(f"Failed to load email template {template_name}: {type(e).__name__}")
            return None
    
    def _render_variables(self, text: str, variables: dict) -> str:
        """
        Replace {variable} placeholders with actual values.
        
        Args:
            text: Text with {variable} placeholders
            variables: Dictionary of variable names to values
            
        Returns:
            Text with variables replaced
        """
        result = text
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def _convert_md_to_html(self, md_content: str) -> str:
        """
        Convert Markdown content to HTML.
        
        Args:
            md_content: Markdown string
            
        Returns:
            HTML string
        """
        # Reset the markdown instance for clean conversion
        self._md.reset()
        return self._md.convert(md_content)
    
    def _wrap_html(self, html_body: str) -> str:
        """
        Wrap HTML body in a complete HTML document with basic styling.
        
        Args:
            html_body: HTML content
            
        Returns:
            Complete HTML document
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 24px;
            margin-bottom: 16px;
        }}
        h2 {{
            color: #333;
            font-size: 18px;
            margin-top: 24px;
            margin-bottom: 12px;
        }}
        p {{
            margin: 12px 0;
        }}
        ul, ol {{
            margin: 12px 0;
            padding-left: 24px;
        }}
        li {{
            margin: 6px 0;
        }}
        strong {{
            color: #1a1a1a;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 1px solid #eee;
            margin: 24px 0;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    def render(self, template_name: str, variables: dict) -> Optional[EmailTemplate]:
        """
        Render an email template with the given variables.
        
        Args:
            template_name: Name of the template (e.g., 'welcome')
            variables: Dictionary of variables to substitute
            
        Returns:
            EmailTemplate with subject, text_content, and html_content,
            or None if template not found
        """
        template = self._load_template(template_name)
        if not template:
            return None
        
        # Get frontmatter fields
        subject = template.get('subject', 'No Subject')
        description = template.get('description', '')
        body = template.content
        
        # Render variables in all parts
        subject = self._render_variables(subject, variables)
        text_content = self._render_variables(description, variables)
        body = self._render_variables(body, variables)
        
        # Convert body to HTML
        html_body = self._convert_md_to_html(body)
        html_content = self._wrap_html(html_body)
        
        return EmailTemplate(
            subject=subject,
            text_content=text_content,
            html_content=html_content
        )
    
    def clear_cache(self) -> None:
        """Clear the templates cache."""
        self._templates_cache.clear()
        logger.info("Email templates cache cleared")

