"""
Contextual Recommender Service
Generates context-aware content recommendations and university suggestions
based on accumulated session data.
"""

FIELD_PROGRAMS = {
    "Computer Science / IT": {
        "programs": ["MS Computer Science", "MS Software Engineering", "MS AI/ML", "MS Cybersecurity"],
        "top_universities": ["Carnegie Mellon", "MIT", "Stanford", "UIUC", "Georgia Tech"],
        "avg_salary_usd": 115000,
        "growth": "Excellent",
    },
    "Data Science / AI / ML": {
        "programs": ["MS Data Science", "MS Machine Learning", "MS Artificial Intelligence", "MS Statistics"],
        "top_universities": ["CMU", "Columbia", "NYU", "UC San Diego", "Michigan"],
        "avg_salary_usd": 120000,
        "growth": "Excellent",
    },
    "Business Administration (MBA)": {
        "programs": ["MBA", "MBA Finance", "MBA Strategy", "MBA Marketing"],
        "top_universities": ["Harvard", "Wharton", "Booth", "Sloan", "Kellogg"],
        "avg_salary_usd": 130000,
        "growth": "Good",
    },
    "Electrical Engineering": {
        "programs": ["MS Electrical Engineering", "MS VLSI", "MS Embedded Systems", "MS Power Systems"],
        "top_universities": ["MIT", "Stanford", "Caltech", "Georgia Tech", "UIUC"],
        "avg_salary_usd": 105000,
        "growth": "Good",
    },
    "Finance / Economics": {
        "programs": ["MS Finance", "MS Financial Engineering", "MS Quantitative Finance"],
        "top_universities": ["LSE", "MIT Sloan", "Columbia", "Carnegie Mellon", "NYU Stern"],
        "avg_salary_usd": 125000,
        "growth": "Good",
    },
}

COUNTRY_CONTEXT = {
    "USA": {
        "strengths": ["World-class research", "OPT/H1B pathway", "High salaries", "Diverse programs"],
        "challenges": ["High cost of living", "Competitive H1B lottery", "High tuition"],
        "avg_cost_usd_yr": 55000,
        "work_visa": "OPT (1-3 years) + H1B",
        "pr_pathway": "EB-1/EB-2/EB-3 (long wait for Indians)",
        "top_cities": ["Boston", "San Francisco", "New York", "Chicago"],
    },
    "Canada": {
        "strengths": ["Easy PR pathway (PGWP)", "Lower cost vs USA", "Multicultural", "Quality education"],
        "challenges": ["Cold winters", "Lower salaries vs USA", "Competitive job market"],
        "avg_cost_usd_yr": 30000,
        "work_visa": "PGWP (up to 3 years)",
        "pr_pathway": "Express Entry (fastest for Indians)",
        "top_cities": ["Toronto", "Vancouver", "Montreal", "Waterloo"],
    },
    "UK": {
        "strengths": ["1-year programs (cost savings)", "Graduate Route visa (2 yrs)", "Historic universities"],
        "challenges": ["Brexit impact", "Expensive living in London", "Pound exchange rate"],
        "avg_cost_usd_yr": 35000,
        "work_visa": "Graduate Route (2 years)",
        "pr_pathway": "Skilled Worker Visa → ILR (5 years)",
        "top_cities": ["London", "Edinburgh", "Manchester", "Birmingham"],
    },
    "Germany": {
        "strengths": ["Free/low tuition at public universities", "Strong engineering", "EU work permit"],
        "challenges": ["German language (some programs)", "Lower salaries vs USA"],
        "avg_cost_usd_yr": 12000,
        "work_visa": "Job Seeker Visa (18 months) → EU Blue Card",
        "pr_pathway": "Permanent Residence after 3-5 years",
        "top_cities": ["Munich", "Berlin", "Hamburg", "Frankfurt"],
    },
}

def get_contextual_recommendations(field: str, country: str, budget_yr_lakhs: float) -> dict:
    """Generate context-aware program and university recommendations."""
    field_data   = FIELD_PROGRAMS.get(field, FIELD_PROGRAMS["Computer Science / IT"])
    country_data = COUNTRY_CONTEXT.get(country, COUNTRY_CONTEXT["USA"])

    # Budget fit
    cost_usd = country_data["avg_cost_usd_yr"]
    budget_usd = budget_yr_lakhs * 1200  # Approximate INR to USD
    budget_fit = "Comfortable" if budget_usd >= cost_usd * 1.1 else ("Tight" if budget_usd >= cost_usd * 0.7 else "Insufficient")

    return {
        "field": field,
        "recommended_programs": field_data["programs"][:3],
        "top_universities": field_data["top_universities"][:4],
        "avg_salary_usd": field_data["avg_salary_usd"],
        "growth_outlook": field_data["growth"],
        "country_info": country_data,
        "budget_fit": budget_fit,
        "cost_usd_yr": cost_usd,
    }
