import os
import asyncio
import json
from openai import OpenAI
from fastmcp import Client
from dotenv import load_dotenv

load_dotenv()

MCP_ENDPOINT = "http://127.0.0.1:8000/mcp"
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AWSMCPAgent:
    def __init__(self, mcp_endpoint: str):
        self.mcp_endpoint = mcp_endpoint
        self.tools = []
        self.conversation_history = []
    
    async def initialize(self):
        async with Client(self.mcp_endpoint) as mcp_client:
            tools_response = await mcp_client.list_tools()
            
            # Convert to OpenAI format
            self.tools = []
            for tool in tools_response:
                self.tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or f"Tool: {tool.name}",
                        "parameters": tool.inputSchema
                    }
                })
            
            print(f"Connected to MCP server. Available tools: {[t['function']['name'] for t in self.tools]}")
    
    async def process_query(self, user_query: str) -> str:
        """
        Process a user query, automatically checking and scraping resources as needed
        
        Args:
            user_query: User's AWS-related request
        
        Returns:
            Final response
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })
        
        # System prompt that guides the LLM to use tools intelligently
        system_prompt = """You are an AWS automation assistant with access to MCP tools.

When a user asks you to perform AWS operations, follow this workflow:

1. ALWAYS start by calling 'check_aws_resources' with the user's query
   - This tells you which AWS services are needed
   - And whether documentation resources exist for them

2. If resources are missing (needs_scraping list is not empty):
   - Call 'scrape_aws_documentation' with the missing services
   - This will fetch and cache the documentation

3. Once you have all resources:
   - Call 'get_aws_service_methods' to see available operations
   - If method_count is 0, the documentation scraping may have had issues
   - In that case, proceed with your knowledge of common AWS operations
   - Call 'search_aws_examples' if you need code examples
   - Call 'execute_aws_operation' to perform the actual AWS operation

4. Always explain what you're doing at each step

IMPORTANT: If get_aws_service_methods returns 0 methods, do NOT call it repeatedly.
Instead, use your knowledge of AWS SDK to construct the operation call.

For EC2 instances, common operations include:
- run_instances: Create new EC2 instances
- describe_instances: List instances
- stop_instances: Stop running instances
- terminate_instances: Terminate instances

Example workflow for "Create a t2.micro EC2 instance":
1. check_aws_resources("Create a t2.micro EC2 instance")
2. If EC2 docs missing: scrape_aws_documentation(["ec2"])
3. get_aws_service_methods("ec2") to find run_instances
4. If methods found: use them; if not: use your AWS knowledge
5. execute_aws_operation("ec2", "run_instances", {
     "ImageId": "ami-0c55b159cbfafe1f0",
     "InstanceType": "t2.micro",
     "MinCount": 1,
     "MaxCount": 1
   })

Be methodical and thorough."""

        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history
        
        tool_call_history = []
        max_iterations = 15
        iteration_count = 0
        
        # Start conversation loop
        async with Client(self.mcp_endpoint) as mcp_client:
            while iteration_count < max_iterations:
                iteration_count += 1
                
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                assistant_message = response.choices[0].message
                messages.append(assistant_message)
                
                # Check if we're done
                if not assistant_message.tool_calls:
                    # No more tool calls, return final response
                    final_response = assistant_message.content
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": final_response
                    })
                    return final_response
                
                # Execute tool calls
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    call_signature = f"{tool_name}:{json.dumps(tool_args, sort_keys=True)}"
                    if call_signature in tool_call_history[-3:]:
                        print(f"Warning: Repeated tool call detected: {tool_name}")
                        # Add a message to break the loop
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({
                                "error": "This tool was already called with the same parameters. Please proceed with available information or try a different approach."
                            })
                        })
                        continue
                    
                    tool_call_history.append(call_signature)
                    
                    print(f"\nCalling: {tool_name}({json.dumps(tool_args, indent=2)})")
                    
                    try:
                        # Execute via MCP
                        result = await mcp_client.call_tool(tool_name, tool_args)
                        result_content = result.content[0].text
                        
                        print(f"Result: {result_content[:200]}...")
                        
                        # Add result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_content
                        })
                    except Exception as e:
                        print(f"Error calling {tool_name}: {e}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": str(e)})
                        })
            
            # If we hit max iterations, return a message
            return "I've reached the maximum number of operations. Please try breaking down your request into smaller steps."


async def main():
    """Main interactive loop"""
    print("AWS MCP Agent - Auto-Documentation System")
    print("=" * 50)
    
    agent = AWSMCPAgent(MCP_ENDPOINT)
    
    print("\nInitializing agent...")
    await agent.initialize()
    
    print("\nAgent ready! You can now make AWS requests.")
    print("The agent will automatically scrape documentation as needed.")
    print("\nExamples:")
    print("  - Create a t2.micro EC2 instance")
    print("  - Create an S3 bucket named my-data-bucket")
    print("  - List all my running EC2 instances")
    print("  - Create a Lambda function")
    print("\nType 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            print("\nProcessing your request...\n")
            response = await agent.process_query(user_input)
            print(f"\nAssistant: {response}\n")
            print("-" * 50 + "\n")
        
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())