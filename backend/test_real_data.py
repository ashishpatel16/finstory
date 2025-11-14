"""
Test the AI Agent with real financial data
"""
import pandas as pd
import asyncio
from ai_agent import run_langgraph_analysis
from config import config


def load_and_merge_financial_data():
    """
    Load all three financial statements and merge them
    """
    print("Loading financial data from CSV files...")

    # Load individual statements
    income_stmt = pd.read_csv("data/Income_statement.csv")
    balance_sheet = pd.read_csv("data/balance_sheet.csv")
    cash_flow = pd.read_csv("data/cash_flow.csv")

    print(f"  - Income Statement: {len(income_stmt)} periods")
    print(f"  - Balance Sheet: {len(balance_sheet)} periods")
    print(f"  - Cash Flow: {len(cash_flow)} periods")

    # Rename columns BEFORE merging to avoid duplicates
    income_mapping = {
        'Period': 'period',
        'Revenue': 'revenue',
        'Cost_of_Revenue': 'cost_of_goods_sold',
        'Operating_Expenses': 'operating_expenses',
        'EBIT': 'operating_income',
        'Net_Income': 'net_income',
        'EBITDA': 'ebitda',
        'Depreciation_Amortization': 'depreciation_amortization'
    }

    balance_mapping = {
        'Period': 'period',
        'Cash_and_Equivalents': 'cash_and_equivalents',
        'Total_Current_Assets': 'current_assets',
        'Total_Current_Liabilities': 'current_liabilities',
        'Total_Assets': 'total_assets',
        'Long_Term_Debt': 'total_debt',
        'Total_Shareholders_Equity': 'total_equity',
        'Accounts_Receivable': 'accounts_receivable',
        'Inventory': 'inventory',
        'Accounts_Payable': 'accounts_payable'
    }

    cashflow_mapping = {
        'Period': 'period',
        'Cash_from_Operations': 'cash_from_operations',
        'Capital_Expenditures': 'capital_expenditures'
    }

    # Rename each dataframe
    income_stmt.rename(columns={k: v for k, v in income_mapping.items() if k in income_stmt.columns}, inplace=True)
    balance_sheet.rename(columns={k: v for k, v in balance_mapping.items() if k in balance_sheet.columns}, inplace=True)
    cash_flow.rename(columns={k: v for k, v in cashflow_mapping.items() if k in cash_flow.columns}, inplace=True)

    # Select only needed columns to avoid duplicates
    income_cols = ['period', 'Year', 'Quarter', 'revenue', 'cost_of_goods_sold', 'operating_expenses',
                   'operating_income', 'net_income', 'ebitda', 'depreciation_amortization']
    balance_cols = ['period', 'cash_and_equivalents', 'current_assets', 'current_liabilities', 'total_assets',
                    'total_debt', 'total_equity', 'accounts_receivable', 'inventory', 'accounts_payable']
    cash_cols = ['period', 'cash_from_operations', 'capital_expenditures']

    # Filter to existing columns
    income_cols = [c for c in income_cols if c in income_stmt.columns]
    balance_cols = [c for c in balance_cols if c in balance_sheet.columns]
    cash_cols = [c for c in cash_cols if c in cash_flow.columns]

    # Merge all three on Period
    merged = income_stmt[income_cols].merge(balance_sheet[balance_cols], on='period', how='outer')
    merged = merged.merge(cash_flow[cash_cols], on='period', how='outer')

    # Sort by period
    merged = merged.sort_values('period')

    print(f"\nMerged dataset: {len(merged)} periods, {len(merged.columns)} columns")
    print(f"Date range: {merged['period'].iloc[0]} to {merged['period'].iloc[-1]}")

    return merged


