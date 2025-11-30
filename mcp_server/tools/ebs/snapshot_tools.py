# mcp_server/tools/ec2/ebs/snapshot_tools.py

import boto3
from fastmcp.tools import FunctionTool

from mcp_server.models.ebs import (
    ListSnapshotsParams,
    SnapshotIdParam,
    DeleteSnapshotParams,
    CopySnapshotParams,
    CreateVolumeFromSnapshotParams,
    FastRestoreParams,
    CreateSnapshotParams,
)

# =======================================================
# CREATE SNAPSHOT
# =======================================================
def create_snapshot(params: CreateSnapshotParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    req = {
        "VolumeId": params.VolumeId,
        "Description": params.Description or f"Snapshot of {params.VolumeId}",
    }

    if params.Tags:
        req["TagSpecifications"] = [
            {
                "ResourceType": "snapshot",
                "Tags": [{"Key": k, "Value": v} for k, v in params.Tags.items()],
            }
        ]

    return ec2.create_snapshot(**req)


# =======================================================
# LIST SNAPSHOTS
# =======================================================
def list_snapshots(params: ListSnapshotsParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    req = {}

    if params.OwnerIds:
        req["OwnerIds"] = params.OwnerIds

    if params.Filters:
        req["Filters"] = params.Filters

    resp = ec2.describe_snapshots(**req)
    return resp.get("Snapshots", [])


# =======================================================
# DESCRIBE A SPECIFIC SNAPSHOT
# =======================================================
def describe_snapshot(params: SnapshotIdParam):
    ec2 = boto3.client("ec2", region_name=params.region)
    resp = ec2.describe_snapshots(SnapshotIds=[params.SnapshotId])
    return resp.get("Snapshots", [])


# =======================================================
# DELETE SNAPSHOT
# =======================================================
def delete_snapshot(params: DeleteSnapshotParams):
    ec2 = boto3.client("ec2", region_name=params.region)
    return ec2.delete_snapshot(SnapshotId=params.SnapshotId)


# =======================================================
# COPY SNAPSHOT (Cross Region Snapshot Copy)
# =======================================================
def copy_snapshot(params: CopySnapshotParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    req = {
        "SourceRegion": params.SourceRegion,
        "SourceSnapshotId": params.SourceSnapshotId,
        "Description": params.Description or f"Copy of {params.SourceSnapshotId}",
    }

    if params.Encrypted is not None:
        req["Encrypted"] = params.Encrypted

    if params.KmsKeyId:
        req["KmsKeyId"] = params.KmsKeyId

    if params.Tags:
        req["TagSpecifications"] = [
            {
                "ResourceType": "snapshot",
                "Tags": [{"Key": k, "Value": v} for k, v in params.Tags.items()],
            }
        ]

    return ec2.copy_snapshot(**req)


# =======================================================
# CREATE VOLUME FROM SNAPSHOT (RESTORE)
# =======================================================
def restore_volume_from_snapshot(params: CreateVolumeFromSnapshotParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    req = {
        "SnapshotId": params.SnapshotId,
        "AvailabilityZone": params.AvailabilityZone,
        "VolumeType": params.VolumeType,
    }

    if params.Size:
        req["Size"] = params.Size
    if params.Iops:
        req["Iops"] = params.Iops
    if params.Throughput:
        req["Throughput"] = params.Throughput
    if params.Encrypted is not None:
        req["Encrypted"] = params.Encrypted
    if params.KmsKeyId:
        req["KmsKeyId"] = params.KmsKeyId
    if params.ExtraParams:
        req.update(params.ExtraParams)

    return ec2.create_volume(**req)


# =======================================================
# FAST SNAPSHOT RESTORE (ENABLE/DISABLE)
# =======================================================
def manage_fast_snapshot_restore(params: FastRestoreParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    if params.State not in ("enable", "disable"):
        return {"error": "State must be 'enable' or 'disable'"}

    if params.State == "enable":
        return ec2.enable_fast_snapshot_restores(
            SnapshotId=params.SnapshotId,
            AvailabilityZones=params.AvailabilityZones,
        )

    if params.State == "disable":
        return ec2.disable_fast_snapshot_restores(
            SnapshotId=params.SnapshotId,
            AvailabilityZones=params.AvailabilityZones,
        )


# =======================================================
# TOOL REGISTRATION
# =======================================================
tools = [
    FunctionTool(
        name="aws.create_snapshot",
        description="Create an EBS snapshot from a volume.",
        fn=create_snapshot,
        parameters=CreateSnapshotParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.list_snapshots",
        description="List EBS snapshots (owned/shared/public).",
        fn=list_snapshots,
        parameters=ListSnapshotsParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.describe_snapshot",
        description="Describe a specific snapshot.",
        fn=describe_snapshot,
        parameters=SnapshotIdParam.model_json_schema(),
    ),
    FunctionTool(
        name="aws.delete_snapshot",
        description="Delete a snapshot.",
        fn=delete_snapshot,
        parameters=DeleteSnapshotParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.copy_snapshot",
        description="Copy a snapshot to another region.",
        fn=copy_snapshot,
        parameters=CopySnapshotParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.restore_volume_from_snapshot",
        description="Create/restore an EBS volume from a snapshot.",
        fn=restore_volume_from_snapshot,
        parameters=CreateVolumeFromSnapshotParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.manage_fast_snapshot_restore",
        description="Enable or disable Fast Snapshot Restore for AZs.",
        fn=manage_fast_snapshot_restore,
        parameters=FastRestoreParams.model_json_schema(),
    ),
]
