import asyncio
import os
import sys
from contextlib import AsyncExitStack

from core.claude import Claude
from core.cli import CliApp
from core.cli_chat import CliChat
from dotenv import load_dotenv
from mcp_client import MCPClient

load_dotenv()

# Anthropic Config
claude_model = "claude-sonnet-4-5@20250929"
gcp_project_id = os.getenv("ANTHROPIC_VERTEX_PROJECT_ID", "")
gcp_region = os.getenv("CLOUD_ML_REGION", "")


assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert gcp_project_id, "Error: GCP_PROJECT_ID cannot be empty. Update .env"
assert gcp_region, "Error: GCP_REGION cannot be empty. Update .env"


async def main():
    claude_service = Claude(
        model=claude_model, gcp_region=gcp_region, gcp_project_id=gcp_project_id
    )

    server_scripts = sys.argv[1:]
    clients = {}

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=claude_service,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
