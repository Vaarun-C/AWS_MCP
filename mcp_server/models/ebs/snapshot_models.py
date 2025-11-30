# mcp_server/models/ec2/ebs_snapshot_models.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class RegionOnlyParams(BaseModel):
    region: str = Field(default="ap-south-1")


class SnapshotIdParam(BaseModel):
    region: str = Field(default="ap-south-1")
    SnapshotId: str


class ListSnapshotsParams(BaseModel):
    region: str = Field(default="ap-south-1")
    OwnerIds: Optional[List[str]] = None   # ["self"]
    Filters: Optional[List[Dict[str, Any]]] = None


class DeleteSnapshotParams(BaseModel):
    region: str = Field(default="ap-south-1")
    SnapshotId: str


class CopySnapshotParams(BaseModel):
    region: str = Field(default="ap-south-1")
    SourceRegion: str
    SourceSnapshotId: str
    Description: Optional[str] = None
    Encrypted: Optional[bool] = None
    KmsKeyId: Optional[str] = None
    Tags: Optional[Dict[str, str]] = None


class CreateVolumeFromSnapshotParams(BaseModel):
    region: str = Field(default="ap-south-1")
    SnapshotId: str
    AvailabilityZone: str
    VolumeType: Optional[str] = "gp3"
    Size: Optional[int] = None
    Iops: Optional[int] = None
    Throughput: Optional[int] = None
    Encrypted: Optional[bool] = None
    KmsKeyId: Optional[str] = None
    ExtraParams: Optional[Dict[str, Any]] = None


class FastRestoreParams(BaseModel):
    region: str = Field(default="ap-south-1")
    SnapshotId: str
    AvailabilityZones: List[str]
    State: str = Field(..., description="enable | disable")

class CreateSnapshotParams(BaseModel):
    region: str = Field(default="ap-south-1")
    VolumeId: str
    Description: Optional[str] = None
    Tags: Optional[Dict[str, str]] = None
