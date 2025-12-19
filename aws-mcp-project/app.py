import os
import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from fastmcp import Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_ENDPOINT = "http://127.0.0.1:8000/mcp"
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = f"""You are an AWS automation assistant (Alaiy Cloud V1.0).

IMPORTANT AWS REGION CONFIGURATION:
- The AWS region is configured as: {os.getenv('AWS_REGION', 'ap-south-1')}
- This region is set via environment variables and is automatically used
- NEVER include 'region' or 'region_name' as a parameter when calling execute_aws_operation
- The region is already configured - you don't need to specify it

When using execute_aws_operation:
- Only pass parameters that the specific AWS API method accepts
- Do NOT pass 'region' as a parameter - it's already configured
- Example: For describe_instances, pass filters or instance IDs, but NOT region

Use your tools to scrape docs and execute commands. 
Be concise. Do not use markdown formatting like bold or italics.
Output plain text only, matching a typewriter style."""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize Tools
    tools = []
    try:
        async with Client(MCP_ENDPOINT) as mcp_client:
            tools_response = await mcp_client.list_tools()
            for tool in tools_response:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
    except Exception as e:
        await websocket.send_json({"type": "error", "content": "Failed to connect to MCP Server"})
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    try:
        while True:
            # Wait for user input
            data = await websocket.receive_text()
            user_input = json.loads(data)["message"]
            messages.append({"role": "user", "content": user_input})

            # Agent Loop
            iteration = 0
            max_iterations = 10
            
            async with Client(MCP_ENDPOINT) as mcp_client:
                while iteration < max_iterations:
                    iteration += 1
                    
                    # Call OpenAI
                    response = await openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        stream=True
                    )
                    
                    token_collector = ""
                    tool_calls = []
                    cur_tool = None
                    
                    # Stream chunks
                    async for chunk in response:
                        delta = chunk.choices[0].delta
                        
                        # Stream Text
                        if delta.content:
                            token_collector += delta.content
                            await websocket.send_json({
                                "type": "token",
                                "content": delta.content
                            })
                        
                        # Collect Tool Calls
                        if delta.tool_calls:
                            for tc in delta.tool_calls:
                                if tc.id:
                                    if cur_tool: tool_calls.append(cur_tool)
                                    cur_tool = {"id": tc.id, "type": "function", "function": {"name": "", "arguments": ""}}
                                if tc.function.name: cur_tool["function"]["name"] += tc.function.name
                                if tc.function.arguments: cur_tool["function"]["arguments"] += tc.function.arguments
                    
                    if cur_tool: tool_calls.append(cur_tool)
                    
                    # Save assistant message
                    assistant_msg = {"role": "assistant", "content": token_collector}
                    if tool_calls: assistant_msg["tool_calls"] = tool_calls
                    messages.append(assistant_msg)

                    # Stop if no tools
                    if not tool_calls:
                        await websocket.send_json({"type": "end"})
                        break

                    # Execute Tools
                    for tool in tool_calls:
                        fn_name = tool["function"]["name"]
                        fn_args = json.loads(tool["function"]["arguments"])
                        
                        # Notify frontend of tool use
                        await websocket.send_json({
                            "type": "log", 
                            "content": f"> EXEC_PROC: {fn_name}"
                        })

                        try:
                            result = await mcp_client.call_tool(fn_name, fn_args)
                            result_text = result.content[0].text
                        except Exception as e:
                            result_text = str(e)

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool["id"],
                            "content": result_text
                        })

    except Exception as e:
        print(f"Connection closed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)