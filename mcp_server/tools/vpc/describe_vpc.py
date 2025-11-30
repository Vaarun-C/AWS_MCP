# mcp_server/tools/ec2/vpc_tools.py

import boto3
from fastmcp.tools import FunctionTool
from typing import Optional

from mcp_server.models.vpc.describe_vpc import (
    RegionOnlyParams,
    DescribeVpcParams,
    DescribeSubnetParams
)

# ============================================================
# LIST ALL VPCS
# ============================================================

def list_vpcs(*, region: str = "ap-south-1"):
    ec2 = boto3.client("ec2", region_name=region)
    resp = ec2.describe_vpcs()
    return {
        "region": region,
        "vpcs": resp.get("Vpcs", [])
    }


# ============================================================
# GET DEFAULT VPC
# ============================================================

def get_default_vpc(*, region: str = "ap-south-1"):
    ec2 = boto3.client("ec2", region_name=region)
    resp = ec2.describe_vpcs(
        Filters=[{"Name": "isDefault", "Values": ["true"]}]
    )

    vpcs = resp.get("Vpcs", [])
    return {
        "region": region,
        "default_vpc": vpcs[0] if vpcs else None
    }


# ============================================================
# DESCRIBE SPECIFIC VPC
# ============================================================

def describe_vpc(*, vpc_id: Optional[str] = None, region: str = "ap-south-1"):
    ec2 = boto3.client("ec2", region_name=region)

    if vpc_id:
        resp = ec2.describe_vpcs(VpcIds=[vpc_id])
    else:
        resp = ec2.describe_vpcs()

    return {
        "region": region,
        "vpcs": resp.get("Vpcs", [])
    }


# ============================================================
# LIST SUBNETS
# ============================================================

def list_subnets(*, region: str = "ap-south-1"):
    ec2 = boto3.client("ec2", region_name=region)
    resp = ec2.describe_subnets()
    return {
        "region": region,
        "subnets": resp.get("Subnets", [])
    }


# ============================================================
# GET ALL SUBNETS IN DEFAULT VPC
# ============================================================

def get_default_subnets(*, region: str = "ap-south-1"):
    ec2 = boto3.client("ec2", region_name=region)

    # Fetch default VPC
    vpcs = ec2.describe_vpcs(
        Filters=[{"Name": "isDefault", "Values": ["true"]}]
    ).get("Vpcs", [])

    if not vpcs:
        return {
            "region": region,
            "error": "Default VPC not found",
            "subnets": []
        }

    default_vpc_id = vpcs[0]["VpcId"]

    resp = ec2.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [default_vpc_id]}]
    )

    return {
        "region": region,
        "default_vpc_id": default_vpc_id,
        "subnets": resp.get("Subnets", [])
    }


# ============================================================
# DESCRIBE SPECIFIC SUBNET OR FILTER BY VPC
# ============================================================

def describe_subnet(
    *,
    subnet_id: Optional[str] = None,
    vpc_id: Optional[str] = None,
    region: str = "ap-south-1"
):
    ec2 = boto3.client("ec2", region_name=region)

    filters = []
    if vpc_id:
        filters.append({"Name": "vpc-id", "Values": [vpc_id]})

    if subnet_id:
        resp = ec2.describe_subnets(SubnetIds=[subnet_id])
    else:
        resp = ec2.describe_subnets(Filters=filters or None)

    return {
        "region": region,
        "subnets": resp.get("Subnets", [])
    }


# ============================================================
# REGISTER TOOLS
# ============================================================

tools = [
    FunctionTool(
        name="vpc.list_vpcs",
        description="List all VPCs in a region.",
        fn=list_vpcs,
        parameters=RegionOnlyParams.model_json_schema()
    ),
    FunctionTool(
        name="vpc.get_default_vpc",
        description="Get the default VPC in a region.",
        fn=get_default_vpc,
        parameters=RegionOnlyParams.model_json_schema()
    ),
    FunctionTool(
        name="vpc.describe_vpc",
        description="Describe specific VPC or all VPCs.",
        fn=describe_vpc,
        parameters=DescribeVpcParams.model_json_schema()
    ),
    FunctionTool(
        name="vpc.list_subnets",
        description="List all subnets in a region.",
        fn=list_subnets,
        parameters=RegionOnlyParams.model_json_schema()
    ),
    FunctionTool(
        name="vpc.get_default_subnets",
        description="List all subnets that belong to the default VPC.",
        fn=get_default_subnets,
        parameters=RegionOnlyParams.model_json_schema()
    ),
    FunctionTool(
        name="vpc.describe_subnet",
        description="Describe a subnet or list subnets in a specific VPC.",
        fn=describe_subnet,
        parameters=DescribeSubnetParams.model_json_schema()
    ),
]
