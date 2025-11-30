# 🦾 AWS-MCP — An Open-Source Model Context Protocol Server for AWS

**AWS-MCP** is an open-source **Model Context Protocol (MCP)** server that exposes AWS services as *typed, safe, schema-driven tools* for LLMs.
It enables AI agents (GPT-4.1, Claude 3.5, Cursor, Replit Agents, Copilot-style systems) to interact with AWS infrastructure using natural language while remaining fully governed by IAM-controlled tool access.

⚡ **In short:**
**“Your AWS account, accessible through AI — but safely and with full structure.”**

---

## 🧠 Why This Project Exists

Modern LLMs are extremely capable at reasoning but blind when it comes to interacting with infrastructure.
MCP solves this by defining a universal protocol for exposing *tools* with strict schemas.

This project implements an **MCP server for AWS**, enabling:

* Inspecting EC2 instances
* Fetching CloudWatch metrics
* Exploring Lambdas, ECR images, ECS services
* Reading S3 objects
* (future) modifying infrastructure safely

…all through **structured tool calls**, not free-form prompts.

This is **NOT** a chatbot.
This is the *backend* that any LLM-powered agent can call to understand and manage AWS.

A separate repository will contain the chat interface and agentic orchestration layer.

---

# 🚀 Features & Current Progress

This MCP server provides 51 production-ready AWS tools across multiple services, all with typed schemas and FastMCP compatibility.

## ✅ EC2 Service — 32 Tools (Complete)

### Instance Management (10 tools)
* `ec2.list_instances` - List all EC2 instances with filters
* `ec2.describe_instances` - Get detailed instance information
* `ec2.start_instances` - Start stopped instances
* `ec2.stop_instances` - Stop running instances
* `ec2.reboot_instances` - Reboot instances
* `ec2.terminate_instances` - Terminate instances
* `ec2.create_instance` - Launch EC2 instances with full configuration
* `ec2.create_instance_minimal` - Quick instance creation
* `ec2.create_spot_instance` - Create spot instance requests
* `ec2.generate_instance_ssh_instruction` - Generate SSH connection commands

### KeyPair Management (3 tools)
* `ec2.create_keypair` - Create new EC2 key pairs
* `ec2.describe_keypairs` - List key pairs
* `ec2.delete_keypair` - Delete key pairs

### Security Groups (3 tools)
* `ec2.describe_security_groups` - List security groups
* `ec2.create_security_group` - Create new security groups
* `ec2.authorize_security_group_ingress` - Add inbound rules

### Launch Templates (6 tools)
* `ec2.create_launch_template` - Create reusable launch templates
* `ec2.create_launch_template_version` - Version launch templates
* `ec2.describe_launch_template` - Get template details
* `ec2.delete_launch_template` - Remove templates
* `ec2.list_launch_templates` - List all templates
* `ec2.launch_from_template` - Launch instances from templates

### AMI Management (3 tools)
* `ec2.create_ami` - Create AMI from instance
* `ec2.describe_images` - List and filter AMIs
* `ec2.deregister_ami` - Deregister AMIs

### Metadata & Pricing (6 tools)
* `ec2.get_user_data` - Fetch instance user-data scripts
* `ec2.describe_metadata_options` - Get IMDS settings
* `ec2.modify_metadata_options` - Modify IMDS configuration
* `ec2.get_ondemand_price` - Get on-demand pricing
* `ec2.get_spot_price_history` - Spot price history
* `ec2.estimate_instance_cost` - Calculate monthly costs

### VPC Integration (1 tool)
* `ec2.get_instance_vpc_info` - Get VPC/subnet details for instances

## ✅ EBS (Elastic Block Store) — 13 Tools (Complete)

### Volume Management (4 tools)
* `ebs.create_volume` - Create EBS volumes
* `ebs.modify_volume` - Modify volume size/type/IOPS
* `ebs.delete_volume` - Delete volumes
* `ebs.describe_volumes` - List and filter volumes

### Volume Attachments (2 tools)
* `ebs.attach_volume` - Attach volumes to instances
* `ebs.detach_volume` - Detach volumes from instances

### Snapshot Management (7 tools)
* `ebs.create_snapshot` - Create volume snapshots
* `ebs.delete_snapshot` - Delete snapshots
* `ebs.list_snapshots` - List with filters
* `ebs.describe_snapshot` - Get snapshot details
* `ebs.copy_snapshot` - Copy snapshots across regions
* `ebs.restore_volume_from_snapshot` - Create volumes from snapshots
* `ebs.get_snapshot_progress` - Track snapshot creation progress

