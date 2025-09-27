"""Pydantic models for AI threat generation and response handling."""

from pydantic import BaseModel, Field, RootModel
from typing import List, Dict


class Threat(BaseModel):
    title: str
    status: str = Field(..., pattern=r"^(NA|Open|Mitigated)$")
    severity: str = Field(..., pattern=r"^(High|Medium|Low)$")
    type: str
    description: str
    mitigation: str
    modelType: str = Field(..., pattern=r"^(STRIDE|LINDDUN|CIA|DIEF|RANSOM|PLOT4ai|Generic)$")


class AIThreatsResponse(RootModel[Dict[str, List[Threat]]]):
    """Pydantic model for AI response containing threats for multiple cells."""
    root: Dict[str, List[Threat]] = Field(..., description="Dictionary mapping cell IDs to lists of threats")
    
    def to_dict(self) -> Dict[str, List[Dict]]:
        """Convert to dictionary format expected by update_threats_in_file."""
        return {cell_id: [threat.model_dump() for threat in threats] 
                for cell_id, threats in self.root.items()}
