import os
import json
import re
import asyncio
from typing import Dict, List, Set
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from fastmcp import FastMCP
import boto3
from dotenv import load_dotenv
from utils import scrape_service_docs

load_dotenv()

mcp = FastMCP("AWS Auto-Doc Server")

RESOURCES_DIR = Path("./aws_resources")
RESOURCES_DIR.mkdir(exist_ok=True)

resource_index = {}

class ResourceManager:
    """Manages FastMCP resources and determines when to scrape"""
    
    def __init__(self):
        self.load_resource_index()
    
    def load_resource_index(self):
        """Load existing resource index from disk"""
        global resource_index
        
        index_file = RESOURCES_DIR / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                resource_index = json.load(f)
        else:
            resource_index = {}
    
    def save_resource_index(self):
        """Save resource index to disk"""
        index_file = RESOURCES_DIR / "index.json"
        with open(index_file, 'w') as f:
            json.dump(resource_index, f, indent=2)
    
    def check_resources_for_query(self, query: str) -> Dict[str, bool]:
        """
        Check if we have sufficient resources for a query
        
        Args:
            query: User query (e.g., "Create a t2.micro instance connected to S3")
        
        Returns:
            Dict mapping service -> has_sufficient_resources
        """
        # Extract AWS services from query
        services = self._extract_services_from_query(query)
        
        result = {}
        for service in services:
            # Check if we have resources for this service
            has_resources = service in resource_index
            
            if has_resources:
                # Check if resources are recent (less than 7 days old)
                timestamp = resource_index[service].get('timestamp', 0)
                age_days = (asyncio.get_event_loop().time() - timestamp) / 86400
                has_resources = age_days < 7
            
            result[service] = has_resources
        
        return result
    
    def _extract_services_from_query(self, query: str) -> Set[str]:
        """Extract AWS service names from a query"""
        query_lower = query.lower()
        
        # Common service keywords
        service_patterns = {
            'ec2': ['ec2', 'instance', 't2.micro', 't2.small', 'virtual machine', 'vm', 'server'],
            's3': ['s3', 'bucket', 'storage', 'object storage'],
            'lambda': ['lambda', 'function', 'serverless'],
            'rds': ['rds', 'database', 'mysql', 'postgres'],
            'dynamodb': ['dynamodb', 'nosql', 'table'],
            'sqs': ['sqs', 'queue', 'message queue'],
            'sns': ['sns', 'notification', 'topic'],
            'iam': ['iam', 'role', 'user', 'policy', 'permission'],
            'vpc': ['vpc', 'network', 'subnet'],
            'elb': ['elb', 'load balancer', 'alb', 'nlb']
        }
        
        detected_services = set()
        for service, keywords in service_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_services.add(service)
        
        return detected_services
    
    async def ensure_resources(self, services: List[str]) -> Dict[str, str]:
        """
        Ensure resources exist for given services, scraping if necessary
        
        Args:
            services: List of AWS service names
        
        Returns:
            Dict mapping service -> resource_uri
        """
        results = {}
        
        for service in services:
            if service not in resource_index or self._is_stale(service):
                print(f"Scraping documentation for {service}...")
                
                # Scrape documentation
                docs = scrape_service_docs(service)

                print(docs)
                
                if docs:
                    # Save to disk
                    resource_file = RESOURCES_DIR / f"{service}_docs.json"
                    with open(resource_file, 'w') as f:
                        json.dump(docs, f, indent=2)
                    
                    # Update index
                    resource_index[service] = {
                        'file': str(resource_file),
                        'timestamp': docs['timestamp'],
                        'method_count': len(docs['methods'])
                    }
                    
                    # Register as MCP resource
                    self._register_resource(service, resource_file)
                    
                    results[service] = f"aws://{service}/docs"
                else:
                    results[service] = None
            else:
                results[service] = f"aws://{service}/docs"
        
        self.save_resource_index()
        return results
    
    def _is_stale(self, service: str) -> bool:
        """Check if service documentation is stale (>7 days old)"""
        if service not in resource_index:
            return True
        
        timestamp = resource_index[service].get('timestamp', 0)
        age_days = (asyncio.get_event_loop().time() - timestamp) / 86400
        return age_days > 7
    
    def _register_resource(self, service: str, resource_file: Path):
        """Register a resource with FastMCP dynamically"""
        # This would need FastMCP to support dynamic resource registration
        # For now, we'll store it in our index and make it available via tools
        pass


# Initialize scraper and resource manager
resource_manager = ResourceManager()

# MCP Tools