## ✅ VPC (Virtual Private Cloud) — 6 Tools (Complete)

* `vpc.list_vpcs` - List all VPCs in region
* `vpc.get_default_vpc` - Get default VPC
* `vpc.describe_vpc` - Describe specific VPC
* `vpc.list_subnets` - List all subnets
* `vpc.get_default_subnets` - Get default VPC subnets
* `vpc.describe_subnet` - Describe subnet details

## 🔄 CloudWatch — In Progress

* Metric retrieval for EC2, Lambda, ECS
* Custom metric queries
* Alarm management (planned)

## 🔧 Lambda — In Progress

* Function listing and configuration
* Invocation and logs (planned)

## 📦 ECR — Planned

* Repository management
* Image listing and tagging

## 🐳 ECS — Planned

* Cluster and service management
* Task descriptions

## 📁 S3 — Planned

* Bucket and object operations
* Safe read-only access

---

# 🏗️ Architecture Overview

The server is designed with **clean modular boundaries**, strong typing (Pydantic v2), and production-ready service abstraction.

```
aws-mcp/
│
├── mcp_server/
│   ├── core/              # MCP scaffolding & registry
│   │   ├── config.py      # Configuration management
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── registry.py    # Tool registration system
│   │
│   ├── aws/               # Boto3 wrapper clients
│   │   ├── ec2_client.py
│   │   ├── cloudwatch_client.py
│   │   ├── lambda_client.py
│   │   ├── ecr_client.py
│   │   ├── ecs_client.py
│   │   ├── s3_client.py
│   │   └── iam_client.py
│   │
│   ├── models/            # Pydantic v2 schemas (modularized)
│   │   ├── ec2/           # EC2 models by functionality
│   │   │   ├── list.py
│   │   │   ├── lifecycle.py
│   │   │   ├── creation.py
│   │   │   ├── keypair.py
│   │   │   ├── security_group.py
│   │   │   ├── launch_templates.py
│   │   │   ├── ami.py
│   │   │   ├── metadata.py
│   │   │   └── pricing.py
│   │   ├── ebs/           # EBS models
│   │   │   ├── volume.py
│   │   │   ├── attachment.py
│   │   │   └── snapshot_models.py
│   │   ├── vpc/           # VPC models
│   │   ├── cloudwatch.py
│   │   ├── lambda_.py
│   │   └── common.py
│   │
│   ├── tools/             # FastMCP tools (kwargs-based)
│   │   ├── ec2/           # EC2 tools by functionality
│   │   │   ├── list.py
│   │   │   ├── instance_lifecycle.py
│   │   │   ├── instance_creation.py
│   │   │   ├── keypair.py
│   │   │   ├── security_groups.py
│   │   │   ├── preparation.py
│   │   │   ├── launch_templates.py
│   │   │   ├── ami.py
│   │   │   ├── metadata.py
│   │   │   └── pricing.py
│   │   ├── ebs/           # EBS tools
│   │   │   ├── volume_tools.py
│   │   │   ├── attachment_tools.py
│   │   │   └── snapshot_tools.py
│   │   ├── vpc/
│   │   │   └── describe_vpc.py
│   │   ├── cloudwatch_tools.py
│   │   ├── lambda_tools.py
│   │   └── s3_tools.py
│   │
│   └── utils/             # Logging, validation, helpers
│       ├── logging.py
│       ├── validators.py
│       └── responses.py
│
├── TOOLS_CHECKLIST/       # Tool documentation
│   └── EC2_TOOLKIT.md
├── server.py              # FastMCP server entry point
├── fastmcp.json           # MCP configuration
└── README.md
```

### 🔹 **Core Design Choices**

* **Service-based organization**: Tools grouped by AWS service (EC2, EBS, VPC)
* **Modular architecture**: Models and tools split by functionality for maintainability
* **FastMCP compatibility**: All tools use keyword arguments instead of Pydantic params
* **Pydantic v2 models**: Strong typing for schemas, used via `model_json_schema()`
* **Tool naming convention**: `service.operation` (e.g., `ec2.create_instance`, `ebs.create_volume`)
* **Explicit registry**: Service-level tool loading prevents duplicates
* **Type-safe parameters**: Full type hints with Optional, List, Dict from typing module
* **Default regions**: All tools default to `ap-south-1` or environment-configured region
* **Clean separation**: AWS clients → Pydantic models → Tool functions → Registry

