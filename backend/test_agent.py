"""
Test script for the FinStory AI Agent
Demonstrates the complete workflow with sample financial data
"""
import pandas as pd
import asyncio
from ai_agent import run_langgraph_analysis
from config import config


def create_sample_financial_data() -> pd.DataFrame:
    """
    Create sample financial data for testing

    Returns:
        DataFrame with sample financial data
    """
    data = {
        "period": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
        "revenue": [1000000, 1150000, 1200000, 1100000],
        "cost_of_goods_sold": [600000, 690000, 720000, 700000],
        "operating_income": [250000, 290000, 300000, 260000],
        "net_income": [180000, 210000, 220000, 190000],
        "cash_from_operations": [200000, 230000, 240000, 210000],
        "capital_expenditures": [50000, 60000, 55000, 65000],
        "cash_and_equivalents": [500000, 520000, 545000, 550000],
        "current_assets": [800000, 850000, 900000, 920000],
        "current_liabilities": [400000, 420000, 440000, 460000],
        "total_assets": [2000000, 2100000, 2150000, 2200000],
        "total_debt": [600000, 580000, 560000, 540000],
        "total_equity": [1200000, 1320000, 1390000, 1450000],
        "accounts_receivable": [150000, 160000, 170000, 165000],
        "inventory": [100000, 110000, 115000, 120000],
        "accounts_payable": [80000, 85000, 90000, 95000]
    }

    return pd.DataFrame(data)


async def test_cfo_analysis():
    """Test analysis for CFO persona"""
    print("\n" + "="*80)
    print("TEST 1: CFO Analysis")
    print("="*80)

    df = create_sample_financial_data()
    result = await run_langgraph_analysis(df, persona="CFO")

    print("\n--- RESULTS ---")
    print(f"Status: {result['status']}")
    print(f"\nKey Metrics:")
    if "revenue_metrics" in result["metrics"]:
        rev = result["metrics"]["revenue_metrics"]
        print(f"  Revenue Growth: {rev.get('growth_rate', 'N/A')}%")
    if "margins" in result["metrics"]:
        margins = result["metrics"]["margins"]
        print(f"  Gross Margin: {margins.get('gross_margin', 'N/A')}%")
        print(f"  Net Margin: {margins.get('net_margin', 'N/A')}%")

    print(f"\nKey Takeaways ({len(result['insights'].get('key_takeaways', []))}):")
    for i, takeaway in enumerate(result["insights"].get("key_takeaways", []), 1):
        print(f"  {i}. {takeaway}")

    print(f"\nRisks Identified ({len(result['risks'])}):")
    for risk in result["risks"][:3]:  # Show top 3 risks
        print(f"  - [{risk['severity'].upper()}] {risk['title']}")
        print(f"    {risk['description']}")

    print(f"\nRecommendations ({len(result['recommendations'])}):")
    for i, rec in enumerate(result["recommendations"][:3], 1):  # Show top 3
        print(f"  {i}. {rec}")


async def test_investor_analysis():
    """Test analysis for Investor persona"""
    print("\n" + "="*80)
    print("TEST 2: Investor Analysis")
    print("="*80)

    df = create_sample_financial_data()
    result = await run_langgraph_analysis(df, persona="Investor")

    print("\n--- RESULTS ---")
    print(f"Status: {result['status']}")

    print(f"\nKey Takeaways for Investors:")
    for i, takeaway in enumerate(result["insights"].get("key_takeaways", []), 1):
        print(f"  {i}. {takeaway}")

    print(f"\nSummary:")
    print(f"  {result['insights'].get('summary', 'N/A')}")


async def test_board_analysis():
    """Test analysis for Board persona"""
    print("\n" + "="*80)
    print("TEST 3: Board Analysis")
    print("="*80)

    df = create_sample_financial_data()
    result = await run_langgraph_analysis(df, persona="Board")

    print("\n--- RESULTS ---")
    print(f"Status: {result['status']}")

    print(f"\nStrategic Insights:")
    for i, takeaway in enumerate(result["insights"].get("key_takeaways", []), 1):
        print(f"  {i}. {takeaway}")


def test_financial_calculations():
    """Test individual financial calculation functions"""
    print("\n" + "="*80)
    print("TEST 4: Financial Calculations")
    print("="*80)

    from financial_calculations import (
        calculate_growth,
        calculate_margin,
        calculate_cash_flow,
        calculate_financial_ratios
    )

    df = create_sample_financial_data()

    print("\n--- Revenue Growth ---")
    growth = calculate_growth(df, "revenue")
    print(f"  Current: ${growth.get('current_value', 0):,.0f}")
    print(f"  Growth Rate: {growth.get('growth_rate', 0)}%")
    print(f"  CAGR: {growth.get('cagr', 0)}%")

    print("\n--- Margins ---")
    margins = calculate_margin(df)
    print(f"  Gross Margin: {margins.get('gross_margin', 0)}%")
    print(f"  Net Margin: {margins.get('net_margin', 0)}%")

    print("\n--- Cash Flow ---")
    cf = calculate_cash_flow(df)
    print(f"  Operating Cash Flow: ${cf.get('operating_cash_flow', 0):,.0f}")
    print(f"  Free Cash Flow: ${cf.get('free_cash_flow', 0):,.0f}")
    print(f"  Cash Position: ${cf.get('cash_position', 0):,.0f}")

    print("\n--- Financial Ratios ---")
    ratios = calculate_financial_ratios(df)
    print(f"  Current Ratio: {ratios.get('current_ratio', 0)}")
    print(f"  Debt to Equity: {ratios.get('debt_to_equity', 0)}")
    print(f"  ROE: {ratios.get('return_on_equity', 0)}%")


async def run_all_tests():
    """Run all tests"""
    try:
        # Validate configuration
        config.validate()
        print("[OK] Configuration validated")

        # Test financial calculations (synchronous)
        test_financial_calculations()

        # Test AI agent workflows (asynchronous)
        await test_cfo_analysis()
        await test_investor_analysis()
        await test_board_analysis()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")

    except ValueError as e:
        print(f"\n[ERROR] Configuration Error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Set your GEMINI_API_KEY in the .env file")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey\n")

    except Exception as e:
        print(f"\n[ERROR] Test Failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FinStory AI Agent - Test Suite")
    print("="*80)

    # Run all tests
    asyncio.run(run_all_tests())
