"""EBS Models - Re-export all models for backward compatibility."""

from .volume import (
    RegionOnlyParams,
    CreateVolumeParams,
    ModifyVolumeParams,
    DeleteVolumeParams,
    DescribeVolumeParams,
)

from .attachment import (
    AttachVolumeParams,
    DetachVolumeParams,
)

from .snapshot_models import (
    SnapshotIdParam,
    ListSnapshotsParams,
    DeleteSnapshotParams,
    CopySnapshotParams,
    CreateVolumeFromSnapshotParams,
    FastRestoreParams,
    CreateSnapshotParams,
)

__all__ = [
    # Volume models
    "RegionOnlyParams",
    "CreateVolumeParams",
    "ModifyVolumeParams",
    "DeleteVolumeParams",
    "DescribeVolumeParams",
    
    # Attachment models
    "AttachVolumeParams",
    "DetachVolumeParams",
    
    # Snapshot models
    "SnapshotIdParam",
    "ListSnapshotsParams",
    "DeleteSnapshotParams",
    "CopySnapshotParams",
    "CreateVolumeFromSnapshotParams",
    "FastRestoreParams",
    "CreateSnapshotParams",
]
