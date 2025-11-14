# FinStory AI Agent

Complete AI-powered financial analysis system using LangGraph and Google Gemini.

## Architecture Overview

The AI Agent consists of several interconnected modules:

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
│                     (ai_agent.py)                           │
└─────────────────────────────────────────────────────────────┘
        │
        ├─> 1. Calculate Metrics (financial_calculations.py)
        │       - Revenue growth, CAGR
        │       - Profit margins (gross, operating, net)
        │       - Cash flow analysis
        │       - Financial ratios
        │
        ├─> 2. Generate Insights (prompts.py + ai_utils.py)
        │       - Persona-specific prompts (CFO/Investor/Board)
        │       - AI-powered analysis via Gemini
        │       - Structured insight parsing
        │
        ├─> 3. Identify Risks (ai_utils.py)
        │       - Rule-based risk detection
        │       - AI-enhanced risk analysis
        │       - Risk categorization & severity
        │
        ├─> 4. Generate Charts (charts.py)
        │       - Revenue trends
        │       - Margin analysis
        │       - Cash flow waterfall
        │       - Financial ratio gauges
        │
        └─> 5. Create Recommendations (ai_utils.py)
                - Actionable recommendations
                - Persona-tailored priorities
                - Risk-based suggestions
```

## Module Descriptions

### 1. `ai_agent.py` - Core Workflow
The main LangGraph workflow that orchestrates the entire analysis process.

**Key Functions:**
- `run_langgraph_analysis(financial_data, persona)` - Main entry point
- `build_workflow()` - Constructs the LangGraph state machine
- Individual node functions for each analysis step

**Usage:**
```python
from ai_agent import run_langgraph_analysis
import pandas as pd

df = pd.read_csv("financial_data.csv")
result = await run_langgraph_analysis(df, persona="CFO")
```

### 2. `financial_calculations.py` - Metrics Engine
Comprehensive financial metrics calculation module.

**Metrics Calculated:**
- **Growth Metrics**: Revenue growth, CAGR, period-over-period changes
- **Margin Analysis**: Gross, operating, and net profit margins
- **Cash Flow**: OCF, FCF, cash conversion cycle, runway
- **Financial Ratios**: Current ratio, quick ratio, D/E, ROE, ROA
- **Trend Analysis**: Multi-period trend identification

**Key Functions:**
```python
calculate_growth(df, "revenue")          # Growth analysis
calculate_margin(df)                     # Margin calculations
calculate_cash_flow(df)                  # Cash flow metrics
calculate_financial_ratios(df)          # Key ratios
calculate_all_metrics(df)               # All at once
```

### 3. `prompts.py` - Persona-Specific Prompts
Generates tailored prompts for different stakeholder personas.

**Supported Personas:**
- **CFO**: Operational efficiency, cost management, cash flow
- **Investor**: Growth potential, ROI, competitive position
- **Board**: Strategic direction, governance, sustainability

**Key Functions:**
```python
create_persona_prompt(metrics, persona)        # Main analysis prompt
create_risk_analysis_prompt(metrics)           # Risk identification
create_comparison_prompt(m1, m2, p1, p2)      # Period comparison
create_qa_prompt(context, question, persona)   # Q&A prompts
```

### 4. `ai_utils.py` - AI Response Processing
Handles parsing and processing of AI-generated responses.

**Key Functions:**
```python
parse_insights(response_text)                  # Extract structured insights
identify_risks(metrics)                        # Rule-based risk detection
generate_recommendations(metrics, risks, persona)  # Create recommendations
parse_risk_response(response_text)            # Parse AI risk analysis
```

### 5. `charts.py` - Visualization Data
Generates chart-ready data structures for frontend visualization.

**Chart Types:**
- Revenue trend (line chart)
- Margin analysis (multi-line)
- Key metrics (bar chart)
- Cash flow waterfall
- Financial ratio gauges

**Key Functions:**
```python
generate_revenue_chart(df)            # Revenue trends
generate_margin_chart(df)             # Margin analysis
generate_metrics_chart(df)            # Key metrics bar chart
generate_cash_flow_waterfall(df)      # Cash flow breakdown
generate_ratio_gauge(df)              # Ratio gauges
generate_all_charts(df)               # All charts at once
```

### 6. `config.py` - Configuration Management
Centralized configuration and environment variable management.

**Configuration:**
- API keys (Gemini)
- Model settings
- Persona definitions
- Risk thresholds

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get key from: https://makersuite.google.com/app/apikey
```

### 3. Test the Agent
```bash
python test_agent.py
```

## Data Format Requirements

