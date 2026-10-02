from typing import Any
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    category: str
    item: str
    platform: str
    estimated_price: float = Field(ge=0)
    reason: str
    search_url: str = ""


class RecommendationResult(BaseModel):
    title: str
    summary: str
    budget: float = Field(ge=0)
    estimated_total: float = Field(ge=0)
    remaining_budget: float
    recommendations: list[RecommendationItem]
    tips: list[str] = []
    outfit_analysis: str | None = None
    source: str = "fallback"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SessionInfo(BaseModel):
    authenticated: bool
    user: dict[str, Any] | None = None
