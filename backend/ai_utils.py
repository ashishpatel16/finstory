"""
AI utility functions for parsing insights and identifying risks
"""
import json
import re
from typing import Dict, List, Any
from config import config


def parse_insights(response_text: str) -> Dict[str, Any]:
    """
    Parse insights from Gemini response text

    Args:
        response_text: Raw text response from Gemini

    Returns:
        Structured dictionary with parsed insights
    """
    try:
        # Try to extract JSON from response
        # Look for JSON block in the response
        json_match = re.search(r'\{[\s\S]*\}', response_text)

        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)

            # Validate and structure the response
            return {
                "key_takeaways": parsed.get("key_takeaways", []),
                "strengths": parsed.get("strengths", []),
                "concerns": parsed.get("concerns", []),
                "recommendations": parsed.get("recommendations", []),
                "summary": parsed.get("summary", "")
            }
        else:
            # Fallback: parse unstructured text
            return parse_unstructured_insights(response_text)

    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract insights from text
        return parse_unstructured_insights(response_text)
    except Exception as e:
        return {
            "error": f"Failed to parse insights: {str(e)}",
            "raw_response": response_text[:500]  # First 500 chars for debugging
        }


def parse_unstructured_insights(text: str) -> Dict[str, Any]:
    """
    Parse insights from unstructured text response

    Args:
        text: Unstructured response text

    Returns:
        Best-effort structured insights
    """
    insights = {
        "key_takeaways": [],
        "strengths": [],
        "concerns": [],
        "recommendations": [],
        "summary": ""
    }

    # Split into lines and look for bullet points or numbered lists
    lines = text.split('\n')

    current_section = None
    for line in lines:
        line = line.strip()

        # Identify sections
        if re.search(r'(key|takeaway|insight)', line, re.IGNORECASE):
            current_section = "key_takeaways"
        elif re.search(r'(strength|positive|good)', line, re.IGNORECASE):
            current_section = "strengths"
        elif re.search(r'(concern|risk|issue|problem|weakness)', line, re.IGNORECASE):
            current_section = "concerns"
        elif re.search(r'(recommend|suggest|action|should)', line, re.IGNORECASE):
            current_section = "recommendations"
        elif re.search(r'(summary|overview|conclusion)', line, re.IGNORECASE):
            current_section = "summary"

        # Extract bullet points or numbered items
        if current_section and current_section != "summary":
            # Match bullet points, numbers, or dashes
            match = re.match(r'^[\-\*\d\.\)]\s*(.+)$', line)
            if match:
                content = match.group(1).strip()
                if content and len(content) > 10:  # Meaningful content
                    insights[current_section].append(content)

        # For summary, accumulate text
        elif current_section == "summary" and line:
            if not re.match(r'^[\-\*\d\.\)]', line):  # Not a bullet point
                insights["summary"] += " " + line

    # Clean up summary
    insights["summary"] = insights["summary"].strip()

    # If we didn't extract much, use first paragraph as summary
    if not insights["summary"] and len(text) > 50:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            insights["summary"] = paragraphs[0][:500]

    return insights


