import json

import httpx
import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def query(text: str, api_url: str = "http://127.0.0.1:8000") -> None:
    """Search monster stat blocks using natural language."""
    response = httpx.post(f"{api_url}/v1/query", json={"query": text}, timeout=20)
    response.raise_for_status()
    typer.echo(json.dumps(response.json(), indent=2))


@app.command()
def get(slug: str, api_url: str = "http://127.0.0.1:8000") -> None:
    """Fetch the original stat block for one monster."""
    response = httpx.get(f"{api_url}/v1/monsters/{slug}", timeout=20)
    response.raise_for_status()
    typer.echo(json.dumps(response.json(), indent=2))
