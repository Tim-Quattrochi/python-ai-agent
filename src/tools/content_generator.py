"""Content generation and media processing tools."""

import logging
import requests
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import tempfile
import subprocess

from .base import Tool

logger = logging.getLogger(__name__)


class ContentGeneratorTool(Tool):
    """Tool for content generation and media processing."""

    name = "content_generator"
    description = "Generate various types of content, process media, and create documents"

    def __init__(self):
        """Initialize content generator tool."""
        super().__init__(
            name="content_generator",
            description="Generate various types of content, process media, and create documents"
        )

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for content generator parameters."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["generate_text", "create_markdown", "generate_html", "create_presentation", "process_text", "extract_text_from_pdf"],
                    "description": "The content generation action to perform"
                },
                "prompt": {
                    "type": "string",
                    "description": "Text prompt for content generation"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["general", "article", "blog", "email", "social", "technical"],
                    "default": "general",
                    "description": "Type of content to generate"
                },
                "length": {
                    "type": "string",
                    "enum": ["short", "medium", "long"],
                    "default": "medium",
                    "description": "Length of generated content"
                },
                "title": {
                    "type": "string",
                    "description": "Title for the document or presentation"
                },
                "content": {
                    "type": "string",
                    "description": "Main content for the document"
                },
                "sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of sections for structured documents"
                },
                "output_path": {
                    "type": "string",
                    "description": "File path where output should be saved"
                },
                "text": {
                    "type": "string",
                    "description": "Text to process"
                },
                "operations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of text processing operations"
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute content generation operations."""
        try:
            if action == "generate_text":
                return self._generate_text(
                    prompt=kwargs.get('prompt'),
                    content_type=kwargs.get('content_type', 'general'),
                    length=kwargs.get('length', 'medium')
                )
            elif action == "create_markdown":
                return self._create_markdown(
                    title=kwargs.get('title'),
                    content=kwargs.get('content'),
                    sections=kwargs.get('sections', []),
                    output_path=kwargs.get('output_path')
                )
            elif action == "generate_html":
                return self._generate_html(
                    title=kwargs.get('title'),
                    content=kwargs.get('content'),
                    template=kwargs.get('template', 'basic'),
                    output_path=kwargs.get('output_path')
                )
            elif action == "create_presentation":
                return self._create_presentation(
                    title=kwargs.get('title'),
                    slides=kwargs.get('slides', []),
                    output_path=kwargs.get('output_path')
                )
            elif action == "process_text":
                return self._process_text(
                    text=kwargs.get('text'),
                    operations=kwargs.get('operations', [])
                )
            elif action == "extract_text_from_pdf":
                return self._extract_text_from_pdf(
                    pdf_path=kwargs.get('pdf_path')
                )
            elif action == "generate_qr_code":
                return self._generate_qr_code(
                    data=kwargs.get('data'),
                    output_path=kwargs.get('output_path')
                )
            elif action == "create_csv_report":
                return self._create_csv_report(
                    data=kwargs.get('data'),
                    output_path=kwargs.get('output_path'),
                    headers=kwargs.get('headers')
                )
            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Error in content generator tool: {str(e)}")
            return {"error": f"Content generator error: {str(e)}"}

    def _generate_text(self, prompt: str, content_type: str = 'general', length: str = 'medium') -> Dict[str, Any]:
        """Generate text content based on prompts and templates."""
        try:
            templates = {
                'email': {
                    'short': f"Subject: {prompt}\n\nDear [Recipient],\n\n[Brief content based on: {prompt}]\n\nBest regards,\n[Your name]",
                    'medium': f"Subject: {prompt}\n\nDear [Recipient],\n\nI hope this email finds you well.\n\n[Detailed content about: {prompt}]\n\nPlease let me know if you have any questions.\n\nBest regards,\n[Your name]",
                    'long': f"Subject: {prompt}\n\nDear [Recipient],\n\nI hope this email finds you well.\n\n[Introduction paragraph]\n\n[Main content about: {prompt}]\n\n[Supporting details and examples]\n\n[Call to action or next steps]\n\nPlease don't hesitate to reach out if you need any clarification.\n\nBest regards,\n[Your name]"
                },
                'blog_post': {
                    'short': f"# {prompt}\n\n[Introduction]\n\n[Main point about {prompt}]\n\n[Conclusion]",
                    'medium': f"# {prompt}\n\n## Introduction\n[Hook and context]\n\n## Main Content\n[Detailed discussion of {prompt}]\n\n## Key Points\n- Point 1\n- Point 2\n- Point 3\n\n## Conclusion\n[Summary and takeaways]",
                    'long': f"# {prompt}\n\n## Introduction\n[Engaging hook and background]\n\n## Background\n[Context and relevance]\n\n## Deep Dive: {prompt}\n[Comprehensive analysis]\n\n## Examples and Case Studies\n[Real-world applications]\n\n## Best Practices\n[Actionable recommendations]\n\n## Future Implications\n[Looking ahead]\n\n## Conclusion\n[Key takeaways and call to action]"
                },
                'report': {
                    'short': f"# Report: {prompt}\n\n## Executive Summary\n[Brief overview]\n\n## Findings\n[Key findings about {prompt}]\n\n## Recommendations\n[Action items]",
                    'medium': f"# Report: {prompt}\n\n## Executive Summary\n[Overview and key points]\n\n## Methodology\n[How the analysis was conducted]\n\n## Findings\n[Detailed findings about {prompt}]\n\n## Analysis\n[Interpretation of results]\n\n## Recommendations\n[Specific action items]\n\n## Conclusion\n[Summary and next steps]",
                    'long': f"# Comprehensive Report: {prompt}\n\n## Executive Summary\n[High-level overview and key recommendations]\n\n## Introduction and Scope\n[Purpose and boundaries of the report]\n\n## Methodology\n[Research and analysis approach]\n\n## Background and Context\n[Relevant background information]\n\n## Detailed Findings\n[Comprehensive analysis of {prompt}]\n\n## Data Analysis\n[Statistical and qualitative insights]\n\n## Risk Assessment\n[Potential challenges and mitigation strategies]\n\n## Recommendations\n[Prioritized action items with timelines]\n\n## Implementation Plan\n[Step-by-step execution strategy]\n\n## Conclusion\n[Summary and expected outcomes]\n\n## Appendices\n[Supporting data and references]"
                }
            }

            template = templates.get(content_type, {}).get(
                length, f"Content about: {prompt}\n\n[Generated content would be {length} length for {content_type} type]")

            return {
                "success": True,
                "message": f"📝 Generated {content_type} content ({length} length)",
                "content": template,
                "content_type": content_type,
                "length": length,
                "word_count": len(template.split())
            }

        except Exception as e:
            return {"error": f"Text generation failed: {str(e)}"}

    def _create_markdown(self, title: str, content: str, sections: List[Dict] = None, output_path: str = None) -> Dict[str, Any]:
        """Create a structured markdown document."""
        try:
            md_content = f"# {title}\n\n"

            if content:
                md_content += f"{content}\n\n"

            if sections:
                for section in sections:
                    level = section.get('level', 2)
                    section_title = section.get('title', 'Untitled Section')
                    section_content = section.get('content', '')

                    md_content += f"{'#' * level} {section_title}\n\n"
                    if section_content:
                        md_content += f"{section_content}\n\n"

            # Add metadata
            md_content += f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

            return {
                "success": True,
                "message": f"📄 Markdown document created: {title}",
                "content": md_content,
                "output_path": output_path,
                "character_count": len(md_content),
                "sections_count": len(sections) if sections else 0
            }

        except Exception as e:
            return {"error": f"Markdown creation failed: {str(e)}"}

    def _generate_html(self, title: str, content: str, template: str = 'basic', output_path: str = None) -> Dict[str, Any]:
        """Generate HTML document from content."""
        try:
            templates = {
                'basic': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1 {{ color: #333; border-bottom: 2px solid #007acc; }}
        .content {{ margin-top: 20px; }}
        .footer {{ margin-top: 40px; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="content">
        {content}
    </div>
    <div class="footer">
        Generated on {timestamp}
    </div>
</body>
</html>''',
                'modern': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.8; background: #f5f5f5; color: #333;
        }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; margin-bottom: 30px; font-size: 2.5em; }}
        .content {{ font-size: 1.1em; }}
        .footer {{ margin-top: 50px; text-align: center; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            Generated on {timestamp}
        </div>
    </div>
</body>
</html>'''
            }

            html_template = templates.get(template, templates['basic'])
            html_content = html_template.format(
                title=title,
                content=content.replace('\n', '<br>\n'),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

            return {
                "success": True,
                "message": f"🌐 HTML document generated: {title}",
                "content": html_content,
                "output_path": output_path,
                "template_used": template,
                "file_size": len(html_content.encode('utf-8'))
            }

        except Exception as e:
            return {"error": f"HTML generation failed: {str(e)}"}

    def _create_presentation(self, title: str, slides: List[Dict], output_path: str = None) -> Dict[str, Any]:
        """Create a presentation in markdown format (compatible with reveal.js)."""
        try:
            presentation_content = f"# {title}\n\n---\n\n"

            for i, slide in enumerate(slides):
                slide_title = slide.get('title', f'Slide {i+1}')
                slide_content = slide.get('content', '')
                slide_notes = slide.get('notes', '')

                presentation_content += f"## {slide_title}\n\n"
                if slide_content:
                    presentation_content += f"{slide_content}\n\n"
                if slide_notes:
                    presentation_content += f"Note: {slide_notes}\n\n"

                if i < len(slides) - 1:
                    presentation_content += "---\n\n"

            # Add metadata slide
            presentation_content += f"---\n\n## Thank You\n\n*Presentation generated on {datetime.now().strftime('%Y-%m-%d')}*\n"

            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(presentation_content)

            return {
                "success": True,
                "message": f"🎯 Presentation created: {title}",
                "content": presentation_content,
                "output_path": output_path,
                "slides_count": len(slides),
                "total_length": len(presentation_content)
            }

        except Exception as e:
            return {"error": f"Presentation creation failed: {str(e)}"}

    def _process_text(self, text: str, operations: List[str]) -> Dict[str, Any]:
        """Process text with various operations."""
        try:
            processed_text = text
            applied_operations = []

            for operation in operations:
                if operation == "uppercase":
                    processed_text = processed_text.upper()
                    applied_operations.append("uppercase")
                elif operation == "lowercase":
                    processed_text = processed_text.lower()
                    applied_operations.append("lowercase")
                elif operation == "title_case":
                    processed_text = processed_text.title()
                    applied_operations.append("title_case")
                elif operation == "remove_extra_spaces":
                    processed_text = ' '.join(processed_text.split())
                    applied_operations.append("remove_extra_spaces")
                elif operation == "remove_punctuation":
                    import string
                    processed_text = processed_text.translate(
                        str.maketrans('', '', string.punctuation))
                    applied_operations.append("remove_punctuation")
                elif operation == "extract_emails":
                    import re
                    emails = re.findall(
                        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                    return {
                        "success": True,
                        "message": f"📧 Extracted {len(emails)} email addresses",
                        "emails": emails,
                        "operation": "extract_emails"
                    }
                elif operation == "word_count":
                    words = len(text.split())
                    chars = len(text)
                    return {
                        "success": True,
                        "message": f"📊 Text analysis complete",
                        "word_count": words,
                        "character_count": chars,
                        "character_count_no_spaces": len(text.replace(' ', '')),
                        "operation": "word_count"
                    }

            return {
                "success": True,
                "message": f"🔧 Text processed with {len(applied_operations)} operations",
                "original_text": text,
                "processed_text": processed_text,
                "operations_applied": applied_operations,
                "original_length": len(text),
                "processed_length": len(processed_text)
            }

        except Exception as e:
            return {"error": f"Text processing failed: {str(e)}"}

    def _generate_qr_code(self, data: str, output_path: str = None) -> Dict[str, Any]:
        """Generate QR code for given data."""
        try:
            import qrcode
            from PIL import Image

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            if output_path:
                img.save(output_path)
            else:
                output_path = f"qr_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                img.save(output_path)

            return {
                "success": True,
                "message": f"📱 QR code generated for data",
                "data": data,
                "output_path": output_path,
                "data_length": len(data)
            }

        except ImportError:
            return {"error": "qrcode library not installed. Run: pip install qrcode[pil]"}
        except Exception as e:
            return {"error": f"QR code generation failed: {str(e)}"}

    def _create_csv_report(self, data: List[Dict], output_path: str = None, headers: List[str] = None) -> Dict[str, Any]:
        """Create CSV report from data."""
        try:
            import csv

            if not data:
                return {"error": "No data provided"}

            if not headers and data:
                headers = list(data[0].keys())

            if not output_path:
                output_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)

            return {
                "success": True,
                "message": f"📊 CSV report created with {len(data)} rows",
                "output_path": output_path,
                "rows_count": len(data),
                "columns_count": len(headers),
                "headers": headers
            }

        except Exception as e:
            return {"error": f"CSV report creation failed: {str(e)}"}
