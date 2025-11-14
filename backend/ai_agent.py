"""
LangGraph AI Agent for Financial Analysis
Complete workflow implementation with OpenAI and Gemini support
"""
import pandas as pd
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END

from config import config
from financial_calculations import calculate_all_metrics, identify_metric_trends
from prompts import (
    create_persona_prompt,
    create_risk_analysis_prompt,
    format_metrics_for_prompt
)
from ai_utils import (
    parse_insights,
    identify_risks,
    generate_recommendations,
    parse_risk_response
)
from charts import generate_all_charts


def get_ai_model():
    """Get the configured AI model (OpenAI or Gemini)"""
    if config.AI_PROVIDER == "openai":
        from openai import OpenAI
        return OpenAI(api_key=config.OPENAI_API_KEY)
    elif config.AI_PROVIDER == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        return genai.GenerativeModel(config.GEMINI_MODEL)
    else:
        raise ValueError(f"Unsupported AI provider: {config.AI_PROVIDER}")


def generate_ai_response(prompt: str) -> str:
    """Generate AI response using configured provider"""
    if config.AI_PROVIDER == "openai":
        client = get_ai_model()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert financial analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content

    elif config.AI_PROVIDER == "gemini":
        model = get_ai_model()
        response = model.generate_content(prompt)
        return response.text

    else:
        raise ValueError(f"Unsupported AI provider: {config.AI_PROVIDER}")


class FinancialAnalysisState(TypedDict):
    """State object for LangGraph workflow"""
    financial_data: pd.DataFrame
    persona: str
    metrics: Dict[str, Any]
    insights: Dict[str, Any]
    risks: List[Dict[str, Any]]
    charts_data: Dict[str, Any]
    recommendations: List[str]
    trends: Dict[str, str]
    error: str


def calculate_metrics_node(state: FinancialAnalysisState) -> FinancialAnalysisState:
    """
    Node 1: Calculate all financial metrics from raw data

    Args:
        state: Current workflow state

    Returns:
        Updated state with calculated metrics
    """
    try:
        df = state["financial_data"]

        # Calculate comprehensive metrics
        metrics = calculate_all_metrics(df)

        # Identify trends
        trends = identify_metric_trends(df)

        state["metrics"] = metrics
        state["trends"] = trends

        print(f"[OK] Calculated {len(metrics)} metric categories")

    except Exception as e:
        state["error"] = f"Metrics calculation failed: {str(e)}"
        print(f"[ERROR] Error in metrics calculation: {str(e)}")

    return state


def generate_insights_node(state: FinancialAnalysisState) -> FinancialAnalysisState:
    """
    Node 2: Generate AI-powered insights using OpenAI or Gemini

    Args:
        state: Current workflow state

    Returns:
        Updated state with generated insights
    """
    try:
        metrics = state["metrics"]
        persona = state["persona"]

        # Create persona-specific prompt
        prompt = create_persona_prompt(metrics, persona)

        # Query AI model
        response_text = generate_ai_response(prompt)

        # Parse insights from response
        insights = parse_insights(response_text)

        state["insights"] = insights

        print(f"[OK] Generated {len(insights.get('key_takeaways', []))} key takeaways for {persona}")

    except Exception as e:
        state["error"] = f"Insight generation failed: {str(e)}"
        print(f"[ERROR] Error in insight generation: {str(e)}")

        # Fallback insights
        state["insights"] = {
            "key_takeaways": ["Unable to generate AI insights"],
            "strengths": [],
            "concerns": [],
            "recommendations": [],
            "summary": "Analysis pending due to AI service error"
        }

    return state


def identify_risks_node(state: FinancialAnalysisState) -> FinancialAnalysisState:
    """
    Node 3: Identify financial risks using rule-based and AI analysis

    Args:
        state: Current workflow state

    Returns:
        Updated state with identified risks
    """
    try:
        metrics = state["metrics"]

        # Rule-based risk identification
        rule_based_risks = identify_risks(metrics)

        # AI-powered risk analysis
        ai_risks = []
        try:
            risk_prompt = create_risk_analysis_prompt(metrics)
            response_text = generate_ai_response(risk_prompt)
            ai_risks = parse_risk_response(response_text)
        except Exception as e:
            print(f"Warning: AI risk analysis failed: {str(e)}")

        # Combine and deduplicate risks
        all_risks = rule_based_risks + ai_risks

        # Remove duplicates based on title
        seen_titles = set()
        unique_risks = []
        for risk in all_risks:
            if risk.get("title") not in seen_titles:
                unique_risks.append(risk)
                seen_titles.add(risk.get("title"))

        state["risks"] = unique_risks

        print(f"[OK] Identified {len(unique_risks)} potential risks")

    except Exception as e:
        state["error"] = f"Risk identification failed: {str(e)}"
        print(f"[ERROR] Error in risk identification: {str(e)}")
        state["risks"] = []

    return state


