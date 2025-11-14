"""
Persona-specific prompt templates for AI-powered financial analysis
"""
from typing import Dict, Any


def create_persona_prompt(metrics: Dict[str, Any], persona: str) -> str:
    """
    Create a persona-specific prompt for financial analysis

    Args:
        metrics: Dictionary of calculated financial metrics
        persona: Target persona (CFO, Investor, Board)

    Returns:
        Formatted prompt string for Gemini
    """

    # Base context about the financial data
    base_context = f"""
You are an expert financial analyst providing insights for a {persona}.

Financial Metrics Summary:
{format_metrics_for_prompt(metrics)}

Based on these financial metrics, provide a comprehensive analysis.
"""

    # Persona-specific instructions
    persona_instructions = {
        "CFO": """
As a CFO-focused analyst, prioritize:
1. Operational efficiency and cost management
2. Cash flow optimization and working capital management
3. Short-term financial health and liquidity
4. Budget variances and expense control
5. Internal process improvements

Provide insights that help with:
- Day-to-day financial operations
- Cost reduction opportunities
- Cash flow management strategies
- Operational KPI improvements
- Risk mitigation for immediate concerns
""",
        "Investor": """
As an investor-focused analyst, prioritize:
1. Revenue growth and market expansion
2. Profitability and return on investment
3. Competitive positioning and market share
4. Growth potential and scalability
5. Valuation metrics and investment returns

Provide insights that help with:
- Investment decision-making
- Growth opportunities and potential
- Return expectations and projections
- Competitive advantages
- Long-term value creation
""",
        "Board": """
As a board-focused analyst, prioritize:
1. Strategic direction and long-term sustainability
2. Governance and risk management
3. Stakeholder value and ESG considerations
4. Major strategic initiatives and their impact
5. Overall company performance against strategic goals

Provide insights that help with:
- Strategic planning and direction
- Risk oversight and governance
- Stakeholder communication
- Major strategic decisions
- Long-term sustainability and growth
"""
    }

    instructions = persona_instructions.get(persona, persona_instructions["CFO"])

    # Output format requirements
    output_format = """
Provide your analysis in the following JSON-parseable format:

{
    "key_takeaways": [
        "3-5 most important insights tailored to this persona",
        "Focus on actionable and strategic insights",
        "Be specific with numbers and percentages"
    ],
    "strengths": [
        "2-3 key financial strengths",
        "Areas of strong performance"
    ],
    "concerns": [
        "2-3 areas of concern or risk",
        "Potential problems to address"
    ],
    "recommendations": [
        "3-5 specific, actionable recommendations",
        "Prioritized by impact and urgency"
    ],
    "summary": "A concise 2-3 sentence executive summary focusing on what matters most to this persona"
}

Important:
- Be specific with numbers and metrics
- Tailor language and focus to the persona
- Prioritize insights by relevance to this persona
- Make recommendations actionable and practical
- Use professional but clear language
"""

    return base_context + instructions + output_format


