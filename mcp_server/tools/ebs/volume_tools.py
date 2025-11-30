# mcp_server/tools/ec2/ebs/volume_tools.py

import boto3
from fastmcp.tools import FunctionTool
from mcp_server.models.ebs import (
    CreateVolumeParams,
    ModifyVolumeParams,
    DeleteVolumeParams,
    DescribeVolumeParams,
)

# =======================================================
# CREATE VOLUME
# =======================================================
def create_volume(params: CreateVolumeParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    req = {
        "AvailabilityZone": params.AvailabilityZone,
        "VolumeType": params.VolumeType,
    }

    if params.Size:
        req["Size"] = params.Size
    if params.SnapshotId:
        req["SnapshotId"] = params.SnapshotId
    if params.Iops:
        req["Iops"] = params.Iops
    if params.Throughput:
        req["Throughput"] = params.Throughput
    if params.Encrypted is not None:
        req["Encrypted"] = params.Encrypted
    if params.KmsKeyId:
        req["KmsKeyId"] = params.KmsKeyId

    if params.Tags:
        req["TagSpecifications"] = [
            {
                "ResourceType": "volume",
                "Tags": [{"Key": k, "Value": v} for k, v in params.Tags.items()],
            }
        ]

    if params.ExtraParams:
        req.update(params.ExtraParams)

    return ec2.create_volume(**req)


# =======================================================
# MODIFY VOLUME
# =======================================================
def modify_volume(params: ModifyVolumeParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    req = {"VolumeId": params.VolumeId}

    if params.Size:
        req["Size"] = params.Size
    if params.VolumeType:
        req["VolumeType"] = params.VolumeType
    if params.Iops:
        req["Iops"] = params.Iops
    if params.Throughput:
        req["Throughput"] = params.Throughput

    return ec2.modify_volume(**req)


# =======================================================
# DELETE VOLUME
# =======================================================
def delete_volume(params: DeleteVolumeParams):
    ec2 = boto3.client("ec2", region_name=params.region)
    return ec2.delete_volume(VolumeId=params.VolumeId)


# =======================================================
# DESCRIBE VOLUMES
# =======================================================
def describe_volumes(params: DescribeVolumeParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    if params.VolumeId:
        resp = ec2.describe_volumes(VolumeIds=[params.VolumeId])
    else:
        resp = ec2.describe_volumes(Filters=params.Filters or [])

    return resp.get("Volumes", [])


tools = [
    FunctionTool(
        name="aws.create_volume",
        description="Create an EBS volume",
        fn=create_volume,
        parameters=CreateVolumeParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.modify_volume",
        description="Modify an EBS volume",
        fn=modify_volume,
        parameters=ModifyVolumeParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.delete_volume",
        description="Delete an EBS volume",
        fn=delete_volume,
        parameters=DeleteVolumeParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.describe_volumes",
        description="Describe EBS volumes",
        fn=describe_volumes,
        parameters=DescribeVolumeParams.model_json_schema(),
    ),
]
