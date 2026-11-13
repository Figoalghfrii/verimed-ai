"""Standardized reusable API response and error envelopes."""

from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from verimed_api.core.config import get_settings

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata attached to every API response."""

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    api_version: str = "v1"
    is_demonstration: bool = Field(default_factory=lambda: get_settings().is_demonstration_mode)


class ApiResponse(BaseModel, Generic[T]):
    """Standardized success response wrapper."""

    model_config = ConfigDict(extra="forbid")

    success: bool = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class ErrorDetail(BaseModel):
    """Specific validation or domain error item."""

    model_config = ConfigDict(extra="forbid")

    field: str | None = None
    issue: str


class ErrorBody(BaseModel):
    """Structured error information."""

    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Standardized error response wrapper."""

    model_config = ConfigDict(extra="forbid")

    success: bool = False
    error: ErrorBody
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