---

# ⚙️ How It Works

1. The MCP server registers multiple **tools** (functions) with schemas.
2. An LLM (like GPT-4.1) receives these tool definitions.
3. You ask a natural language question:

   > “Show me all EC2 instances in us-east-1.”
4. The LLM chooses the correct tool and calls it with parameters.
5. The MCP server executes AWS APIs via boto3 wrappers.
6. The tool returns **structured JSON** back to the LLM.
7. The LLM interprets the structure and answers the user.

This is the same architecture used by:

* AI agents in Cloud IDEs
* Cursor / Replit Agents
* OpenAI’s internal GPT tool-calling
* GitHub Copilot Workspace

---

# 🔐 IAM Permissions

The server requires specific AWS IAM permissions based on which tools you use. Below are the minimum permissions needed:

### **EC2 Tools (32 tools)**

```yaml
# Instance operations
ec2:DescribeInstances
ec2:RunInstances
ec2:StartInstances
ec2:StopInstances
ec2:RebootInstances
ec2:TerminateInstances
ec2:DescribeInstanceAttribute

# KeyPair management
ec2:CreateKeyPair
ec2:DescribeKeyPairs
ec2:DeleteKeyPair

# Security Groups
ec2:DescribeSecurityGroups
ec2:CreateSecurityGroup
ec2:AuthorizeSecurityGroupIngress

# Launch Templates
ec2:CreateLaunchTemplate
ec2:CreateLaunchTemplateVersion
ec2:DescribeLaunchTemplates
ec2:DeleteLaunchTemplate

# AMI management
ec2:CreateImage
ec2:DescribeImages
ec2:DeregisterImage

# Metadata
ec2:ModifyInstanceMetadataOptions

# VPC
ec2:DescribeVpcs
ec2:DescribeSubnets
```

### **EBS Tools (13 tools)**

```yaml
# Volume operations
ec2:CreateVolume
ec2:ModifyVolume
ec2:DeleteVolume
ec2:DescribeVolumes
ec2:AttachVolume
ec2:DetachVolume

# Snapshot operations
ec2:CreateSnapshot
ec2:DeleteSnapshot
ec2:DescribeSnapshots
ec2:CopySnapshot
```

### **CloudWatch Tools**

```yaml
cloudwatch:GetMetricData
cloudwatch:GetMetricStatistics
cloudwatch:ListMetrics
```

### **Future Services (Optional)**

* Lambda: `lambda:ListFunctions`, `lambda:GetFunctionConfiguration`, `lambda:InvokeFunction`
* ECS: `ecs:ListClusters`, `ecs:ListServices`, `ecs:DescribeServices`, `ecs:DescribeTasks`
* ECR: `ecr:DescribeRepositories`, `ecr:ListImages`, `ecr:DescribeImages`
* S3: `s3:ListBucket`, `s3:GetObject` (read-only)

### **Pricing API**

For EC2 pricing tools, the Pricing API requires `us-east-1` region:
```yaml
pricing:GetProducts
```

**Note**: Destructive operations (terminate, delete) are included but should be carefully controlled via IAM policies in production.

---

# 🛠️ Installation & Setup

### Prerequisites

* Python 3.10+
* AWS credentials configured (`~/.aws/credentials` or environment variables)
* Boto3 installed

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/thejasrao262003/AWS_MCP.git
   cd AWS_MCP
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**:
   ```bash
   aws configure
   # Or set environment variables:
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=ap-south-1
   ```

4. **Run the MCP server**:
   ```bash
   python server.py
   ```

### Configuration

The server uses `fastmcp.json` for MCP configuration. You can customize:
* Default AWS region
* Tool registration
* Server settings

Example `fastmcp.json`:
```json
{
  "name": "aws-mcp",
  "version": "0.1.0",
  "description": "AWS Model Context Protocol Server"
}
```

---

# 🧩 Example Usage

### Using Tools Directly

```python
from mcp_server.tools.ec2.list import list_instances

# List all running instances
result = list_instances(
    region="ap-south-1",
    state="running"
)

print(result)
```

### Creating an EC2 Instance

```python
from mcp_server.tools.ec2.instance_creation import create_instance_minimal

# Launch a simple EC2 instance
result = create_instance_minimal(
    ImageId="ami-0c55b159cbfafe1f0",
    InstanceType="t2.micro",
    KeyName="my-keypair",
    region="ap-south-1"
)

print(f"Instance created: {result['instance_id']}")
```

