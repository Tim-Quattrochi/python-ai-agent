"""Minimal test of cover letter generator."""

from src.tools.job_automation.job_scraper import JobPosting
from src.tools.base import Tool
from src.tools.job_automation.company_research import CompanyInfo
from src.tools.job_automation.resume_parser import ResumeData
import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Test basic dataclass first


@dataclass
class TestTemplate:
    """Test template."""
    name: str = ""
    style: str = ""


print("Dataclass definition successful")

print("ResumeData import successful")

print("JobPosting import successful")

print("CompanyInfo import successful")

print("Tool import successful")

# Now try the actual dataclass with the full imports


@dataclass
class CoverLetterTemplate:
    """Cover letter template structure."""
    name: str = ""
    style: str = ""  # professional, creative, technical, executive
    tone: str = ""   # formal, conversational, enthusiastic, confident
    # paragraph types: intro, value_prop, experience, company_fit, closing
    structure: List[str] = None
    placeholders: Dict[str, str] = None

    def __post_init__(self):
        if self.structure is None:
            self.structure = ["intro", "value_prop",
                              "experience", "company_fit", "closing"]
        if self.placeholders is None:
            self.placeholders = {}


print("CoverLetterTemplate definition successful")


class TestTool(Tool):
    def __init__(self):
        super().__init__(
            name="test_tool",
            description="Test tool"
        )

    def get_schema(self):
        return {"type": "object"}

    def execute(self, **kwargs):
        return {"success": True}


print("Tool class definition successful")
print("All tests passed!")
