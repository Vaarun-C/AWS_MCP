# mcp_server/models/ec2/pricing_models.py

from pydantic import BaseModel, Field
from typing import Optional, List


class EC2OnDemandPriceParams(BaseModel):
    instance_type: str
    operating_system: str = Field(
        default="Linux",
        description="Linux | Windows | RHEL | SUSE | Ubuntu"
    )
    region: str = Field(default="ap-south-1")


class SpotPriceHistoryParams(BaseModel):
    instance_type: str
    product_description: str = Field(
        default="Linux/UNIX",
        description="Linux/UNIX | Windows | Linux/UNIX (Amazon VPC) | Windows (Amazon VPC)"
    )
    region: str = Field(default="ap-south-1")
    start_time: Optional[str] = Field(default=None)
    end_time: Optional[str] = Field(default=None)
    availability_zone: Optional[str] = None


class EC2CostEstimateParams(BaseModel):
    instance_type: str
    hours_per_month: int = Field(default=720)
    operating_system: str = "Linux"
    region: str = Field(default="ap-south-1")
