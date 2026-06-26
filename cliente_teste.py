# cliente_teste.py
import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def extrair(resultado, lista=False):
    """Extrai o payload de um CallToolResult de forma robusta entre versoes do SDK.

    O formato de call_tool(...).content varia: algumas versoes preenchem
    `structuredContent`, outras devolvem `content` como uma lista de blocos
    TextContent (um bloco por item, no caso de ferramentas que retornam lista).
    """
    # 1) SDK novo: dados ja vem estruturados em structuredContent
    structured = getattr(resultado, "structuredContent", None)
    if structured is not None:
        # FastMCP envelopa retornos que nao sao dict (ex.: list) em {"result": ...}
        if isinstance(structured, dict) and list(structured.keys()) == ["result"]:
            return structured["result"]
        return structured

    # 2) Fallback: content como lista de blocos TextContent, cada um com JSON em .text
    content = getattr(resultado, "content", None) or []
    itens = [json.loads(b.text) for b in content if getattr(b, "text", None) is not None]
    if not itens:
        raise ValueError("Nao foi possivel extrair JSON do resultado da ferramenta")

    if lista:
        # se a lista veio num unico bloco ja como JSON array, desempacota
        if len(itens) == 1 and isinstance(itens[0], list):
            return itens[0]
        return itens  # um bloco por item -> junta tudo numa lista

    return itens[0]  # objeto unico


async def main() -> dict:
    params = StdioServerParameters(command="python", args=["servidor_mcp.py"])
    # Manda o stderr do servidor para o devnull: garante que o stdout lido pelo
    # autograder contenha SOMENTE o envelope JSON, sem logs do MCP.
    with open(os.devnull, "w") as devnull:
        async with stdio_client(params, errlog=devnull) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                nomes = [t.name for t in tools.tools]

                criar = await session.call_tool("criar_tarefa", {"titulo": "tarefa via mcp"})
                listar = await session.call_tool("listar_tarefas", {})

                return {
                    "tools": nomes,
                    "criar_resultado": extrair(criar),
                    "listar_resultado": extrair(listar, lista=True),
                }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(main())))