def create_charts_node(state: FinancialAnalysisState) -> FinancialAnalysisState:
    """
    Node 4: Generate chart data for visualizations

    Args:
        state: Current workflow state

    Returns:
        Updated state with chart data
    """
    try:
        df = state["financial_data"]

        # Generate all chart data
        charts_data = generate_all_charts(df)

        state["charts_data"] = charts_data

        chart_count = len([k for k, v in charts_data.items() if "error" not in v])
        print(f"[OK] Generated {chart_count} chart datasets")

    except Exception as e:
        state["error"] = f"Chart generation failed: {str(e)}"
        print(f"[ERROR] Error in chart generation: {str(e)}")
        state["charts_data"] = {}

    return state


def generate_recommendations_node(state: FinancialAnalysisState) -> FinancialAnalysisState:
    """
    Node 5: Generate actionable recommendations

    Args:
        state: Current workflow state

    Returns:
        Updated state with recommendations
    """
    try:
        metrics = state["metrics"]
        risks = state["risks"]
        persona = state["persona"]

        # Generate recommendations
        recommendations = generate_recommendations(metrics, risks, persona)

        # Also include recommendations from insights if available
        insight_recommendations = state.get("insights", {}).get("recommendations", [])
        if insight_recommendations:
            # Combine and limit to top recommendations
            all_recommendations = recommendations + insight_recommendations
            # Remove duplicates while preserving order
            seen = set()
            unique_recommendations = []
            for rec in all_recommendations:
                rec_lower = rec.lower()
                if rec_lower not in seen:
                    unique_recommendations.append(rec)
                    seen.add(rec_lower)

            recommendations = unique_recommendations[:7]  # Top 7 recommendations

        state["recommendations"] = recommendations

        print(f"[OK] Generated {len(recommendations)} recommendations")

    except Exception as e:
        state["error"] = f"Recommendation generation failed: {str(e)}"
        print(f"[ERROR] Error in recommendation generation: {str(e)}")
        state["recommendations"] = []

    return state


def build_workflow() -> StateGraph:
    """
    Build the LangGraph workflow

    Returns:
        Compiled workflow
    """
    # Create workflow graph
    workflow = StateGraph(FinancialAnalysisState)

    # Add nodes
    workflow.add_node("calculate_metrics", calculate_metrics_node)
    workflow.add_node("generate_insights", generate_insights_node)
    workflow.add_node("identify_risks", identify_risks_node)
    workflow.add_node("create_charts", create_charts_node)
    workflow.add_node("generate_recommendations", generate_recommendations_node)

    # Define workflow edges
    workflow.set_entry_point("calculate_metrics")
    workflow.add_edge("calculate_metrics", "generate_insights")
    workflow.add_edge("generate_insights", "identify_risks")
    workflow.add_edge("identify_risks", "create_charts")
    workflow.add_edge("create_charts", "generate_recommendations")
    workflow.add_edge("generate_recommendations", END)

    return workflow.compile()


async def run_langgraph_analysis(
    financial_data: pd.DataFrame,
    persona: str = "CFO"
) -> Dict[str, Any]:
    """
    Run the complete LangGraph financial analysis workflow

    Args:
        financial_data: DataFrame with financial data
        persona: Target persona (CFO, Investor, Board)

    Returns:
        Complete analysis results
    """
    try:
        # Validate persona
        if persona not in config.PERSONAS:
            persona = "CFO"
            print(f"Warning: Invalid persona, defaulting to CFO")

        # Validate API key based on provider
        config.validate()

        print(f"\n{'='*60}")
        print(f"Starting Financial Analysis for {persona}")
        print(f"{'='*60}\n")

        # Build workflow
        app = build_workflow()

        # Initialize state
        initial_state = {
            "financial_data": financial_data,
            "persona": persona,
            "metrics": {},
            "insights": {},
            "risks": [],
            "charts_data": {},
            "recommendations": [],
            "trends": {},
            "error": ""
        }

        # Run workflow
        result = await app.ainvoke(initial_state)

        print(f"\n{'='*60}")
        print("Analysis Complete!")
        print(f"{'='*60}\n")

        # Format response
        return {
            "status": "success" if not result.get("error") else "partial",
            "persona": persona,
            "metrics": result["metrics"],
            "insights": result["insights"],
            "risks": result["risks"],
            "charts_data": result["charts_data"],
            "recommendations": result["recommendations"],
            "trends": result["trends"],
            "error": result.get("error", "")
        }

    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {str(e)}\n")
        return {
            "status": "error",
            "error": str(e),
            "persona": persona,
            "metrics": {},
            "insights": {},
            "risks": [],
            "charts_data": {},
            "recommendations": []
        }


def run_langgraph_analysis_sync(
    financial_data: pd.DataFrame,
    persona: str = "CFO"
) -> Dict[str, Any]:
    """
    Synchronous version of the workflow (for non-async environments)

    Args:
        financial_data: DataFrame with financial data
        persona: Target persona

    Returns:
        Complete analysis results
    """
    import asyncio

    try:
        # Run async function in sync context
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(
        run_langgraph_analysis(financial_data, persona)
    )
