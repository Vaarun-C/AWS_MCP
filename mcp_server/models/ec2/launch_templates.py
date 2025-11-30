"""Models for EC2 Launch Template operations."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# -----------------------------------
# SHARED SUB-MODELS
# -----------------------------------

class LaunchTemplateTag(BaseModel):
    Key: str
    Value: str


class LaunchTemplateBlockDeviceEBS(BaseModel):
    VolumeSize: Optional[int] = None
    VolumeType: Optional[str] = None
    DeleteOnTermination: Optional[bool] = None
    Encrypted: Optional[bool] = None
    SnapshotId: Optional[str] = None


class LaunchTemplateBlockDevice(BaseModel):
    DeviceName: str
    Ebs: Optional[LaunchTemplateBlockDeviceEBS] = None


class LaunchTemplateNetworkInterface(BaseModel):
    DeviceIndex: int
    SubnetId: Optional[str] = None
    Description: Optional[str] = None
    Groups: Optional[List[str]] = None
    DeleteOnTermination: Optional[bool] = None
    AssociatePublicIpAddress: Optional[bool] = None


# -----------------------------------
# MAIN CREATE / UPDATE MODELS
# -----------------------------------

class CreateLaunchTemplateParams(BaseModel):
    region: str = Field(default="ap-south-1")

    LaunchTemplateName: str = Field(..., description="Name of the launch template")
    VersionDescription: Optional[str] = None

    ImageId: str = Field(..., description="AMI ID")
    InstanceType: str = Field(..., description="Instance type")

    KeyName: Optional[str] = None
    SecurityGroupIds: Optional[List[str]] = None
    SubnetId: Optional[str] = None

    UserData: Optional[str] = Field(
        default=None,
        description="UserData script (plain text, will be base64-encoded)"
    )

    TagSpecifications: Optional[List[Dict[str, Any]]] = None
    BlockDeviceMappings: Optional[List[LaunchTemplateBlockDevice]] = None
    NetworkInterfaces: Optional[List[LaunchTemplateNetworkInterface]] = None

    IamInstanceProfile: Optional[Dict[str, str]] = None
    MetadataOptions: Optional[Dict[str, Any]] = None

    ExtraParams: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Any additional AWS run/launch template fields"
    )


class CreateLaunchTemplateVersionParams(BaseModel):
    region: str = Field(default="ap-south-1")
    LaunchTemplateName: str
    VersionDescription: Optional[str] = None

    # Same configs as create template
    ImageId: Optional[str] = None
    InstanceType: Optional[str] = None
    KeyName: Optional[str] = None
    SecurityGroupIds: Optional[List[str]] = None
    SubnetId: Optional[str] = None
    UserData: Optional[str] = None
    TagSpecifications: Optional[List[Dict[str, Any]]] = None
    BlockDeviceMappings: Optional[List[LaunchTemplateBlockDevice]] = None
    NetworkInterfaces: Optional[List[LaunchTemplateNetworkInterface]] = None
    IamInstanceProfile: Optional[Dict[str, str]] = None
    MetadataOptions: Optional[Dict[str, Any]] = None
    ExtraParams: Optional[Dict[str, Any]] = None


class LaunchFromTemplateParams(BaseModel):
    region: str = Field(default="ap-south-1")
    LaunchTemplateName: str
    Version: Optional[str] = "$Latest"
    MinCount: int = 1
    MaxCount: int = 1


class DescribeLaunchTemplateParams(BaseModel):
    region: str = Field(default="ap-south-1")
    LaunchTemplateName: Optional[str] = None
    LaunchTemplateId: Optional[str] = None


class DeleteLaunchTemplateParams(BaseModel):
    region: str = Field(default="ap-south-1")
    LaunchTemplateName: Optional[str] = None
    LaunchTemplateId: Optional[str] = None
