# mcp_server/models/ec2/vpc_models.py

from typing import Optional, List
from pydantic import BaseModel, Field


class RegionOnlyParams(BaseModel):
    region: str = Field(default="ap-south-1")


class DescribeVpcParams(BaseModel):
    region: str = "ap-south-1"
    vpc_id: Optional[str] = None


class DescribeSubnetParams(BaseModel):
    region: str = "ap-south-1"
    subnet_id: Optional[str] = None
    vpc_id: Optional[str] = None
