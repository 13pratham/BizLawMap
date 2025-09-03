"""
Configuration settings for the BizLaw Advisor application
"""
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

@dataclass
class SourceConfig:
    """Configuration for legal source prioritization"""
    FEDERAL_SOURCES = [
        "irs.gov",
        "osha.gov",
        "epa.gov",
        "dol.gov",
        "msha.gov",
        "eeoc.gov",
        "hhs.gov",
        "sba.gov",
        "ecfr.gov",
        "govinfo.gov"
    ]
    
    DOMAIN_PRIORITY = [".gov", ".org"]

@dataclass
class LawCategories:
    """Available law categories"""
    CATEGORIES = [
        "Business Formation and Governance",
        "Taxation",
        "Employment and Labor",
        "Health and Safety",
        "Environmental Protection",
        "Intellectual Property",
        "Consumer Protection and Marketing",
        "Privacy and Data Protection",
        "Antitrust and Competition",
        "Licensing, Permits and Zoning",
        "Immigration and Workforce Eligibility",
        "Financial and Securities",
        "International Trade and Imports/Exports",
        "Industry-Specific Regulations",
        "OTHER"
    ]

@dataclass
class AppConfig:
    """Main application configuration"""
    # API Configuration
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyClEeF5cKvSEdcDWPVXQ79d-gqDQXs0fVc")
    MODEL_NAME = "gemini-2.5-flash"
    
    # Response Configuration
    MAX_RESPONSE_TIME = 20  # seconds
    
    # Jurisdiction Priority
    JURISDICTION_ORDER = ["Federal", "State", "Local"]
    
    # Source Registry
    SOURCES = SourceConfig()
    
    # Law Categories
    LAW_CATEGORIES = LawCategories()
    
    # Session Configuration
    SESSION_TIMEOUT = 3600  # 1 hour