def format_metrics_for_prompt(metrics: Dict[str, Any]) -> str:
    """
    Format metrics dictionary into a readable string for prompts

    Args:
        metrics: Dictionary of financial metrics

    Returns:
        Formatted string representation
    """
    lines = []

    # Revenue metrics
    if "revenue_metrics" in metrics:
        rev = metrics["revenue_metrics"]
        lines.append("REVENUE METRICS:")
        if "current_value" in rev:
            lines.append(f"  - Current Revenue: ${rev['current_value']:,.2f}")
        if "growth_rate" in rev:
            lines.append(f"  - Growth Rate: {rev['growth_rate']}%")
        if "cagr" in rev and rev["cagr"]:
            lines.append(f"  - CAGR: {rev['cagr']}%")
        if "trend" in rev:
            lines.append(f"  - Trend: {rev['trend']}")
        lines.append("")

    # Profit metrics
    if "profit_metrics" in metrics:
        profit = metrics["profit_metrics"]
        lines.append("PROFIT METRICS:")
        if "current_value" in profit:
            lines.append(f"  - Net Income: ${profit['current_value']:,.2f}")
        if "growth_rate" in profit:
            lines.append(f"  - Profit Growth: {profit['growth_rate']}%")
        lines.append("")

    # Margins
    if "margins" in metrics:
        margins = metrics["margins"]
        lines.append("MARGINS:")
        if "gross_margin" in margins:
            lines.append(f"  - Gross Margin: {margins['gross_margin']}%")
        if "operating_margin" in margins:
            lines.append(f"  - Operating Margin: {margins['operating_margin']}%")
        if "net_margin" in margins:
            lines.append(f"  - Net Margin: {margins['net_margin']}%")
        if "margin_trend" in margins:
            lines.append(f"  - Margin Change: {margins['margin_trend']}%")
        lines.append("")

    # Cash flow
    if "cash_flow" in metrics:
        cf = metrics["cash_flow"]
        lines.append("CASH FLOW:")
        if "operating_cash_flow" in cf:
            lines.append(f"  - Operating Cash Flow: ${cf['operating_cash_flow']:,.2f}")
        if "free_cash_flow" in cf:
            lines.append(f"  - Free Cash Flow: ${cf['free_cash_flow']:,.2f}")
        if "cash_position" in cf:
            lines.append(f"  - Cash Position: ${cf['cash_position']:,.2f}")
        if "runway_months" in cf:
            lines.append(f"  - Cash Runway: {cf['runway_months']} months")
        lines.append("")

    # Financial ratios
    if "financial_ratios" in metrics:
        ratios = metrics["financial_ratios"]
        lines.append("KEY RATIOS:")
        if "current_ratio" in ratios:
            lines.append(f"  - Current Ratio: {ratios['current_ratio']}")
        if "quick_ratio" in ratios:
            lines.append(f"  - Quick Ratio: {ratios['quick_ratio']}")
        if "debt_to_equity" in ratios:
            lines.append(f"  - Debt to Equity: {ratios['debt_to_equity']}")
        if "return_on_equity" in ratios:
            lines.append(f"  - Return on Equity: {ratios['return_on_equity']}%")
        if "return_on_assets" in ratios:
            lines.append(f"  - Return on Assets: {ratios['return_on_assets']}%")
        lines.append("")

    return "\n".join(lines)


def create_risk_analysis_prompt(metrics: Dict[str, Any]) -> str:
    """
    Create a prompt specifically for risk identification

    Args:
        metrics: Dictionary of financial metrics

    Returns:
        Prompt for risk analysis
    """
    return f"""
You are a risk analysis expert. Analyze the following financial metrics and identify potential risks:

{format_metrics_for_prompt(metrics)}

Identify and categorize risks in the following JSON format:

{{
    "risks": [
        {{
            "category": "liquidity|profitability|growth|operational|market",
            "severity": "high|medium|low",
            "title": "Brief risk title",
            "description": "Detailed description of the risk",
            "indicators": ["Specific metrics that indicate this risk"],
            "impact": "Potential impact if not addressed",
            "mitigation": "Suggested mitigation strategies"
        }}
    ]
}}

Focus on:
1. Declining trends in key metrics
2. Ratio values outside healthy ranges
3. Cash flow concerns
4. Profitability issues
5. Sustainability risks

Be specific and data-driven. Only identify genuine risks based on the metrics provided.
"""


def create_comparison_prompt(metrics1: Dict[str, Any], metrics2: Dict[str, Any],
                            period1: str, period2: str) -> str:
    """
    Create a prompt for comparing two periods

    Args:
        metrics1: Metrics for period 1
        metrics2: Metrics for period 2
        period1: Name of first period
        period2: Name of second period

    Returns:
        Comparison analysis prompt
    """
    return f"""
You are a financial analyst comparing two time periods: {period1} vs {period2}.

{period1} Metrics:
{format_metrics_for_prompt(metrics1)}

{period2} Metrics:
{format_metrics_for_prompt(metrics2)}

Provide a detailed comparison analysis in JSON format:

{{
    "key_changes": [
        "Most significant changes between periods"
    ],
    "improvements": [
        "Areas showing positive movement"
    ],
    "deteriorations": [
        "Areas showing negative movement"
    ],
    "drivers": [
        "Key factors driving the changes"
    ],
    "outlook": "Brief assessment of the trajectory based on these changes"
}}

Be specific with percentage changes and dollar amounts where relevant.
"""


def create_qa_prompt(context: str, question: str, persona: str) -> str:
    """
    Create a prompt for Q&A about financial data

    Args:
        context: Financial data context
        question: User's question
        persona: User persona

    Returns:
        Q&A prompt
    """
    return f"""
You are a financial analyst assistant helping a {persona} understand their financial data.

Financial Context:
{context}

Question: {question}

Provide a clear, accurate answer based on the financial data provided.

Guidelines:
1. Be specific and reference actual numbers from the data
2. Tailor your language and focus to a {persona}'s perspective
3. If the data doesn't contain information to answer the question, say so
4. Provide context and explain financial concepts when helpful
5. Keep the answer concise but comprehensive (2-4 paragraphs)

Answer:
"""
