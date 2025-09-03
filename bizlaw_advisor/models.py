"""
Data models for the BizLaw Advisor application
"""
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class BusinessContext:
    """Business context information"""
    city: str
    state: str
    business_type: str
    area_of_law: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "city": self.city,
            "state": self.state,
            "business_type": self.business_type,
            "area_of_law": self.area_of_law
        }

@dataclass
class LegalSource:
    """Legal source information"""
    url: str
    jurisdiction: str  # Federal, State, or Local
    title: str
    description: str
    relevance_score: float
    content: Optional[str] = None  # Full content from the source

@dataclass
class LegalResponse:
    """Response containing legal information"""
    federal_laws: List[LegalSource]
    state_laws: List[LegalSource]
    local_laws: List[LegalSource]
    summary: str
    key_points: List[str]
    jurisdiction_analysis: Dict[str, str]  # Analysis by jurisdiction level
    compliance_steps: List[str]  # Steps for compliance
    overlapping_regulations: List[str]  # Identified overlapping regulations
    sources: List[str]
    response_time: float  # in seconds