The AI agent expects a pandas DataFrame with the following columns (flexible - only uses what's available):

### Required Columns:
- `revenue` - Total revenue/sales

### Recommended Columns:
- `cost_of_goods_sold` - COGS
- `operating_income` - Operating profit
- `net_income` - Net profit
- `cash_from_operations` - Operating cash flow
- `capital_expenditures` - CapEx
- `cash_and_equivalents` - Cash position

### Optional Columns (for advanced metrics):
- `current_assets`, `current_liabilities`
- `total_assets`, `total_debt`, `total_equity`
- `accounts_receivable`, `inventory`, `accounts_payable`
- `period` or `date` - Period labels

### Example CSV Format:
```csv
period,revenue,cost_of_goods_sold,net_income,cash_from_operations
Q1 2024,1000000,600000,180000,200000
Q2 2024,1150000,690000,210000,230000
Q3 2024,1200000,720000,220000,240000
```

## Usage Examples

### Basic Analysis
```python
import pandas as pd
from ai_agent import run_langgraph_analysis

# Load data
df = pd.read_csv("financials.csv")

# Run analysis for CFO
result = await run_langgraph_analysis(df, persona="CFO")

# Access results
print(result["insights"]["key_takeaways"])
print(result["risks"])
print(result["recommendations"])
```

### Synchronous Usage
```python
from ai_agent import run_langgraph_analysis_sync

# For non-async environments
result = run_langgraph_analysis_sync(df, persona="Investor")
```

### Individual Calculations
```python
from financial_calculations import calculate_growth, calculate_margin

# Calculate specific metrics
revenue_growth = calculate_growth(df, "revenue")
margins = calculate_margin(df)

print(f"Revenue Growth: {revenue_growth['growth_rate']}%")
print(f"Gross Margin: {margins['gross_margin']}%")
```

## Integration with FastAPI

The AI agent is designed to integrate seamlessly with the FastAPI backend:

```python
# In your FastAPI endpoint
from ai_agent import run_langgraph_analysis

@app.post("/api/analyze")
async def analyze_financials(request: AnalysisRequest):
    financial_data = get_financial_data(request.analysis_id)
    result = await run_langgraph_analysis(
        financial_data=financial_data,
        persona=request.persona
    )
    return result
```

## Output Structure

The workflow returns a comprehensive dictionary:

```python
{
    "status": "success",  # success, partial, or error
    "persona": "CFO",
    "metrics": {
        "revenue_metrics": {...},
        "profit_metrics": {...},
        "margins": {...},
        "cash_flow": {...},
        "financial_ratios": {...}
    },
    "insights": {
        "key_takeaways": ["...", "..."],
        "strengths": ["...", "..."],
        "concerns": ["...", "..."],
        "recommendations": ["...", "..."],
        "summary": "..."
    },
    "risks": [
        {
            "category": "liquidity",
            "severity": "high",
            "title": "...",
            "description": "...",
            "impact": "...",
            "metric_value": 1.2
        }
    ],
    "charts_data": {
        "revenue_trend": {...},
        "margin_analysis": {...},
        "key_metrics": {...},
        ...
    },
    "recommendations": ["...", "..."],
    "trends": {"revenue": "upward", ...}
}
```

## Error Handling

The agent includes comprehensive error handling:

1. **Graceful Degradation**: If AI service fails, falls back to rule-based analysis
2. **Partial Results**: Returns available data even if some steps fail
3. **Detailed Error Messages**: Includes error context in response
4. **Validation**: Validates input data and configuration

## Performance Considerations

- **Async/Await**: Workflow is fully async for better performance
- **Parallel Processing**: Can run multiple analyses concurrently
- **Caching**: Consider caching results for repeated queries
- **Rate Limiting**: Be mindful of Gemini API rate limits

## Customization

### Adding New Metrics
Edit `financial_calculations.py`:
```python
def calculate_custom_metric(df: pd.DataFrame) -> Dict[str, Any]:
    # Your calculation logic
    return {"metric_value": value}
```

### Adding New Personas
Edit `config.py` and `prompts.py`:
```python
# config.py
PERSONAS = {
    "CFO": {...},
    "CustomPersona": {
        "focus": "...",
        "priority": "..."
    }
}

# prompts.py - Add to persona_instructions dict
"CustomPersona": """..."""
```

### Custom Risk Rules
Edit `ai_utils.py`:
```python
def identify_risks(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Add your custom risk detection logic
    risks.append({...})
```

## Troubleshooting

### "GEMINI_API_KEY is required"
- Ensure `.env` file exists
- Check that `GEMINI_API_KEY` is set in `.env`
- Verify the key is valid

### "Column not found" errors
- Check your CSV has the required columns
- Update column names to match expected format
- Use flexible column matching

### AI responses not parsing correctly
- Check the `parse_insights` function
- Review Gemini response format
- Adjust JSON extraction regex if needed

## Contributing

When adding new features:
1. Follow existing code structure
2. Add type hints
3. Include error handling
4. Update this README
5. Add tests to `test_agent.py`

## License

[Your License Here]

## Support

For issues or questions:
- Create an issue in the repository
- Contact: [Your Contact Info]
