# FinStory AI Agent - Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Dependencies (2 min)

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (web framework)
- Pandas & NumPy (data processing)
- Google Generative AI (Gemini)
- LangGraph & LangChain (AI workflow)
- Python-PPTX (presentation generation)

## Step 2: Get Gemini API Key (1 min)

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key

## Step 3: Configure Environment (1 min)

```bash
# Copy the example file
cp .env.example .env

# Edit .env and paste your API key
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

Your `.env` should look like:
```env
GEMINI_API_KEY=AIzaSy...your_actual_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
DEBUG=False
```

## Step 4: Test the Agent (1 min)

```bash
python test_agent.py
```

You should see output like:
```
================================================================================
FinStory AI Agent - Test Suite
================================================================================

Testing imports...
[OK] Configuration validated

================================================================================
TEST 1: CFO Analysis
================================================================================

============================================================
Starting Financial Analysis for CFO
============================================================

[OK] Calculated 5 metric categories
[OK] Generated 4 key takeaways for CFO
[OK] Identified 2 potential risks
[OK] Generated 5 chart datasets
[OK] Generated 5 recommendations

============================================================
Analysis Complete!
============================================================

--- RESULTS ---
Status: success

Key Metrics:
  Revenue Growth: -8.33%
  Gross Margin: 36.36%
  Net Margin: 17.27%

Key Takeaways (4):
  1. [AI-generated insight about revenue decline]
  2. [AI-generated insight about margins]
  3. [AI-generated insight about cash position]
  4. [AI-generated insight about financial health]

Risks Identified (2):
  - [MEDIUM] Revenue Decline
    Revenue is declining at -8.33% year-over-year

Recommendations (5):
  1. [Actionable recommendation]
  2. [Actionable recommendation]
  ...
```

## Step 5: Use in Your Code (< 1 min)

### Simple Example
```python
import pandas as pd
from ai_agent import run_langgraph_analysis

# Your financial data
df = pd.DataFrame({
    "period": ["Q1", "Q2", "Q3", "Q4"],
    "revenue": [1000000, 1150000, 1200000, 1100000],
    "net_income": [180000, 210000, 220000, 190000]
})

# Run analysis
result = await run_langgraph_analysis(df, persona="CFO")

# Use results
print(result["insights"]["summary"])
print(result["risks"])
print(result["recommendations"])
```

### FastAPI Integration
```python
from fastapi import FastAPI
from ai_agent import run_langgraph_analysis

app = FastAPI()

@app.post("/api/analyze")
async def analyze_financials(data: dict):
    df = pd.DataFrame(data["financial_data"])
    result = await run_langgraph_analysis(
        df,
        persona=data.get("persona", "CFO")
    )
    return result
```

## What You Get

The AI Agent provides:

### 📊 Comprehensive Metrics
- Revenue growth & CAGR
- Profit margins (gross, operating, net)
- Cash flow analysis (OCF, FCF, runway)
- Financial ratios (liquidity, leverage, profitability)

### 🤖 AI-Powered Insights
- Key takeaways (3-5 bullet points)
- Strengths and concerns
- Executive summary
- Persona-specific analysis (CFO, Investor, Board)

### ⚠️ Risk Detection
- Automated risk identification
- Severity classification (high/medium/low)
- Impact analysis
- Mitigation suggestions

### 📈 Visualization Data
- Revenue trend charts
- Margin analysis charts
- Key metrics comparisons
- Cash flow waterfalls
- Financial ratio gauges

### 💡 Actionable Recommendations
- Prioritized by urgency
- Persona-tailored
- Specific and actionable

## Supported Personas

### CFO (Chief Financial Officer)
**Focus**: Operational efficiency, cost management, cash flow
**Priority**: Financial health, liquidity, operational metrics

### Investor
**Focus**: Growth potential, ROI, market position
**Priority**: Revenue growth, profitability, competitive advantage

### Board
**Focus**: Strategic direction, governance, sustainability
**Priority**: Strategic goals, risk management, stakeholder value

## Data Format

Your CSV or DataFrame should have:

**Required:**
- `revenue` - Total revenue

**Recommended:**
- `cost_of_goods_sold` - COGS
- `operating_income` - Operating profit
- `net_income` - Net profit
- `cash_from_operations` - Operating cash flow

**Optional:**
- `current_assets`, `current_liabilities`
- `total_assets`, `total_debt`, `total_equity`
- `period` or `date` - Time period labels

Example CSV:
```csv
period,revenue,cost_of_goods_sold,net_income,cash_from_operations
Q1 2024,1000000,600000,180000,200000
Q2 2024,1150000,690000,210000,230000
Q3 2024,1200000,720000,220000,240000
Q4 2024,1100000,700000,190000,210000
```

## Troubleshooting

### "GEMINI_API_KEY is required"
**Solution**: Make sure you created `.env` file and added your API key

### "No module named 'google'"
**Solution**: Run `pip install -r requirements.txt`

### Import errors
**Solution**: Run `python verify_imports.py` to diagnose

### AI responses not parsing
**Solution**: Check your Gemini API key is valid and has credits

## Common Customizations

### Change Risk Thresholds
Edit `config.py`:
```python
RISK_THRESHOLDS = {
    "revenue_decline": -5.0,  # Change from -5% to your threshold
    "margin_decline": -3.0,
    ...
}
```

### Add Custom Persona
Edit `config.py`:
```python
PERSONAS = {
    "CFO": {...},
    "MyCustomRole": {
        "focus": "your focus areas",
        "priority": "your priorities"
    }
}
```

Then add prompt in `prompts.py`.

### Add New Metrics
Edit `financial_calculations.py`:
```python
def calculate_my_metric(df: pd.DataFrame) -> Dict[str, Any]:
    # Your calculation
    return {"my_metric": value}
```

## Next Steps

1. ✅ **Test with your data**: Replace sample data with real financials
2. ✅ **Integrate with backend**: Connect to your FastAPI endpoints
3. ✅ **Customize personas**: Tailor prompts to your stakeholders
4. ✅ **Add visualizations**: Use chart data in your frontend
5. ✅ **Deploy**: Add to production environment

## Files Created

```
backend/
├── config.py                   # Config & API keys
├── financial_calculations.py   # Metrics engine
├── prompts.py                  # AI prompts
├── ai_utils.py                 # Response parsing
├── charts.py                   # Chart data
├── ai_agent.py                 # Main workflow ⭐
├── test_agent.py               # Test suite
├── verify_imports.py           # Validation
├── requirements.txt            # Dependencies
├── .env.example                # Config template
├── AI_AGENT_README.md          # Full docs
├── IMPLEMENTATION_SUMMARY.md   # Technical details
└── QUICKSTART.md               # This file
```

## Getting Help

1. **Check documentation**: See `AI_AGENT_README.md`
2. **Run tests**: `python test_agent.py`
3. **Verify setup**: `python verify_imports.py`
4. **Check implementation**: See `IMPLEMENTATION_SUMMARY.md`

---

**Ready to analyze!** 🚀

The AI Agent is fully functional and ready for your financial analysis needs.
