# mcp_server/tools/ec2/ebs/attachment_tools.py

import boto3
from fastmcp.tools import FunctionTool
from mcp_server.models.ebs import (
    AttachVolumeParams,
    DetachVolumeParams,
)

# =======================================================
# ATTACH
# =======================================================
def attach_volume(params: AttachVolumeParams):
    ec2 = boto3.client("ec2", region_name=params.region)
    return ec2.attach_volume(
        VolumeId=params.VolumeId,
        InstanceId=params.InstanceId,
        Device=params.Device,
    )


# =======================================================
# DETACH
# =======================================================
def detach_volume(params: DetachVolumeParams):
    ec2 = boto3.client("ec2", region_name=params.region)
    return ec2.detach_volume(
        VolumeId=params.VolumeId,
        InstanceId=params.InstanceId,
        Force=params.Force,
    )


tools = [
    FunctionTool(
        name="aws.attach_volume",
        description="Attach an EBS volume to EC2",
        fn=attach_volume,
        parameters=AttachVolumeParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.detach_volume",
        description="Detach an EBS volume",
        fn=detach_volume,
        parameters=DetachVolumeParams.model_json_schema(),
    ),
]