def identify_risks(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identify financial risks based on metrics and thresholds

    Args:
        metrics: Dictionary of calculated financial metrics

    Returns:
        List of identified risks
    """
    risks = []
    thresholds = config.RISK_THRESHOLDS

    # Revenue decline risk
    if "revenue_metrics" in metrics:
        rev = metrics["revenue_metrics"]
        if "growth_rate" in rev and rev["growth_rate"] < thresholds["revenue_decline"]:
            risks.append({
                "category": "growth",
                "severity": "high" if rev["growth_rate"] < -10 else "medium",
                "title": "Revenue Decline",
                "description": f"Revenue is declining at {rev['growth_rate']}% year-over-year",
                "indicators": [f"Revenue growth: {rev['growth_rate']}%"],
                "impact": "Reduced profitability and potential market share loss",
                "metric_value": rev["growth_rate"]
            })

    # Margin compression risk
    if "margins" in metrics:
        margins = metrics["margins"]
        if "margin_trend" in margins and margins["margin_trend"] < thresholds["margin_decline"]:
            risks.append({
                "category": "profitability",
                "severity": "medium",
                "title": "Margin Compression",
                "description": f"Profit margins declining by {margins['margin_trend']}%",
                "indicators": [f"Margin change: {margins['margin_trend']}%"],
                "impact": "Reduced profitability despite revenue performance",
                "metric_value": margins["margin_trend"]
            })

        # Low margin warning
        if "net_margin" in margins and margins["net_margin"] < 5:
            risks.append({
                "category": "profitability",
                "severity": "medium",
                "title": "Low Net Margin",
                "description": f"Net profit margin is only {margins['net_margin']}%",
                "indicators": [f"Net margin: {margins['net_margin']}%"],
                "impact": "Limited buffer for operational challenges or market changes",
                "metric_value": margins["net_margin"]
            })

    # Cash flow risk
    if "cash_flow" in metrics:
        cf = metrics["cash_flow"]

        # Negative operating cash flow
        if "operating_cash_flow" in cf and cf["operating_cash_flow"] < 0:
            risks.append({
                "category": "liquidity",
                "severity": "high",
                "title": "Negative Operating Cash Flow",
                "description": f"Operating cash flow is negative at ${cf['operating_cash_flow']:,.2f}",
                "indicators": ["Negative operating cash flow"],
                "impact": "Company is burning cash from core operations",
                "metric_value": cf["operating_cash_flow"]
            })

        # Low cash runway
        if "runway_months" in cf and cf["runway_months"] < 6:
            risks.append({
                "category": "liquidity",
                "severity": "high",
                "title": "Low Cash Runway",
                "description": f"Only {cf['runway_months']:.1f} months of cash remaining at current burn rate",
                "indicators": [f"Cash runway: {cf['runway_months']:.1f} months"],
                "impact": "Urgent need for funding or profitability improvement",
                "metric_value": cf["runway_months"]
            })

    # Liquidity risk
    if "financial_ratios" in metrics:
        ratios = metrics["financial_ratios"]

        # Low current ratio
        if "current_ratio" in ratios and ratios["current_ratio"] < thresholds["low_liquidity"]:
            risks.append({
                "category": "liquidity",
                "severity": "medium" if ratios["current_ratio"] > 1.0 else "high",
                "title": "Low Liquidity Ratio",
                "description": f"Current ratio of {ratios['current_ratio']} indicates potential liquidity stress",
                "indicators": [f"Current ratio: {ratios['current_ratio']}"],
                "impact": "May struggle to meet short-term obligations",
                "metric_value": ratios["current_ratio"]
            })

        # High leverage
        if "debt_to_equity" in ratios and ratios["debt_to_equity"] > thresholds["debt_ratio_high"]:
            risks.append({
                "category": "leverage",
                "severity": "medium" if ratios["debt_to_equity"] < 1.5 else "high",
                "title": "High Leverage",
                "description": f"Debt-to-equity ratio of {ratios['debt_to_equity']} indicates high leverage",
                "indicators": [f"D/E ratio: {ratios['debt_to_equity']}"],
                "impact": "Increased financial risk and interest burden",
                "metric_value": ratios["debt_to_equity"]
            })

    # Sort risks by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    risks.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return risks


def generate_recommendations(metrics: Dict[str, Any], risks: List[Dict[str, Any]],
                            persona: str) -> List[str]:
    """
    Generate actionable recommendations based on metrics and risks

    Args:
        metrics: Financial metrics
        risks: Identified risks
        persona: Target persona

    Returns:
        List of recommendations
    """
    recommendations = []

    # Risk-based recommendations
    for risk in risks:
        if risk["severity"] == "high":
            if risk["category"] == "liquidity":
                if persona == "CFO":
                    recommendations.append(
                        f"URGENT: {risk['title']} - Implement immediate cash preservation measures "
                        "and explore short-term financing options"
                    )
                elif persona == "Board":
                    recommendations.append(
                        f"Strategic Action Required: {risk['title']} - Review capital structure "
                        "and consider strategic financing options"
                    )

            elif risk["category"] == "growth":
                if persona == "Investor":
                    recommendations.append(
                        f"Growth Concern: {risk['title']} - Assess market position and "
                        "evaluate strategic pivots or new market opportunities"
                    )

    # Performance-based recommendations
    if "margins" in metrics and "net_margin" in metrics["margins"]:
        margin = metrics["margins"]["net_margin"]
        if margin < 10:
            if persona == "CFO":
                recommendations.append(
                    f"Margin Improvement: Current net margin at {margin}% - "
                    "Conduct detailed cost analysis and identify efficiency opportunities"
                )

    # Cash flow recommendations
    if "cash_flow" in metrics:
        cf = metrics["cash_flow"]
        if "free_cash_flow" in cf and cf["free_cash_flow"] < 0:
            if persona == "CFO":
                recommendations.append(
                    "Cash Flow Management: Negative FCF - Review capital expenditures "
                    "and optimize working capital management"
                )

    # Growth recommendations
    if "revenue_metrics" in metrics:
        rev = metrics["revenue_metrics"]
        if "growth_rate" in rev:
            if rev["growth_rate"] < 5 and persona == "Investor":
                recommendations.append(
                    "Growth Strategy: Revenue growth below market expectations - "
                    "Explore new revenue streams and market expansion opportunities"
                )
            elif rev["growth_rate"] > 30 and persona == "CFO":
                recommendations.append(
                    "Scale Infrastructure: High growth rate - Ensure operational "
                    "infrastructure can support continued rapid expansion"
                )

    # Limit to top 5 recommendations
    return recommendations[:5]


def parse_risk_response(response_text: str) -> List[Dict[str, Any]]:
    """
    Parse risk analysis from Gemini response

    Args:
        response_text: Raw response from risk analysis

    Returns:
        List of parsed risks
    """
    try:
        # Try to extract JSON
        json_match = re.search(r'\{[\s\S]*\}', response_text)

        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            return parsed.get("risks", [])
        else:
            return []

    except Exception:
        return []
