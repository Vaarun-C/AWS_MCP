# mcp_server/tools/ec2/vpc_tools.py

import boto3
from fastmcp.tools import FunctionTool

from mcp_server.models.vpc.describe_vpc import (
    RegionOnlyParams,
    DescribeVpcParams,
    DescribeSubnetParams
)

# ============================================================
# LIST ALL VPCS
# ============================================================

def list_vpcs(params: RegionOnlyParams):
    ec2 = boto3.client("ec2", region_name=params.region)
    resp = ec2.describe_vpcs()
    return {
        "region": params.region,
        "vpcs": resp.get("Vpcs", [])
    }


# ============================================================
# GET DEFAULT VPC
# ============================================================

def get_default_vpc(params: RegionOnlyParams):
    ec2 = boto3.client("ec2", region_name=params.region)
    resp = ec2.describe_vpcs(
        Filters=[{"Name": "isDefault", "Values": ["true"]}]
    )

    vpcs = resp.get("Vpcs", [])
    return {
        "region": params.region,
        "default_vpc": vpcs[0] if vpcs else None
    }


# ============================================================
# DESCRIBE SPECIFIC VPC
# ============================================================

def describe_vpc(params: DescribeVpcParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    if params.vpc_id:
        resp = ec2.describe_vpcs(VpcIds=[params.vpc_id])
    else:
        resp = ec2.describe_vpcs()

    return {
        "region": params.region,
        "vpcs": resp.get("Vpcs", [])
    }


# ============================================================
# LIST SUBNETS
# ============================================================

def list_subnets(params: RegionOnlyParams):
    ec2 = boto3.client("ec2", region_name=params.region)
    resp = ec2.describe_subnets()
    return {
        "region": params.region,
        "subnets": resp.get("Subnets", [])
    }


# ============================================================
# GET ALL SUBNETS IN DEFAULT VPC
# ============================================================

def get_default_subnets(params: RegionOnlyParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    # Fetch default VPC
    vpcs = ec2.describe_vpcs(
        Filters=[{"Name": "isDefault", "Values": ["true"]}]
    ).get("Vpcs", [])

    if not vpcs:
        return {
            "region": params.region,
            "error": "Default VPC not found",
            "subnets": []
        }

    default_vpc_id = vpcs[0]["VpcId"]

    resp = ec2.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [default_vpc_id]}]
    )

    return {
        "region": params.region,
        "default_vpc_id": default_vpc_id,
        "subnets": resp.get("Subnets", [])
    }


# ============================================================
# DESCRIBE SPECIFIC SUBNET OR FILTER BY VPC
# ============================================================

def describe_subnet(params: DescribeSubnetParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    filters = []
    if params.vpc_id:
        filters.append({"Name": "vpc-id", "Values": [params.vpc_id]})

    if params.subnet_id:
        resp = ec2.describe_subnets(SubnetIds=[params.subnet_id])
    else:
        resp = ec2.describe_subnets(Filters=filters or None)

    return {
        "region": params.region,
        "subnets": resp.get("Subnets", [])
    }


# ============================================================
# REGISTER TOOLS
# ============================================================

tools = [
    FunctionTool(
        name="aws.list_vpcs",
        description="List all VPCs in a region.",
        fn=list_vpcs,
        parameters=RegionOnlyParams.model_json_schema()
    ),
    FunctionTool(
        name="aws.get_default_vpc",
        description="Get the default VPC in a region.",
        fn=get_default_vpc,
        parameters=RegionOnlyParams.model_json_schema()
    ),
    FunctionTool(
        name="aws.describe_vpc",
        description="Describe specific VPC or all VPCs.",
        fn=describe_vpc,
        parameters=DescribeVpcParams.model_json_schema()
    ),
    FunctionTool(
        name="aws.list_subnets",
        description="List all subnets in a region.",
        fn=list_subnets,
        parameters=RegionOnlyParams.model_json_schema()
    ),
    FunctionTool(
        name="aws.get_default_subnets",
        description="List all subnets that belong to the default VPC.",
        fn=get_default_subnets,
        parameters=RegionOnlyParams.model_json_schema()
    ),
    FunctionTool(
        name="aws.describe_subnet",
        description="Describe a subnet or list subnets in a specific VPC.",
        fn=describe_subnet,
        parameters=DescribeSubnetParams.model_json_schema()
    ),
]
