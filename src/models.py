"""Pydantic models for AI threat generation and response handling."""

from pydantic import BaseModel, Field, RootModel
from typing import List, Dict


class Threats(BaseModel):
    title: str
    status: str = Field(..., pattern=r"^(NA|Open|Mitigated)$")
    severity: str = Field(..., pattern=r"^(High|Medium|Low)$")
    type: str
    description: str
    mitigation: str
    modelType: str = Field(..., pattern=r"^(STRIDE|LINDDUN|CIA|DIEF|RANSOM|PLOT4ai|Generic)$")


class AIThreatsResponse(BaseModel):
    """Pydantic model for AI response containing threats for multiple cells."""
    id: str= Field(..., description="element id mapping to lists of threats")
    threats: List[Threats] = Field(..., description="list of threats for the element")

class AIThreatsResponseList(RootModel):
    """Pydantic model for validating a list of AIThreatsResponse objects."""
    root: List[AIThreatsResponse] = Field(
        ..., 
        description="List of threat responses, each containing an ID and associated threats"
    )