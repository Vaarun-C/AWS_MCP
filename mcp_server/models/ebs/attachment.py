"""Models for EBS volume attachment operations."""

from pydantic import BaseModel, Field
from typing import Optional


class AttachVolumeParams(BaseModel):
    region: str = Field(default="ap-south-1")
    VolumeId: str
    InstanceId: str
    Device: str  # e.g., "/dev/sdf"


class DetachVolumeParams(BaseModel):
    region: str = Field(default="ap-south-1")
    VolumeId: str
    InstanceId: Optional[str] = None
    Force: Optional[bool] = False
