"""
Financial calculation functions for FinStory AI Agent
Handles all core financial metrics and analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def calculate_growth(df: pd.DataFrame, column: str, periods: int = 1) -> Dict[str, Any]:
    """
    Calculate growth rate for a specific metric

    Args:
        df: DataFrame with financial data
        column: Column name to calculate growth for (e.g., 'revenue')
        periods: Number of periods to compare (default: 1 for period-over-period)

    Returns:
        Dictionary with growth metrics
    """
    try:
        if column not in df.columns:
            return {"error": f"Column '{column}' not found in data"}

        values = df[column].values

        # Handle case where we have multiple periods
        if len(values) < 2:
            return {
                "current_value": float(values[-1]) if len(values) > 0 else 0,
                "growth_rate": 0,
                "growth_amount": 0,
                "error": "Insufficient data for growth calculation"
            }

        current = values[-1]
        previous = values[-periods-1] if len(values) > periods else values[0]

        # Calculate growth
        if previous != 0:
            growth_rate = ((current - previous) / abs(previous)) * 100
            growth_amount = current - previous
        else:
            growth_rate = 0 if current == 0 else float('inf')
            growth_amount = current

        # Calculate CAGR if we have multiple periods
        cagr = None
        if len(values) >= 2:
            n_periods = len(values) - 1
            if values[0] > 0:
                cagr = (((values[-1] / values[0]) ** (1 / n_periods)) - 1) * 100

        return {
            "current_value": float(current),
            "previous_value": float(previous),
            "growth_rate": round(float(growth_rate), 2),
            "growth_amount": round(float(growth_amount), 2),
            "cagr": round(float(cagr), 2) if cagr is not None else None,
            "trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable"
        }

    except Exception as e:
        return {"error": f"Growth calculation failed: {str(e)}"}


def calculate_margin(df: pd.DataFrame, revenue_col: str = "revenue",
                    cost_col: str = "cost_of_goods_sold") -> Dict[str, Any]:
    """
    Calculate various profit margins

    Args:
        df: DataFrame with financial data
        revenue_col: Revenue column name
        cost_col: Cost column name

    Returns:
        Dictionary with margin metrics
    """
    try:
        margins = {}

        # Gross margin
        if revenue_col in df.columns and cost_col in df.columns:
            latest_revenue = df[revenue_col].iloc[-1]
            latest_cost = df[cost_col].iloc[-1]

            if latest_revenue != 0:
                gross_margin = ((latest_revenue - latest_cost) / latest_revenue) * 100
                margins["gross_margin"] = round(float(gross_margin), 2)
            else:
                margins["gross_margin"] = 0

        # Operating margin
        if "operating_income" in df.columns and revenue_col in df.columns:
            operating_income = df["operating_income"].iloc[-1]
            latest_revenue = df[revenue_col].iloc[-1]

            if latest_revenue != 0:
                operating_margin = (operating_income / latest_revenue) * 100
                margins["operating_margin"] = round(float(operating_margin), 2)

        # Net profit margin
        if "net_income" in df.columns and revenue_col in df.columns:
            net_income = df["net_income"].iloc[-1]
            latest_revenue = df[revenue_col].iloc[-1]

            if latest_revenue != 0:
                net_margin = (net_income / latest_revenue) * 100
                margins["net_margin"] = round(float(net_margin), 2)

        # Calculate margin trends
        if revenue_col in df.columns and cost_col in df.columns and len(df) >= 2:
            prev_revenue = df[revenue_col].iloc[-2]
            prev_cost = df[cost_col].iloc[-2]

            if prev_revenue != 0:
                prev_margin = ((prev_revenue - prev_cost) / prev_revenue) * 100
                current_margin = margins.get("gross_margin", 0)
                margin_change = current_margin - prev_margin
                margins["margin_trend"] = round(float(margin_change), 2)

        return margins

    except Exception as e:
        return {"error": f"Margin calculation failed: {str(e)}"}


def calculate_cash_flow(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate cash flow metrics

    Args:
        df: DataFrame with financial data

    Returns:
        Dictionary with cash flow metrics
    """
    try:
        cash_flow = {}

        # Operating cash flow
        if "cash_from_operations" in df.columns:
            ocf = df["cash_from_operations"].iloc[-1]
            cash_flow["operating_cash_flow"] = round(float(ocf), 2)

            # Calculate average OCF
            if len(df) >= 3:
                avg_ocf = df["cash_from_operations"].tail(3).mean()
                cash_flow["avg_operating_cash_flow"] = round(float(avg_ocf), 2)

        # Free cash flow
        if "cash_from_operations" in df.columns and "capital_expenditures" in df.columns:
            ocf = df["cash_from_operations"].iloc[-1]
            capex = df["capital_expenditures"].iloc[-1]
            fcf = ocf - capex
            cash_flow["free_cash_flow"] = round(float(fcf), 2)

        # Cash conversion cycle (if data available)
        if all(col in df.columns for col in ["accounts_receivable", "inventory", "accounts_payable"]):
            # Simplified CCC calculation
            ar = df["accounts_receivable"].iloc[-1]
            inv = df["inventory"].iloc[-1]
            ap = df["accounts_payable"].iloc[-1]
            revenue = df.get("revenue", pd.Series([1])).iloc[-1]

            if revenue > 0:
                dso = (ar / revenue) * 365  # Days Sales Outstanding
                dio = (inv / revenue) * 365  # Days Inventory Outstanding
                dpo = (ap / revenue) * 365  # Days Payable Outstanding
                ccc = dso + dio - dpo
                cash_flow["cash_conversion_cycle"] = round(float(ccc), 1)

        # Cash position
        if "cash_and_equivalents" in df.columns:
            cash = df["cash_and_equivalents"].iloc[-1]
            cash_flow["cash_position"] = round(float(cash), 2)

            # Calculate cash burn rate if negative OCF
            if "operating_cash_flow" in cash_flow and cash_flow["operating_cash_flow"] < 0:
                monthly_burn = abs(cash_flow["operating_cash_flow"]) / 12
                runway_months = cash / monthly_burn if monthly_burn > 0 else float('inf')
                cash_flow["runway_months"] = round(float(runway_months), 1)

        return cash_flow

    except Exception as e:
        return {"error": f"Cash flow calculation failed: {str(e)}"}


