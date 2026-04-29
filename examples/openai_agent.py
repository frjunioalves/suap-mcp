"""
Agente OpenAI (GPT-4o-mini) integrado ao SUAP MCP.

Uso:
    SUAP_BASE_URL=https://suap.ifpi.edu.br \
    SUAP_TOKEN=eyJ... \
    OPENAI_API_KEY=sk-... \
    python examples/openai_agent.py
"""

import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

SUAP_BASE_URL = os.environ["SUAP_BASE_URL"]
SUAP_TOKEN = os.environ["SUAP_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
MODEL = "gpt-4o-mini"

# Inicia o servidor MCP como subprocesso, injetando as credenciais SUAP via env.
server_params = StdioServerParameters(
    command="suap-mcp",
    env={
        **os.environ,          # repassa o ambiente atual (PATH, etc.)
        "SUAP_BASE_URL": SUAP_BASE_URL,
        "SUAP_TOKEN": SUAP_TOKEN,
    },
)


def mcp_tool_to_openai(tool) -> dict:
    """Converte uma ferramenta MCP para o schema de function-calling do OpenAI."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


async def run(user_message: str) -> str:
    client_openai = OpenAI(api_key=OPENAI_API_KEY)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Busca as ferramentas disponíveis no servidor SUAP MCP
            mcp_tools = (await session.list_tools()).tools
            openai_tools = [mcp_tool_to_openai(t) for t in mcp_tools]

            messages = [{"role": "user", "content": user_message}]

            # Loop de tool-calling: continua até o modelo parar de chamar ferramentas
            while True:
                response = client_openai.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                )
                choice = response.choices[0]

                if choice.finish_reason == "tool_calls":
                    messages.append(choice.message)

                    for call in choice.message.tool_calls:
                        args = json.loads(call.function.arguments)
                        result = await session.call_tool(call.function.name, args)
                        content = result.content[0].text if result.content else ""

                        messages.append({
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": content,
                        })
                else:
                    return choice.message.content


if __name__ == "__main__":
    question = input("Pergunta para o assistente SUAP: ")
    answer = asyncio.run(run(question))
    print("\n", answer)
