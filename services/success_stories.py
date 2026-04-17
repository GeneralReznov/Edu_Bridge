"""
Success Stories Service
Provides curated success stories of Indian students who studied abroad.
"""
import random

SUCCESS_STORIES = [
    {
        "id": 1,
        "name": "Priya S.",
        "program": "MS Computer Science",
        "university": "Carnegie Mellon University",
        "country": "USA",
        "year": 2023,
        "profile": {"gpa": "8.9/10", "gre": "329", "work": "2 years at Infosys"},
        "loan": "₹42L from HDFC Credila",
        "job": "SDE at Google, $165K/year",
        "payback_yrs": 2.1,
        "quote": "The Career Navigator showed me CMU's CS program was my best fit. I was skeptical but the AI was right!",
        "tags": ["CS", "USA", "Top 5 university", "Scholarship"],
        "field": "Computer Science / IT",
    },
    {
        "id": 2,
        "name": "Rahul M.",
        "program": "MS Data Science",
        "university": "University of Michigan",
        "country": "USA",
        "year": 2022,
        "profile": {"gpa": "7.8/10", "gre": "317", "work": "1 year at TCS"},
        "loan": "₹38L from SBI Ed-Vantage",
        "job": "Data Scientist at Amazon, $130K/year",
        "payback_yrs": 2.8,
        "quote": "The peer benchmarking showed my GRE was in the top 40% — that motivated me to retake and score 317.",
        "tags": ["Data Science", "USA", "SBI loan"],
        "field": "Data Science / AI / ML",
    },
    {
        "id": 3,
        "name": "Ananya K.",
        "program": "MSc Financial Technology",
        "university": "Imperial College London",
        "country": "UK",
        "year": 2023,
        "profile": {"gpa": "3.7/4.0", "gre": "N/A (GMAT 710)", "work": "3 years at HDFC Bank"},
        "loan": "₹28L from Prodigy Finance",
        "job": "FinTech Analyst at Goldman Sachs London, £85K",
        "payback_yrs": 2.4,
        "quote": "The 1-year UK program was a gamechanger — half the cost and I'm already earning more than I imagined.",
        "tags": ["Finance", "UK", "1-year program", "Prodigy Finance"],
        "field": "Finance / Economics",
    },
    {
        "id": 4,
        "name": "Vikram P.",
        "program": "MS Electrical Engineering",
        "university": "TU Munich (TUM)",
        "country": "Germany",
        "year": 2022,
        "profile": {"gpa": "8.5/10", "gre": "Not required", "work": "Fresher"},
        "loan": "No loan — tuition free",
        "job": "Semiconductor Engineer at Siemens, €65K",
        "payback_yrs": 0.5,
        "quote": "Germany was the best decision — free tuition and world-class research. EduBridge's Germany guide was invaluable.",
        "tags": ["Engineering", "Germany", "Free tuition", "EU Blue Card"],
        "field": "Electrical Engineering",
    },
    {
        "id": 5,
        "name": "Deepa R.",
        "program": "MBA",
        "university": "Rotman School of Management",
        "country": "Canada",
        "year": 2023,
        "profile": {"gpa": "3.5/4.0", "gre": "GMAT 680", "work": "5 years at Wipro"},
        "loan": "₹45L from Avanse",
        "job": "Product Manager at Shopify, CAD 120K",
        "payback_yrs": 3.1,
        "quote": "Canada's PGWP made the PR process so much smoother. I'm now on track for PR in 2025.",
        "tags": ["MBA", "Canada", "PGWP", "PR pathway"],
        "field": "Business Administration (MBA)",
    },
    {
        "id": 6,
        "name": "Arjun T.",
        "program": "MS Artificial Intelligence",
        "university": "University of Toronto",
        "country": "Canada",
        "year": 2023,
        "profile": {"gpa": "9.2/10", "gre": "325", "work": "Fresher"},
        "loan": "₹35L from ICICI Bank",
        "job": "ML Engineer at Cohere, CAD 110K",
        "payback_yrs": 2.6,
        "quote": "The admission predictor gave me 68% probability at UofT — I applied and got in with a $12K scholarship!",
        "tags": ["AI/ML", "Canada", "Scholarship", "Research"],
        "field": "Data Science / AI / ML",
    },
]

def get_stories_for_field(field: str, country: str = None, limit: int = 3) -> list:
    """Return relevant success stories for a field/country."""
    filtered = [s for s in SUCCESS_STORIES if s["field"] == field]
    if not filtered:
        filtered = SUCCESS_STORIES[:]
    if country:
        country_match = [s for s in filtered if s["country"] == country]
        if country_match:
            filtered = country_match

    random.shuffle(filtered)
    return filtered[:limit]

def get_all_stories() -> list:
    return SUCCESS_STORIES
