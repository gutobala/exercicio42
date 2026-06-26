# cliente_teste.py
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> dict:
    params = StdioServerParameters(command="python", args=["servidor_mcp.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            nomes = [t.name for t in tools.tools]

            criar = await session.call_tool("criar_tarefa", {"titulo": "tarefa via mcp"})
            listar = await session.call_tool("listar_tarefas", {})

            return {
                "tools": nomes,
                "criar_resultado": json.loads(criar.content[0].text),
                "listar_resultado": json.loads(listar.content[0].text),
            }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(main())))