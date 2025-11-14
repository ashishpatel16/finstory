"""
Chart data generation for financial visualizations
Returns data structures ready for frontend charting libraries
"""
import pandas as pd
from typing import Dict, List, Any, Optional


def generate_revenue_chart(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate revenue trend chart data

    Args:
        df: DataFrame with financial data

    Returns:
        Chart data structure
    """
    try:
        if "revenue" not in df.columns:
            return {"error": "Revenue column not found"}

        # Prepare time series data
        labels = []
        values = []

        # Check if there's a period/date column
        period_col = None
        for col in ["period", "date", "quarter", "year"]:
            if col in df.columns:
                period_col = col
                break

        if period_col:
            labels = df[period_col].astype(str).tolist()
        else:
            labels = [f"Period {i+1}" for i in range(len(df))]

        values = df["revenue"].tolist()

        # Calculate growth rates for each period
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                growth = ((values[i] - values[i-1]) / abs(values[i-1])) * 100
                growth_rates.append(round(growth, 2))
            else:
                growth_rates.append(0)

        return {
            "chart_type": "line",
            "title": "Revenue Trend",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Revenue",
                        "data": values,
                        "borderColor": "rgb(75, 192, 192)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "tension": 0.1
                    }
                ]
            },
            "metadata": {
                "growth_rates": growth_rates,
                "total": sum(values),
                "average": sum(values) / len(values) if values else 0,
                "latest": values[-1] if values else 0
            }
        }

    except Exception as e:
        return {"error": f"Revenue chart generation failed: {str(e)}"}


def generate_margin_chart(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate margin analysis chart data

    Args:
        df: DataFrame with financial data

    Returns:
        Chart data structure
    """
    try:
        # Check available margin data
        margin_types = {
            "gross_margin": ("revenue", "cost_of_goods_sold"),
            "operating_margin": ("operating_income", "revenue"),
            "net_margin": ("net_income", "revenue")
        }

        labels = []
        datasets = []

        # Get period labels
        period_col = None
        for col in ["period", "date", "quarter", "year"]:
            if col in df.columns:
                period_col = col
                break

        if period_col:
            labels = df[period_col].astype(str).tolist()
        else:
            labels = [f"Period {i+1}" for i in range(len(df))]

        # Calculate each margin type
        colors = {
            "gross_margin": "rgb(54, 162, 235)",
            "operating_margin": "rgb(255, 159, 64)",
            "net_margin": "rgb(153, 102, 255)"
        }

        for margin_name, (numerator, denominator) in margin_types.items():
            if numerator in df.columns and denominator in df.columns:
                margins = []
                for idx in range(len(df)):
                    denom_val = df[denominator].iloc[idx]
                    if denom_val != 0:
                        if margin_name == "gross_margin":
                            numer_val = df[denominator].iloc[idx] - df[numerator].iloc[idx]
                        else:
                            numer_val = df[numerator].iloc[idx]

                        margin = (numer_val / denom_val) * 100
                        margins.append(round(margin, 2))
                    else:
                        margins.append(0)

                datasets.append({
                    "label": margin_name.replace("_", " ").title(),
                    "data": margins,
                    "borderColor": colors[margin_name],
                    "backgroundColor": f"rgba{colors[margin_name][3:-1]}, 0.2)",
                    "fill": False
                })

        return {
            "chart_type": "line",
            "title": "Margin Analysis",
            "data": {
                "labels": labels,
                "datasets": datasets
            }
        }

    except Exception as e:
        return {"error": f"Margin chart generation failed: {str(e)}"}


def generate_metrics_chart(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate key metrics comparison chart

    Args:
        df: DataFrame with financial data

    Returns:
        Chart data structure for bar chart comparison
    """
    try:
        # Get latest values for key metrics
        metrics = {}

        if "revenue" in df.columns:
            metrics["Revenue"] = float(df["revenue"].iloc[-1])

        if "net_income" in df.columns:
            metrics["Net Income"] = float(df["net_income"].iloc[-1])

        if "operating_income" in df.columns:
            metrics["Operating Income"] = float(df["operating_income"].iloc[-1])

        if "cash_from_operations" in df.columns:
            metrics["Operating Cash Flow"] = float(df["cash_from_operations"].iloc[-1])

        if "free_cash_flow" in df.columns:
            metrics["Free Cash Flow"] = float(df["free_cash_flow"].iloc[-1])
        elif "cash_from_operations" in df.columns and "capital_expenditures" in df.columns:
            fcf = df["cash_from_operations"].iloc[-1] - df["capital_expenditures"].iloc[-1]
            metrics["Free Cash Flow"] = float(fcf)

        labels = list(metrics.keys())
        values = list(metrics.values())

        # Determine colors based on positive/negative values
        colors = ["rgb(75, 192, 192)" if v >= 0 else "rgb(255, 99, 132)" for v in values]

        return {
            "chart_type": "bar",
            "title": "Key Financial Metrics",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Current Period",
                    "data": values,
                    "backgroundColor": colors
                }]
            }
        }

    except Exception as e:
        return {"error": f"Metrics chart generation failed: {str(e)}"}


def generate_cash_flow_waterfall(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate cash flow waterfall chart data

    Args:
        df: DataFrame with financial data

    Returns:
        Waterfall chart data structure
    """
    try:
        # Get latest period cash flow components
        components = []

        if "cash_from_operations" in df.columns:
            components.append({
                "label": "Operating Activities",
                "value": float(df["cash_from_operations"].iloc[-1])
            })

        if "cash_from_investing" in df.columns:
            components.append({
                "label": "Investing Activities",
                "value": float(df["cash_from_investing"].iloc[-1])
            })

        if "cash_from_financing" in df.columns:
            components.append({
                "label": "Financing Activities",
                "value": float(df["cash_from_financing"].iloc[-1])
            })

        # Calculate cumulative values for waterfall
        cumulative = 0
        waterfall_data = []

        for comp in components:
            start = cumulative
            cumulative += comp["value"]
            waterfall_data.append({
                "label": comp["label"],
                "value": comp["value"],
                "start": start,
                "end": cumulative,
                "color": "rgb(75, 192, 192)" if comp["value"] >= 0 else "rgb(255, 99, 132)"
            })

        return {
            "chart_type": "waterfall",
            "title": "Cash Flow Breakdown",
            "data": waterfall_data,
            "net_change": cumulative
        }

    except Exception as e:
        return {"error": f"Cash flow waterfall generation failed: {str(e)}"}


def generate_ratio_gauge(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate gauge charts for key financial ratios

    Args:
        df: DataFrame with financial data

    Returns:
        Gauge chart data for multiple ratios
    """
    try:
        gauges = []

        # Current Ratio
        if "current_assets" in df.columns and "current_liabilities" in df.columns:
            ca = df["current_assets"].iloc[-1]
            cl = df["current_liabilities"].iloc[-1]
            if cl != 0:
                current_ratio = ca / cl
                gauges.append({
                    "name": "Current Ratio",
                    "value": round(float(current_ratio), 2),
                    "min": 0,
                    "max": 3,
                    "thresholds": [
                        {"value": 1.0, "color": "red", "label": "Low"},
                        {"value": 1.5, "color": "yellow", "label": "Adequate"},
                        {"value": 2.0, "color": "green", "label": "Good"}
                    ]
                })

        # Debt to Equity
        if "total_debt" in df.columns and "total_equity" in df.columns:
            debt = df["total_debt"].iloc[-1]
            equity = df["total_equity"].iloc[-1]
            if equity != 0:
                de_ratio = debt / equity
                gauges.append({
                    "name": "Debt to Equity",
                    "value": round(float(de_ratio), 2),
                    "min": 0,
                    "max": 2,
                    "thresholds": [
                        {"value": 0.5, "color": "green", "label": "Low"},
                        {"value": 1.0, "color": "yellow", "label": "Moderate"},
                        {"value": 1.5, "color": "red", "label": "High"}
                    ]
                })

        return {
            "chart_type": "gauge",
            "title": "Financial Health Indicators",
            "gauges": gauges
        }

    except Exception as e:
        return {"error": f"Gauge chart generation failed: {str(e)}"}


def generate_all_charts(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate all chart data at once

    Args:
        df: DataFrame with financial data

    Returns:
        Dictionary containing all chart data
    """
    return {
        "revenue_trend": generate_revenue_chart(df),
        "margin_analysis": generate_margin_chart(df),
        "key_metrics": generate_metrics_chart(df),
        "cash_flow_waterfall": generate_cash_flow_waterfall(df),
        "ratio_gauges": generate_ratio_gauge(df)
    }


def generate_comparison_chart(df: pd.DataFrame, metric: str,
                              periods: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate comparison chart for a specific metric across periods

    Args:
        df: DataFrame with financial data
        metric: Metric column name to compare
        periods: Optional list of period names

    Returns:
        Comparison chart data
    """
    try:
        if metric not in df.columns:
            return {"error": f"Metric '{metric}' not found"}

        values = df[metric].tolist()

        if periods and len(periods) == len(values):
            labels = periods
        else:
            # Try to get period labels from dataframe
            period_col = None
            for col in ["period", "date", "quarter", "year"]:
                if col in df.columns:
                    period_col = col
                    break

            if period_col:
                labels = df[period_col].astype(str).tolist()
            else:
                labels = [f"Period {i+1}" for i in range(len(values))]

        return {
            "chart_type": "bar",
            "title": f"{metric.replace('_', ' ').title()} Comparison",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": metric.replace('_', ' ').title(),
                    "data": values,
                    "backgroundColor": "rgba(54, 162, 235, 0.5)",
                    "borderColor": "rgb(54, 162, 235)",
                    "borderWidth": 1
                }]
            }
        }

    except Exception as e:
        return {"error": f"Comparison chart generation failed: {str(e)}"}
