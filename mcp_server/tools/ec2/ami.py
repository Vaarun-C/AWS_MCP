# mcp_server/tools/ec2/ami_tools.py

import boto3
from fastmcp.tools import FunctionTool
from typing import Dict, Any, Optional, List

from mcp_server.models.ec2.ami import (
    CreateAMIParams,
    DescribeImagesParams,
    DeregisterAMIParams,
)

def create_ami(
    *,
    instance_id: str,
    name: str,
    no_reboot: bool = True,
    description: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    region: str = "ap-south-1"
):
    ec2 = boto3.client("ec2", region_name=region)

    req: Dict[str, Any] = {
        "InstanceId": instance_id,
        "Name": name,
        "NoReboot": no_reboot,
    }

    if description:
        req["Description"] = description

    # Tags
    if tags:
        req["TagSpecifications"] = [
            {
                "ResourceType": "image",
                "Tags": [{"Key": k, "Value": v} for k, v in tags.items()],
            }
        ]

    return ec2.create_image(**req)

def describe_images(
    *,
    owners: Optional[List[str]] = None,
    image_ids: Optional[List[str]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    region: str = "ap-south-1"
):
    ec2 = boto3.client("ec2", region_name=region)

    req: Dict[str, Any] = {}

    if owners:
        req["Owners"] = owners

    if image_ids:
        req["ImageIds"] = image_ids

    if filters:
        req["Filters"] = filters

    resp = ec2.describe_images(**req)
    return resp.get("Images", [])

def deregister_ami(
    *,
    image_id: str,
    region: str = "ap-south-1"
):
    ec2 = boto3.client("ec2", region_name=region)
    return ec2.deregister_image(ImageId=image_id)

tools = [
    FunctionTool(
        name="aws.create_ami",
        description="Create an AMI image from an instance.",
        fn=create_ami,
        parameters=CreateAMIParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.describe_images",
        description="Describe AMIs by owner, filters, or image IDs.",
        fn=describe_images,
        parameters=DescribeImagesParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.deregister_ami",
        description="Deregister an existing AMI.",
        fn=deregister_ami,
        parameters=DeregisterAMIParams.model_json_schema(),
    ),
]