def calculate_financial_ratios(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate key financial ratios

    Args:
        df: DataFrame with financial data

    Returns:
        Dictionary with financial ratios
    """
    try:
        ratios = {}

        # Liquidity ratios
        if "current_assets" in df.columns and "current_liabilities" in df.columns:
            current_assets = df["current_assets"].iloc[-1]
            current_liabilities = df["current_liabilities"].iloc[-1]

            if current_liabilities != 0:
                current_ratio = current_assets / current_liabilities
                ratios["current_ratio"] = round(float(current_ratio), 2)

            # Quick ratio (if inventory data available)
            if "inventory" in df.columns:
                quick_assets = current_assets - df["inventory"].iloc[-1]
                if current_liabilities != 0:
                    quick_ratio = quick_assets / current_liabilities
                    ratios["quick_ratio"] = round(float(quick_ratio), 2)

        # Leverage ratios
        if "total_debt" in df.columns and "total_equity" in df.columns:
            debt = df["total_debt"].iloc[-1]
            equity = df["total_equity"].iloc[-1]

            if equity != 0:
                debt_to_equity = debt / equity
                ratios["debt_to_equity"] = round(float(debt_to_equity), 2)

        # Efficiency ratios
        if "revenue" in df.columns and "total_assets" in df.columns:
            revenue = df["revenue"].iloc[-1]
            assets = df["total_assets"].iloc[-1]

            if assets != 0:
                asset_turnover = revenue / assets
                ratios["asset_turnover"] = round(float(asset_turnover), 2)

        # Profitability ratios
        if "net_income" in df.columns and "total_equity" in df.columns:
            net_income = df["net_income"].iloc[-1]
            equity = df["total_equity"].iloc[-1]

            if equity != 0:
                roe = (net_income / equity) * 100
                ratios["return_on_equity"] = round(float(roe), 2)

        if "net_income" in df.columns and "total_assets" in df.columns:
            net_income = df["net_income"].iloc[-1]
            assets = df["total_assets"].iloc[-1]

            if assets != 0:
                roa = (net_income / assets) * 100
                ratios["return_on_assets"] = round(float(roa), 2)

        return ratios

    except Exception as e:
        return {"error": f"Ratio calculation failed: {str(e)}"}


def calculate_all_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate all financial metrics at once

    Args:
        df: DataFrame with financial data

    Returns:
        Comprehensive dictionary with all metrics
    """
    return {
        "revenue_metrics": calculate_growth(df, "revenue") if "revenue" in df.columns else {},
        "profit_metrics": calculate_growth(df, "net_income") if "net_income" in df.columns else {},
        "margins": calculate_margin(df),
        "cash_flow": calculate_cash_flow(df),
        "financial_ratios": calculate_financial_ratios(df),
        "timestamp": pd.Timestamp.now().isoformat()
    }


def identify_metric_trends(df: pd.DataFrame, window: int = 3) -> Dict[str, str]:
    """
    Identify trends in key metrics over a rolling window

    Args:
        df: DataFrame with financial data
        window: Number of periods to analyze

    Returns:
        Dictionary with trend analysis
    """
    trends = {}

    key_metrics = ["revenue", "net_income", "operating_income", "cash_from_operations"]

    for metric in key_metrics:
        if metric in df.columns and len(df) >= window:
            values = df[metric].tail(window)

            # Calculate trend using linear regression slope
            x = np.arange(len(values))
            y = values.values

            if len(x) > 1:
                slope = np.polyfit(x, y, 1)[0]

                if slope > 0:
                    trends[metric] = "upward"
                elif slope < 0:
                    trends[metric] = "downward"
                else:
                    trends[metric] = "stable"

    return trends
