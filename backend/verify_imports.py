"""
Quick verification script to check all imports work correctly
"""

print("Testing imports...")

try:
    print("[OK] Importing config...")
    from config import config

    print("[OK] Importing financial_calculations...")
    from financial_calculations import (
        calculate_growth,
        calculate_margin,
        calculate_cash_flow,
        calculate_financial_ratios,
        calculate_all_metrics
    )

    print("[OK] Importing prompts...")
    from prompts import (
        create_persona_prompt,
        create_risk_analysis_prompt,
        format_metrics_for_prompt
    )

    print("[OK] Importing ai_utils...")
    from ai_utils import (
        parse_insights,
        identify_risks,
        generate_recommendations
    )

    print("[OK] Importing charts...")
    from charts import generate_all_charts

    print("[OK] Importing ai_agent...")
    from ai_agent import run_langgraph_analysis

    print("\n" + "="*60)
    print("SUCCESS! All modules imported correctly.")
    print("="*60)
    print("\nNext steps:")
    print("1. Copy .env.example to .env")
    print("2. Add your GEMINI_API_KEY to .env")
    print("3. Run: python test_agent.py")
    print("\nGet your Gemini API key from:")
    print("https://makersuite.google.com/app/apikey")

except ImportError as e:
    print(f"\n[ERROR] Import Error: {e}")
    print("\nPlease run: pip install -r requirements.txt")

except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
