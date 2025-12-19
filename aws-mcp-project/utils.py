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
import re

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
    
def _extract_methods_and_their_urls(soup: BeautifulSoup) -> List[Dict]:
    """Extract method signatures and descriptions"""
    client_section = soup.find(id="client")
    method_element_list = client_section.find_all("li", {"class": "toctree-l1"})
    methods = [
        {
            "name": method.get_text(),
            "url": method.find("a", {}).get("href")
        }
        for method in method_element_list
    ]
    
    return methods

def _extract_method_details(soup: BeautifulSoup, method_name: str, service_name: str) -> Dict:
    """Extract method details from a specific method page"""
    
    method_section = soup.find("dd", {"class": "sig-object py"})
    if not method_section:
        method_section = soup.find("dd")
    
    method_description = method_section.find("p")
    description_text = method_description.get_text(strip=True) if method_description else ""

    code_blocks = method_section.find_all("div", {"class": "highlight"})
    request_syntax = code_blocks[0].get_text(strip=True) if code_blocks else ""
    response_syntax = code_blocks[1].get_text(strip=True) if len(code_blocks) > 1 else ""
    
    # Extract parameters
    parameters = []
    field_list = method_section.find("dl", {"class": "field-list simple"})
    
    if field_list:
        field_items = field_list.find_all("dd", recursive=False)
        
        for dd in field_items:
            prev_dt = dd.find_previous_sibling("dt")
            if prev_dt and "Parameters" in prev_dt.get_text():
                # Extract parameter list
                param_list = dd.find("ul", {"class": "simple"})
                if param_list:
                    for param_item in param_list.find_all("li", recursive=False):
                        param_info = {}

                        main_p = param_item.find("p")
                        if not main_p:
                            continue
                        
                        # Extract parameter name and type from the strong and em tags
                        strong_tag = main_p.find("strong")
                        if strong_tag:
                            param_info['name'] = strong_tag.get_text(strip=True)
                        
                        em_tag = main_p.find("em")
                        if em_tag:
                            param_info['type'] = em_tag.get_text(strip=True)
                        
                        # Extract all text from the main paragraph and all sibling paragraphs
                        description_parts = []
                        
                        # Get text from the first paragraph (after name and type)
                        # Use get_text() to get all text including <span> content
                        first_p_text = main_p.get_text(separator=' ', strip=True)
                        
                        # Remove the name and type parts
                        if strong_tag:
                            first_p_text = first_p_text.replace(strong_tag.get_text(strip=True), '', 1)
                        if em_tag:
                            first_p_text = first_p_text.replace(em_tag.get_text(strip=True), '', 1)
                        
                        # Clean up the dash separator
                        first_p_text = first_p_text.strip()
                        if first_p_text.startswith('–') or first_p_text.startswith('-') or first_p_text.startswith('—'):
                            first_p_text = first_p_text[1:].strip()
                        
                        if first_p_text:
                            description_parts.append(first_p_text)
                        
                        # Get all sibling <p> tags (including those after nested lists)
                        for sibling in main_p.find_next_siblings():
                            if sibling.name == 'p':
                                sibling_text = sibling.get_text(separator=' ', strip=True)
                                if sibling_text:
                                    description_parts.append(sibling_text)
                            elif sibling.name == 'ul':
                                # Continue past nested lists - don't stop
                                continue
                        
                        # Join all description parts
                        full_description = ' '.join(description_parts)
                        
                        # Clean up non-ASCII characters and empty parentheses
                        full_description = re.sub(r"\(\s*\)", "", full_description)
                        full_description = re.sub(r"[^\x00-\x7F]+", "", full_description).strip()
                        
                        param_info['description'] = full_description
                        
                        # Check if parameter is required
                        if '[REQUIRED]' in param_info.get('description', ''):
                            param_info['required'] = True
                            param_info['description'] = param_info['description'].replace('[REQUIRED]', '').strip()
                        else:
                            param_info['required'] = False
                        
                        parameters.append(param_info)
    
    # Extract response structure
    response_structure = {}
    if field_list:
        field_items = field_list.find_all("dd", recursive=False)
        
        for dd in field_items:
            prev_dt = dd.find_previous_sibling("dt")
            if prev_dt and "Returns" in prev_dt.get_text():
                # Extract response structure details
                response_list = dd.find("ul")
                if response_list:
                    response_structure = _parse_response_structure(response_list)
    
    return {
        'name': method_name,
        'description': description_text,
        'request_syntax': request_syntax,
        'response_syntax': response_syntax,
        'parameters': parameters,
        'response_structure': response_structure,
        'service': service_name
    }


def _parse_response_structure(ul_element) -> Dict:
    """Recursively parse response structure from nested lists"""
    structure = {}
    
    for li in ul_element.find_all("li", recursive=False):
        # Extract field name
        strong_tag = li.find("strong")
        if strong_tag:
            field_name = strong_tag.get_text(strip=True)
            
            # Extract field type
            em_tag = li.find("em")
            field_type = em_tag.get_text(strip=True) if em_tag else ""

            field_type = re.sub(r"\(\s*\)", "", field_type)
            field_type = re.sub(r"[^\x00-\x7F]+", "", field_type).strip()
            
            # Extract description
            description_parts = []
            for content in li.children:
                if isinstance(content, str):
                    text = content.strip()
                    if text and text not in ['–', '-', '—']:
                        description_parts.append(text)
                elif content.name == 'p':
                    description_parts.append(content.get_text(strip=True))
            
            description = ' '.join(description_parts)

            description = re.sub(r"\(\s*\)", "", description)
            description = re.sub(r"[^\x00-\x7F]+", "", description).strip()
            
            # Check for nested structure
            nested_ul = li.find("ul")
            nested_structure = None
            if nested_ul:
                nested_structure = _parse_response_structure(nested_ul)

            if nested_structure: 
                structure[field_name] = {
                    'type': field_type,
                    'description': description,
                    'nested': nested_structure
                }
            else:
                structure[field_name] = {
                    'type': field_type,
                    'description': description
                }
    
    return structure

def _extract_methods(soup: BeautifulSoup, service_name: str) -> List[Dict]:
    method_and_urls = _extract_methods_and_their_urls(soup=soup)

    methods = []

    for method_obj in method_and_urls:
        name, url = method_obj.values()
        url = f"{base_url}/{url}"

        print(f"Fetching documentation from {url}")

        response = session.get(url, timeout=30)
        response.raise_for_status()
        method_soup = BeautifulSoup(response.text, 'html.parser')

        method_details = _extract_method_details(soup=method_soup, method_name=name, service_name=service_name)
        methods.append(method_details)

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
    service = "sqs"
    docs = scrape_service_docs(service)
    if docs:
        print(json.dumps(docs, indent=2))