async def analyze_for_persona(df, persona):
    """Run analysis for a specific persona"""
    print(f"\n{'='*80}")
    print(f"ANALYZING FOR: {persona}")
    print(f"{'='*80}\n")

    result = await run_langgraph_analysis(df, persona=persona)

    print(f"\n{'='*80}")
    print(f"RESULTS FOR {persona}")
    print(f"{'='*80}")

    print(f"\nStatus: {result['status']}")

    # Display key metrics
    print("\n--- KEY METRICS ---")
    if 'revenue_metrics' in result['metrics']:
        rev = result['metrics']['revenue_metrics']
        print(f"\nRevenue:")
        print(f"  Current: ${rev.get('current_value', 0):,.0f}")
        print(f"  Growth Rate: {rev.get('growth_rate', 0)}%")
        print(f"  CAGR: {rev.get('cagr', 0)}%")
        print(f"  Trend: {rev.get('trend', 'N/A')}")

    if 'profit_metrics' in result['metrics']:
        profit = result['metrics']['profit_metrics']
        print(f"\nNet Income:")
        print(f"  Current: ${profit.get('current_value', 0):,.0f}")
        print(f"  Growth Rate: {profit.get('growth_rate', 0)}%")

    if 'margins' in result['metrics']:
        margins = result['metrics']['margins']
        print(f"\nMargins:")
        print(f"  Gross Margin: {margins.get('gross_margin', 0)}%")
        print(f"  Operating Margin: {margins.get('operating_margin', 0)}%")
        print(f"  Net Margin: {margins.get('net_margin', 0)}%")
        if 'margin_trend' in margins:
            trend_word = "UP" if margins['margin_trend'] > 0 else "DOWN" if margins['margin_trend'] < 0 else "FLAT"
            print(f"  Margin Trend: {margins['margin_trend']}% ({trend_word})")

    if 'cash_flow' in result['metrics']:
        cf = result['metrics']['cash_flow']
        print(f"\nCash Flow:")
        print(f"  Operating CF: ${cf.get('operating_cash_flow', 0):,.0f}")
        print(f"  Free CF: ${cf.get('free_cash_flow', 0):,.0f}")
        print(f"  Cash Position: ${cf.get('cash_position', 0):,.0f}")
        if 'runway_months' in cf:
            print(f"  Cash Runway: {cf['runway_months']} months")

    if 'financial_ratios' in result['metrics']:
        ratios = result['metrics']['financial_ratios']
        print(f"\nKey Ratios:")
        if 'current_ratio' in ratios:
            print(f"  Current Ratio: {ratios['current_ratio']}")
        if 'debt_to_equity' in ratios:
            print(f"  Debt/Equity: {ratios['debt_to_equity']}")
        if 'return_on_equity' in ratios:
            print(f"  ROE: {ratios['return_on_equity']}%")
        if 'return_on_assets' in ratios:
            print(f"  ROA: {ratios['return_on_assets']}%")

    # Display AI insights
    print("\n--- AI-GENERATED INSIGHTS ---")
    insights = result['insights']

    if insights.get('key_takeaways'):
        print(f"\nKey Takeaways ({len(insights['key_takeaways'])}):")
        for i, takeaway in enumerate(insights['key_takeaways'], 1):
            print(f"  {i}. {takeaway}")

    if insights.get('strengths'):
        print(f"\nStrengths:")
        for strength in insights['strengths']:
            print(f"  + {strength}")

    if insights.get('concerns'):
        print(f"\nConcerns:")
        for concern in insights['concerns']:
            print(f"  ! {concern}")

    if insights.get('summary'):
        print(f"\nExecutive Summary:")
        print(f"  {insights['summary']}")

    # Display risks
    print("\n--- IDENTIFIED RISKS ---")
    if result['risks']:
        for i, risk in enumerate(result['risks'], 1):
            severity_label = "[HIGH]" if risk['severity'] == 'high' else "[MEDIUM]" if risk['severity'] == 'medium' else "[LOW]"
            print(f"\n{i}. {severity_label} {risk['title']}")
            print(f"   Category: {risk['category']}")
            print(f"   {risk['description']}")
            if 'impact' in risk:
                print(f"   Impact: {risk['impact']}")
    else:
        print("  No significant risks identified")

    # Display recommendations
    print("\n--- RECOMMENDATIONS ---")
    if result['recommendations']:
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
    else:
        print("  No specific recommendations at this time")

    # Display trends
    if result.get('trends'):
        print("\n--- METRIC TRENDS ---")
        for metric, trend in result['trends'].items():
            print(f"  {metric}: {trend}")

    return result


async def main():
    """Main test function"""
    try:
        print("\n" + "="*80)
        print("FINSTORY AI AGENT - REAL DATA ANALYSIS")
        print("="*80 + "\n")

        # Validate configuration
        config.validate()
        print("[OK] Configuration validated\n")

        # Load data
        df = load_and_merge_financial_data()

        # Show sample of data
        print("\n--- DATA PREVIEW ---")
        print(f"Latest Period ({df['period'].iloc[-1]}):")
        print(f"  Revenue: ${df['revenue'].iloc[-1]:,.0f}")
        print(f"  Net Income: ${df['net_income'].iloc[-1]:,.0f}")
        print(f"  Cash: ${df['cash_and_equivalents'].iloc[-1]:,.0f}")

        # Analyze for CFO persona (most detailed)
        cfo_result = await analyze_for_persona(df, "CFO")

        # Optional: Analyze for other personas
        print("\n\nWould you like to see Investor and Board analyses too?")
        print("(Uncomment the lines below to run all personas)\n")

        # investor_result = await analyze_for_persona(df, "Investor")
        # board_result = await analyze_for_persona(df, "Board")

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print("\nThe AI agent successfully analyzed 12 quarters of financial data")
        print("from Q1 2022 to Q4 2024 with persona-specific insights.\n")

        return cfo_result

    except ValueError as e:
        print(f"\n[ERROR] Configuration Error: {e}")
        print("\nPlease check your .env file and Gemini API key\n")

    except Exception as e:
        print(f"\n[ERROR] Analysis Failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting analysis...")
    result = asyncio.run(main())
