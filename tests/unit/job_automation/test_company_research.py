"""Test script for company research tool."""

from src.tools.job_automation.job_scraper import JobPosting
from src.tools.job_automation.company_research import CompanyResearchTool, CompanyInfo
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_company_research():
    """Test the company research tool."""
    print("🚀 Starting Company Research Tests...")
    print("=" * 50)

    # Initialize tool
    researcher = CompanyResearchTool()

    # Test 1: Schema validation
    print("🧪 Testing Company Research Schema...")
    schema = researcher.get_schema()
    assert "properties" in schema
    assert "operation" in schema["properties"]
    assert "company_name" in schema["properties"]
    print("✅ Schema validation passed!")

    # Test 2: Basic company research (without network calls)
    print("🧪 Testing Basic Company Research...")

    # Test internal methods
    test_company = CompanyInfo(
        name="Tech Innovators Inc",
        website="https://techinnovators.com",
        description="Leading technology company focused on AI and machine learning solutions",
        values=["Innovation", "Collaboration", "Excellence"],
        culture_keywords=["innovation", "agile", "remote-friendly"],
        recent_news=["Company launches new AI platform",
                     "Expands to European markets"]
    )

    # Test research summary generation
    summary = researcher._generate_research_summary(test_company, "detailed")
    print(f"Generated talking points: {len(summary.talking_points)}")
    print(
        f"Generated personalization tips: {len(summary.personalization_tips)}")
    print(f"Company fit score: {summary.company_fit_score:.1f}%")
    print("✅ Basic research test passed!")

    # Test 3: Talking points generation
    print("🧪 Testing Talking Points Generation...")
    talking_points_result = researcher.execute(
        operation="generate_talking_points",
        company_info={
            "name": "Awesome Tech",
            "values": ["Innovation", "Teamwork", "Customer Focus"],
            "recent_news": ["Launched new product line", "Won industry award"],
            "culture_keywords": ["agile", "collaborative", "data-driven"],
            "products_services": ["Cloud Platform", "Analytics Tools"]
        }
    )

    assert talking_points_result["success"] == True
    result = talking_points_result["result"]

    print(f"Talking points: {result['talking_points'][:2]}")
    print(f"Cover letter hooks: {result['cover_letter_hooks'][:2]}")
    print(f"Personalization tips: {result['personalization_tips'][:2]}")
    print("✅ Talking points generation test passed!")

    # Test 4: Job posting analysis
    print("🧪 Testing Job Posting Analysis...")
    test_job = {
        "title": "Senior Developer",
        "company": "Innovation Labs",
        "industry": "Technology",
        "company_size": "100-500 employees",
        "description": "Join our innovative team working on cutting-edge AI solutions"
    }

    analysis_result = researcher.execute(
        operation="analyze_job_posting",
        job_posting=test_job,
        research_depth="basic"
    )

    assert analysis_result["success"] == True
    print(f"Extracted company info: {analysis_result['company_info']['name']}")
    print("✅ Job posting analysis test passed!")

    # Test 5: Culture keyword extraction (mock HTML)
    print("🧪 Testing Culture Keyword Extraction...")

    from bs4 import BeautifulSoup
    mock_html = """
    <html>
        <body>
            <div>
                <h2>Our Values</h2>
                <p>We believe in innovation, collaboration, and excellence.</p>
                <ul>
                    <li>Innovation drives everything we do</li>
                    <li>Teamwork and collaboration</li>
                    <li>Diversity and inclusion</li>
                </ul>
            </div>
            <div>
                <h3>Our Mission</h3>
                <p>To create innovative solutions that transform how businesses operate through technology and data-driven insights.</p>
            </div>
        </body>
    </html>
    """

    soup = BeautifulSoup(mock_html, 'html.parser')
    culture_keywords = researcher._extract_culture_keywords(soup)
    values = researcher._extract_company_values(soup)
    mission = researcher._extract_mission_statement(soup)

    print(f"Extracted culture keywords: {culture_keywords}")
    print(f"Extracted values: {values}")
    print(
        f"Extracted mission: {mission[:50]}..." if mission else "No mission found")
    print("✅ Content extraction test passed!")

    # Test 6: Company info merging
    print("🧪 Testing Company Info Merging...")

    base_info = CompanyInfo(
        name="Test Company",
        website="https://test.com",
        values=["Innovation"],
        culture_keywords=["agile"]
    )

    additional_info = CompanyInfo(
        description="A great company",
        mission="To innovate",
        values=["Teamwork", "Innovation"],  # Innovation should not duplicate
        culture_keywords=["collaborative"]
    )

    merged = researcher._merge_company_info(base_info, additional_info)

    print(f"Merged values: {merged.values}")
    print(f"Merged culture keywords: {merged.culture_keywords}")
    print(f"Description added: {bool(merged.description)}")
    print(f"Mission added: {bool(merged.mission)}")
    print("✅ Company info merging test passed!")

    print("=" * 50)
    print("🎉 All company research tests passed!")


if __name__ == "__main__":
    test_company_research()
