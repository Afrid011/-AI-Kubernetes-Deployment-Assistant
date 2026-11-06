from fastmcp import FastMCP

# Create MCP Server
server = FastMCP("AI Kubernetes Deployment Assistant")


@server.tool
async def hello(name: str = "User") -> str:
    """Return a greeting."""
    return f"Hello {name}! MCP is working."


@server.tool
async def add_numbers(a: int, b: int) -> str:
    """Add two numbers."""
    return str(a + b)


async def main():
    # Run using stdio transport (same behavior as before)
    await server.run_async(transport="stdio")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
