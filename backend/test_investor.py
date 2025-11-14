"""
Quick test for Investor persona analysis
"""
import pandas as pd
import asyncio
from test_real_data import load_and_merge_financial_data, analyze_for_persona


async def main():
    """Run investor analysis"""
    print("\n" + "="*80)
    print("INVESTOR PERSONA ANALYSIS")
    print("="*80 + "\n")

    # Load data
    df = load_and_merge_financial_data()

    # Analyze for Investor
    result = await analyze_for_persona(df, "Investor")

    return result


if __name__ == "__main__":
    result = asyncio.run(main())
