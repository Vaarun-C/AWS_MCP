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

base_url = "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

def scrape_service_docs(service_name: str) -> Dict:
    """
    Scrape documentation for a specific AWS service
    
    Args:
        service_name: AWS service (e.g., 'ec2', 's3', 'lambda')
    
    Returns:
        Dictionary with service documentation
    """
    
    url = f"{base_url}/{service_name}.html"
    
    try:
        print(f"Fetching documentation from {url}")
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract methods/operations
        methods = _extract_methods(soup, service_name)
        
        if not methods:
            print(f"Warning: No methods extracted for {service_name}. This might indicate a documentation format change.")
        
        # Extract examples
        examples = _extract_examples(soup)
        
        result = {
            'service': service_name,
            'url': url,
            'methods': methods,
            'examples': examples,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        print(f"Successfully scraped {len(methods)} methods and {len(examples)} examples for {service_name}")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Network error scraping {service_name}: {e}")
        return None
    except Exception as e:
        print(f"Error scraping {service_name}: {e}")
        import traceback
        traceback.print_exc()
        return None
    
def _extract_methods(soup: BeautifulSoup, service_name: str) -> List[Dict]:
    """Extract method signatures and descriptions"""
    methods = []
    
    # Try multiple approaches to find method definitions
    # Pattern 1: Standard boto3 format (e.g., EC2.Client.run_instances)
    method_sections = soup.find_all('dt', id=re.compile(rf'{service_name.upper()}\.Client\.\w+', re.IGNORECASE))
    
    # Pattern 2: If no matches, try more flexible pattern
    if not method_sections:
        method_sections = soup.find_all('dt', id=re.compile(r'Client\.\w+'))
    
    # Pattern 3: Find all dt tags with IDs containing both service and method patterns
    if not method_sections:
        all_dts = soup.find_all('dt', id=True)
        method_sections = [dt for dt in all_dts if 'Client.' in dt.get('id', '') and service_name.lower() in dt.get('id', '').lower()]
    
    # Pattern 4: Fallback - look for any method-like structures
    if not method_sections:
        all_dts = soup.find_all('dt', id=True)
        method_sections = [dt for dt in all_dts if '.Client.' in dt.get('id', '')]
    
    print(f"Found {len(method_sections)} method sections for {service_name}")
    
    for method_dt in method_sections:
        method_id = method_dt.get('id', '')
        method_name = method_id.split('.')[-1] if method_id else ''
        
        if not method_name:
            continue
        
        # Get method description
        dd = method_dt.find_next_sibling('dd')
        if not dd:
            continue
        
        description = ''
        desc_p = dd.find('p')
        if desc_p:
            description = desc_p.get_text(strip=True)
        
        # Extract parameters - try multiple selectors
        params = []
        param_list = dd.find('ul', class_='simple')
        if not param_list:
            param_list = dd.find('ul')
        
        if param_list:
            for li in param_list.find_all('li', recursive=False):
                param_text = li.get_text(strip=True)
                if param_text:
                    params.append(param_text)
        
        methods.append({
            'name': method_name,
            'description': description,
            'parameters': params,
            'service': service_name
        })
    
    return methods

def _extract_examples(soup: BeautifulSoup) -> List[str]:
    """Extract code examples from documentation"""
    examples = []
    
    # Try multiple selectors for code blocks
    code_block_selectors = [
        'div.highlight-python',
        'div.highlight',
        'pre.literal-block',
        'div.code'
    ]
    
    for selector in code_block_selectors:
        if '.' in selector:
            tag, class_name = selector.split('.', 1)
            blocks = soup.find_all(tag, class_=class_name)
        else:
            blocks = soup.find_all(selector)
        
        for block in blocks:
            code = block.get_text(strip=True)
            if code and len(code) > 20:  # Filter out very short snippets
                examples.append(code)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_examples = []
    for ex in examples:
        if ex not in seen:
            seen.add(ex)
            unique_examples.append(ex)
    
    return unique_examples[:10]  # Return max 10 examples


# Test the scraper
if __name__ == "__main__":
    service = "ec2"
    docs = scrape_service_docs(service)
    if docs:
        print(json.dumps(docs, indent=2))