@mcp.tool()
async def check_aws_resources(query: str) -> dict:
    """
    Check if sufficient AWS documentation resources exist for a query.
    If not, identifies which services need documentation scraped.
    
    Args:
        query: The user's AWS-related query
    
    Returns:
        Dict with services and their resource status
    """
    resource_status = resource_manager.check_resources_for_query(query)
    
    missing_services = [svc for svc, has_res in resource_status.items() if not has_res]
    
    return {
        'query': query,
        'detected_services': list(resource_status.keys()),
        'resource_status': resource_status,
        'needs_scraping': missing_services,
        'has_all_resources': len(missing_services) == 0
    }


@mcp.tool()
async def scrape_aws_documentation(services: list) -> dict:
    """
    Scrape AWS SDK documentation for specified services and create MCP resources.
    
    Args:
        services: List of AWS service names (e.g., ['ec2', 's3'])
    
    Returns:
        Dict with scraping results and resource URIs
    """
    results = await resource_manager.ensure_resources(services)
    
    return {
        'scraped_services': services,
        'resources': results,
        'resource_count': len([r for r in results.values() if r])
    }


@mcp.tool()
async def get_aws_service_methods(service: str) -> dict:
    """
    Get all available methods/operations for an AWS service.
    Scrapes documentation if not already cached.
    
    Args:
        service: AWS service name (e.g., 'ec2', 's3')
    
    Returns:
        Dict with service methods and their descriptions
    """
    # Ensure we have resources
    await resource_manager.ensure_resources([service])
    
    # Load from disk
    resource_file = RESOURCES_DIR / f"{service}_docs.json"
    if resource_file.exists():
        with open(resource_file, 'r') as f:
            docs = json.load(f)
        
        return {
            'service': service,
            'method_count': len(docs['methods']),
            'methods': docs['methods'][:20],  # Return first 20 methods
            'documentation_url': docs['url']
        }
    
    return {'error': f'Could not load documentation for {service}'}


@mcp.tool()
async def execute_aws_operation(
    service: str,
    operation: str,
    parameters: dict = None  # ← CHANGED: Made optional with default None
) -> dict:
    """
    Execute an AWS SDK operation with given parameters.
    The region is automatically configured from environment variables (AWS_REGION).
    Do NOT include 'region' in the parameters dict.
    
    Args:
        service: AWS service name (e.g., 'ec2')
        operation: Operation name (e.g., 'describe_instances')
        parameters: Dict of parameters for the operation (do NOT include region here).
                   Optional - defaults to empty dict for operations that don't need parameters.
    
    Returns:
        Result of the AWS operation
    """
    try:
        # Handle None parameters
        if parameters is None:
            parameters = {}
        
        # CRITICAL FIX: Remove 'region' from parameters if present
        # Region should ONLY be set when creating the client, not passed to methods
        clean_params = {k: v for k, v in parameters.items() if k.lower() not in ['region', 'region_name']}
        
        if len(clean_params) != len(parameters):
            print(f"Warning: Removed region parameter from {operation} call. Region is set via environment.")
        
        # Get region from environment
        region = os.getenv('AWS_REGION', 'ap-south-1')
        
        print(f"Creating {service} client in region: {region}")
        print(f"Calling {operation} with parameters: {clean_params}")
        
        # Create boto3 client with region from environment
        client = boto3.client(
            service,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=region
        )
        
        # Execute operation with cleaned parameters
        method = getattr(client, operation)
        result = method(**clean_params)
        
        # Convert datetime objects to strings for JSON serialization
        result_str = json.loads(json.dumps(result, default=str))
        
        return {
            'success': True,
            'service': service,
            'operation': operation,
            'region': region,
            'result': result_str
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error executing {service}.{operation}: {error_details}")
        
        return {
            'success': False,
            'service': service,
            'operation': operation,
            'error': str(e),
            'error_details': error_details
        }

@mcp.tool()
async def list_available_resources() -> dict:
    """
    List all available AWS documentation resources.
    
    Returns:
        Dict with all cached AWS service documentation
    """
    return {
        'resource_count': len(resource_index),
        'services': list(resource_index.keys()),
        'resources': resource_index
    }


# MCP Resources (static examples - dynamic registration would be better)

@mcp.resource("aws://ec2/docs")
async def get_ec2_docs() -> str:
    """EC2 service documentation"""
    resource_file = RESOURCES_DIR / "ec2_docs.json"
    if resource_file.exists():
        with open(resource_file, 'r') as f:
            return json.dumps(json.load(f), indent=2)
    return json.dumps({'error': 'EC2 docs not yet scraped'})


@mcp.resource("aws://s3/docs")
async def get_s3_docs() -> str:
    """S3 service documentation"""
    resource_file = RESOURCES_DIR / "s3_docs.json"
    if resource_file.exists():
        with open(resource_file, 'r') as f:
            return json.dumps(json.load(f), indent=2)
    return json.dumps({'error': 'S3 docs not yet scraped'})


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="http", host="127.0.0.1", port=8000)