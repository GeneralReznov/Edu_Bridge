"""
Application Strategy Recommender Service
Generates personalized application strategy using AI + rule engine
"""

def build_strategy_prompt(data: dict) -> str:
    field      = data.get("field", "")
    gpa        = data.get("gpa", "")
    gre        = data.get("gre", "")
    toefl      = data.get("toefl", "")
    work_exp   = data.get("work_exp", "0")
    research   = data.get("research", "none")
    countries  = data.get("countries", "USA")
    budget     = data.get("budget", "₹20-40L")
    career     = data.get("career_goal", "")
    intake     = data.get("intake", "Fall 2025")
    strengths  = data.get("strengths", "")
    weaknesses = data.get("weaknesses", "")

    return f"""You are an expert graduate admissions consultant specializing in Indian students applying abroad.

Student Profile:
- Field: {field}
- GPA/CGPA: {gpa}
- GRE/GMAT: {gre if gre else 'Not taken'}
- TOEFL/IELTS: {toefl if toefl else 'Not taken'}
- Work Experience: {work_exp} years
- Research: {research}
- Target Countries: {countries}
- Budget/Year: {budget}
- Career Goal: {career}
- Target Intake: {intake}
- Self-identified strengths: {strengths if strengths else 'Not specified'}
- Self-identified weaknesses: {weaknesses if weaknesses else 'Not specified'}

Generate a comprehensive, advanced application strategy (valid JSON only, no markdown, no extra text):
{{
  "profile_assessment": {{
    "overall_score": 76,
    "competitive_advantage": "Clear description of what makes this student unique",
    "profile_gaps": ["gap1", "gap2"],
    "positioning_statement": "How this student should position themselves"
  }},
  "university_portfolio": {{
    "reach": [
      {{
        "name": "MIT",
        "country": "USA",
        "accept_rate": "8%",
        "avg_gre": "330",
        "avg_gpa": "3.9",
        "why_apply": "Specific reason for this student",
        "success_probability": 15,
        "scholarship_chance": "Low",
        "application_tip": "Specific tip for this university"
      }}
    ],
    "target": [
      {{
        "name": "University of Michigan",
        "country": "USA",
        "accept_rate": "22%",
        "avg_gre": "322",
        "avg_gpa": "3.6",
        "why_apply": "Specific reason",
        "success_probability": 55,
        "scholarship_chance": "Medium",
        "application_tip": "Specific tip"
      }}
    ],
    "safe": [
      {{
        "name": "Arizona State University",
        "country": "USA",
        "accept_rate": "62%",
        "avg_gre": "308",
        "avg_gpa": "3.2",
        "why_apply": "Good ROI + research opportunities",
        "success_probability": 87,
        "scholarship_chance": "High",
        "application_tip": "Specific tip"
      }}
    ]
  }},
  "sop_strategy": {{
    "core_narrative": "The central story thread for this student",
    "opening_hook": "Compelling opening sentence idea",
    "key_themes": ["theme1", "theme2", "theme3"],
    "what_to_highlight": ["achievement1", "achievement2"],
    "what_to_avoid": ["mistake1", "mistake2"],
    "word_count_target": 950,
    "structure": [
      {{"section": "Opening Hook", "content": "What to write here", "word_count": 100}},
      {{"section": "Academic Journey", "content": "What to cover", "word_count": 200}},
      {{"section": "Professional Experience", "content": "What to cover", "word_count": 200}},
      {{"section": "Research/Projects", "content": "What to cover", "word_count": 200}},
      {{"section": "Why This Program", "content": "What to cover", "word_count": 150}},
      {{"section": "Career Goals", "content": "What to write", "word_count": 100}}
    ]
  }},
  "lor_strategy": {{
    "number_needed": 3,
    "ideal_recommenders": [
      {{"type": "Academic Professor", "priority": "High", "what_to_ask": "Specific traits to emphasize"}},
      {{"type": "Research Supervisor", "priority": "High", "what_to_ask": "Specific traits"}},
      {{"type": "Industry Manager", "priority": "Medium", "what_to_ask": "Specific traits"}}
    ],
    "request_timeline": "6-8 weeks before deadline",
    "briefing_guide": "What to share with recommenders"
  }},
  "timeline": [
    {{"month": "Month 1", "tasks": ["task1", "task2"], "priority": "Critical"}},
    {{"month": "Month 2", "tasks": ["task1", "task2"], "priority": "High"}},
    {{"month": "Month 3", "tasks": ["task1", "task2"], "priority": "High"}},
    {{"month": "Month 4", "tasks": ["task1", "task2"], "priority": "Medium"}},
    {{"month": "Month 5", "tasks": ["task1", "task2"], "priority": "Medium"}},
    {{"month": "Month 6", "tasks": ["task1", "task2"], "priority": "Low"}}
  ],
  "score_improvement_plan": [
    {{"metric": "GRE", "current": "310", "target": "320", "timeline": "3 months", "resources": ["resource1"]}},
    {{"metric": "TOEFL", "current": "100", "target": "110", "timeline": "2 months", "resources": ["resource1"]}}
  ],
  "financial_strategy": {{
    "estimated_total_cost_inr": 4500000,
    "scholarship_targets": ["Merit scholarship at X", "TA/RA positions"],
    "loan_recommendation": "HDFC Credila for fast processing",
    "monthly_savings_needed": 25000
  }},
  "key_differentiators": ["differentiator1", "differentiator2", "differentiator3"],
  "red_flags": ["potential_red_flag1"],
  "success_probability_overall": 68
}}"""
