"""Pydantic models for Threat Dragon threat modeling data structures."""

from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict


class Marker(BaseModel):
    name: str


class Body(BaseModel):
    stroke: str
    strokeWidth: Optional[float] = None
    strokeDasharray: Optional[str] = None


class Line(BaseModel):
    stroke: str
    strokeWidth: Optional[float] = None
    sourceMarker: Optional[Union[Marker, str]] = None
    strokeDasharray: Optional[str] = None
    targetMarker: Union[Marker, str]


class Attrs(BaseModel):
    body: Optional[Body] = None
    line: Optional[Line] = None


class Position(BaseModel):
    x: float
    y: float


class Size(BaseModel):
    height: float = Field(..., ge=10)
    width: float = Field(..., ge=10)


class Vertice(BaseModel):
    x: float
    y: float


class SourceTarget(BaseModel):
    cell: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None


class Data(BaseModel):
    description: Optional[str] = None
    handlesCardPayment: Optional[bool] = None
    handlesGoodsOrServices: Optional[bool] = None
    isALog: Optional[bool] = None
    isBidirectional: Optional[bool] = None
    isEncrypted: Optional[bool] = None
    isPublicNetwork: Optional[bool] = None
    isSigned: Optional[bool] = None
    isTrustBoundary: Optional[bool] = None
    isWebApplication: Optional[bool] = None
    name: str
    outOfScope: Optional[bool] = None
    privilegeLevel: Optional[str] = None
    protocol: Optional[str] = None
    providesAuthentication: Optional[bool] = None
    reasonOutOfScope: Optional[str] = None
    storesCredentials: Optional[bool] = None
    storesInventory: Optional[bool] = None
    type: str
    hasOpenThreats: bool


class Threat(BaseModel):
    description: str
    mitigation: str
    modelType: Optional[str] = None
    number: Optional[int] = None
    score: Optional[str] = None
    severity: str = Field(..., pattern=r"^(High|Medium|Low)$")
    status: str = Field(..., pattern=r"^(NA|Open|Mitigated)$")
    threatId: Optional[str] = Field(None, min_length=2)
    title: str
    type: str


class Cell(BaseModel):
    attrs: Optional[Attrs] = None
    data: Optional[Data] = None
    id: str = Field(..., min_length=2)
    position: Optional[Position] = None
    size: Optional[Size] = None
    connector: Optional[str] = None
    source: Optional[SourceTarget] = None
    target: Optional[SourceTarget] = None
    threats: List[Threat] = []
    shape: str
    visible: Optional[bool] = None
    vertices: Optional[List[Vertice]] = None
    zIndex: int


class Diagram(BaseModel):
    description: Optional[str] = None
    diagramType: str = Field(..., min_length=3)
    id: int = Field(..., ge=0)
    placeholder: Optional[str] = None
    thumbnail: str
    title: str
    version: str = Field(..., max_length=10)
    cells: List[Cell]


class Contributor(BaseModel):
    name: str


class Detail(BaseModel):
    contributors: List[Contributor]
    diagrams: List[Diagram]
    diagramTop: int = Field(..., ge=0)
    reviewer: str
    threatTop: int = Field(..., ge=0)


class Summary(BaseModel):
    description: Optional[str] = None
    id: Optional[int] = Field(None, ge=0)
    owner: Optional[str] = None
    title: str


class ThreatDragonModel(BaseModel):
    version: str = Field(..., max_length=10)
    summary: Summary
    detail: Detail
