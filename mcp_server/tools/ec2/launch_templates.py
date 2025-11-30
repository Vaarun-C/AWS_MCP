from mcp_server.models.ec2.launch_templates import (
    CreateLaunchTemplateParams,
    CreateLaunchTemplateVersionParams,
    DescribeLaunchTemplateParams,
    DeleteLaunchTemplateParams,
    LaunchFromTemplateParams
)
import boto3
import base64
from fastmcp.tools import FunctionTool


def create_launch_template(params: CreateLaunchTemplateParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    lt_data = {
        "ImageId": params.ImageId,
        "InstanceType": params.InstanceType,
    }

    if params.KeyName:
        lt_data["KeyName"] = params.KeyName

    if params.SecurityGroupIds:
        lt_data["SecurityGroupIds"] = params.SecurityGroupIds

    if params.SubnetId:
        lt_data["SubnetId"] = params.SubnetId

    if params.UserData:
        lt_data["UserData"] = base64.b64encode(params.UserData.encode()).decode()

    if params.TagSpecifications:
        lt_data["TagSpecifications"] = params.TagSpecifications

    if params.BlockDeviceMappings:
        lt_data["BlockDeviceMappings"] = [bd.dict() for bd in params.BlockDeviceMappings]

    if params.NetworkInterfaces:
        lt_data["NetworkInterfaces"] = [ni.dict() for ni in params.NetworkInterfaces]

    if params.IamInstanceProfile:
        lt_data["IamInstanceProfile"] = params.IamInstanceProfile

    if params.MetadataOptions:
        lt_data["MetadataOptions"] = params.MetadataOptions

    if params.ExtraParams:
        lt_data.update(params.ExtraParams)

    resp = ec2.create_launch_template(
        LaunchTemplateName=params.LaunchTemplateName,
        VersionDescription=params.VersionDescription,
        LaunchTemplateData=lt_data
    )
    return resp


# ================================================
# CREATE NEW VERSION
# ================================================

def create_launch_template_version(params: CreateLaunchTemplateVersionParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    lt_data = {}

    # Only include provided fields
    allowed_fields = [
        "ImageId", "InstanceType", "KeyName", "SecurityGroupIds",
        "SubnetId", "UserData", "TagSpecifications", "BlockDeviceMappings",
        "NetworkInterfaces", "IamInstanceProfile", "MetadataOptions"
    ]

    for field in allowed_fields:
        value = getattr(params, field)
        if value is not None:
            if field == "UserData":
                lt_data[field] = base64.b64encode(value.encode()).decode()
            elif field == "BlockDeviceMappings":
                lt_data[field] = [bd.dict() for bd in value]
            elif field == "NetworkInterfaces":
                lt_data[field] = [ni.dict() for ni in value]
            else:
                lt_data[field] = value

    if params.ExtraParams:
        lt_data.update(params.ExtraParams)

    resp = ec2.create_launch_template_version(
        LaunchTemplateName=params.LaunchTemplateName,
        VersionDescription=params.VersionDescription,
        LaunchTemplateData=lt_data
    )

    return resp


# ================================================
# DESCRIBE TEMPLATE
# ================================================

def describe_launch_template(params: DescribeLaunchTemplateParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    if params.LaunchTemplateId:
        return ec2.describe_launch_templates(
            LaunchTemplateIds=[params.LaunchTemplateId]
        )
    else:
        return ec2.describe_launch_templates(
            LaunchTemplateNames=[params.LaunchTemplateName]
        )


# ================================================
# DELETE TEMPLATE
# ================================================

def delete_launch_template(params: DeleteLaunchTemplateParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    if params.LaunchTemplateId:
        return ec2.delete_launch_template(
            LaunchTemplateId=params.LaunchTemplateId
        )
    else:
        return ec2.delete_launch_template(
            LaunchTemplateName=params.LaunchTemplateName
        )


# ================================================
# LIST ALL TEMPLATES
# ================================================

def list_launch_templates(region: str = "ap-south-1"):
    ec2 = boto3.client("ec2", region_name=region)
    return ec2.describe_launch_templates()


# ================================================
# LAUNCH INSTANCE FROM TEMPLATE
# ================================================

def launch_from_template(params: LaunchFromTemplateParams):
    ec2 = boto3.client("ec2", region_name=params.region)

    resp = ec2.run_instances(
        LaunchTemplate={
            "LaunchTemplateName": params.LaunchTemplateName,
            "Version": params.Version or "$Latest"
        },
        MinCount=params.MinCount,
        MaxCount=params.MaxCount
    )

    return resp

tools = [
    FunctionTool(
        name="aws.create_launch_template",
        description="Create a new EC2 Launch Template",
        fn=create_launch_template,
        parameters=CreateLaunchTemplateParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.create_launch_template_version",
        description="Create a new version of an existing launch template",
        fn=create_launch_template_version,
        parameters=CreateLaunchTemplateVersionParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.describe_launch_template",
        description="Describe an EC2 launch template",
        fn=describe_launch_template,
        parameters=DescribeLaunchTemplateParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.delete_launch_template",
        description="Delete an EC2 launch template",
        fn=delete_launch_template,
        parameters=DeleteLaunchTemplateParams.model_json_schema(),
    ),
    FunctionTool(
        name="aws.list_launch_templates",
        description="List all EC2 launch templates in a region",
        fn=list_launch_templates,
        parameters={"type": "object", "properties": {"region": {"type": "string"}}}
    ),
    FunctionTool(
        name="aws.launch_from_template",
        description="Launch an EC2 instance using an AWS Launch Template",
        fn=launch_from_template,
        parameters=LaunchFromTemplateParams.model_json_schema(),
    ),
]