### Managing EBS Volumes

```python
from mcp_server.tools.ebs.volume_tools import create_volume
from mcp_server.tools.ebs.attachment_tools import attach_volume

# Create a 100GB gp3 volume
volume = create_volume(
    AvailabilityZone="ap-south-1a",
    Size=100,
    VolumeType="gp3",
    region="ap-south-1"
)

# Attach it to an instance
attach_volume(
    VolumeId=volume['VolumeId'],
    InstanceId="i-1234567890abcdef0",
    Device="/dev/sdf",
    region="ap-south-1"
)
```

### Getting Instance Pricing

```python
from mcp_server.tools.ec2.pricing import get_ondemand_price, estimate_instance_cost

# Get hourly price for t3.medium
pricing = get_ondemand_price(
    instance_type="t3.medium",
    operating_system="Linux",
    region="ap-south-1"
)

# Estimate monthly cost for 24/7 usage
estimate = estimate_instance_cost(
    instance_type="t3.medium",
    hours_per_month=730,
    region="ap-south-1"
)
```

### Working with VPCs

```python
from mcp_server.tools.vpc.describe_vpc import get_default_vpc, get_default_subnets

# Get default VPC
vpc = get_default_vpc(region="ap-south-1")

# Get all subnets in default VPC
subnets = get_default_subnets(region="ap-south-1")
```

### Using with LLM Tool Calling

```python
# The MCP server exposes tools that can be called by LLMs
# Tools are automatically registered with FastMCP

# Example with OpenAI:
import openai

response = openai.chat.completions.create(
    model="gpt-4o",
    tools=mcp_tools,  # Auto-generated from FastMCP
    messages=[{
        "role": "user", 
        "content": "List all running EC2 instances in Mumbai region"
    }]
)
```

---

# 📘 Documentation

The `docs/` directory will contain:

* **architecture.md** — Full server architecture
* **roadmap.md** — Release plan & services
* **tools.md** — MCP tool specs
* **contributing.md** — How to contribute

---

# 🧭 Roadmap & Progress

### ✅ **v0.1.0 (Current) - EC2 & EBS Foundation**

* ✅ 32 EC2 tools (instances, keypairs, security groups, AMIs, launch templates, pricing, metadata)
* ✅ 13 EBS tools (volumes, snapshots, attachments)
* ✅ 6 VPC tools (VPCs, subnets)
* ✅ Modular Pydantic v2 models
* ✅ FastMCP compatibility (kwargs-based tool functions)
* ✅ Service-based tool organization
* ✅ Clean registry system
* 🔄 CloudWatch metrics (in progress)

### **v0.2.0 (Next) - Lambda & Container Services**

* Lambda function management
* Lambda invocation and logs
* ECR repository and image management
* ECS cluster and service operations
* Enhanced CloudWatch integration

### **v0.3.0 - Storage & Additional Services**

* S3 bucket and object operations
* IAM role and policy inspection
* RDS instance management
* DynamoDB table operations

### **v0.4.0 - Advanced Features**

* Cost optimization recommendations
* Resource tagging automation
* Multi-region operations
* Batch operations support

### **v1.0.0 - Production Ready**

* Comprehensive test suite (unit + integration)
* Full documentation
* CI/CD pipelines
* Performance optimization
* Security hardening
* PyPI package publication
* Docker container support

---

# 🤝 Contributing

Contributions are welcome!

You can:

* Add a new AWS service
* Create Pydantic models
* Write tools
* Improve tests
* Add documentation
* Suggest improvements

See [`docs/contributing.md`](docs/contributing.md) for guidelines.

---

# 📜 License

MIT License

---

# ⭐ Support the Project

If this project helps you or your team, please consider starring the repo — it helps the project grow and reach more developers.

---

# 🙌 Acknowledgements

Built with:

* **AWS SDK** - boto3 for AWS API interactions
* **FastMCP** - Model Context Protocol framework
* **Pydantic v2** - Data validation and schema generation
* **Python 3.10+** - Modern Python features and type hints

Special thanks to:
* The MCP community for the protocol specification
* AWS for comprehensive API documentation
* Contributors and early adopters

---

# 📊 Project Statistics

* **Total Tools**: 51
* **AWS Services**: 3 (EC2, EBS, VPC) + 2 in progress (CloudWatch, Lambda)
* **Model Classes**: 40+ Pydantic models
* **Architecture**: Fully modular, production-ready design
* **Type Safety**: 100% type-hinted with strict Pydantic validation