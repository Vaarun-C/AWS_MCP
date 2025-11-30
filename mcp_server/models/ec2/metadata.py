# mcp_server/models/ec2/metadata_models.py

from pydantic import BaseModel, Field
from typing import Optional, List

class GetUserDataParams(BaseModel):
    instance_id: str
    region: str = Field(default="ap-south-1")

class DescribeMetadataOptionsParams(BaseModel):
    instance_id: str
    region: str = Field(default="ap-south-1")

class ModifyMetadataOptionsParams(BaseModel):
    instance_id: str
    http_tokens: Optional[str] = Field(
        default=None, description="optional | required"
    )
    http_endpoint: Optional[str] = Field(
        default=None, description="disabled | enabled"
    )
    http_put_response_hop_limit: Optional[int] = Field(default=None)
    region: str = Field(default="ap-south-1")
