"""
Configuration management for FinStory API
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Model Configuration
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # "openai" or "gemini"
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # gpt-4o-mini, gpt-4o, gpt-3.5-turbo
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

    # Application Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Persona Definitions
    PERSONAS = {
        "CFO": {
            "focus": "operational efficiency, cost management, cash flow optimization",
            "priority": "financial health, liquidity, operational metrics"
        },
        "Investor": {
            "focus": "growth potential, return on investment, market position",
            "priority": "revenue growth, profitability, competitive advantage"
        },
        "Board": {
            "focus": "strategic direction, risk management, long-term sustainability",
            "priority": "governance, strategic goals, stakeholder value"
        }
    }

    # Financial Thresholds for Risk Detection
    RISK_THRESHOLDS = {
        "revenue_decline": -5.0,  # % decline that triggers risk
        "margin_decline": -3.0,   # % margin decline
        "cash_flow_negative": 0,  # negative cash flow threshold
        "debt_ratio_high": 0.7,   # debt to equity ratio
        "low_liquidity": 1.5      # current ratio threshold
    }

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if cls.AI_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required. Set it in .env file")
        elif cls.AI_PROVIDER == "gemini":
            if not cls.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required. Set it in .env file")
        else:
            raise ValueError(f"Invalid AI_PROVIDER: {cls.AI_PROVIDER}. Must be 'openai' or 'gemini'")
        return True


# Export singleton instance
config = Config()
