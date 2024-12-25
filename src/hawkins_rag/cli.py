"""Command line interface for hawkins_rag package."""
from typing import Optional, List
from pathlib import Path
import json
import importlib
import typer

from .config import Config
from .core import HawkinsRAG
from .utils.loader_registry import _LOADER_REGISTRY

app = typer.Typer()

def load_config(config_file: Optional[Path]) -> Config:
    """Load configuration from file or use defaults."""
    try:
        if config_file and config_file.exists():
            with open(config_file) as f:
                config_data = json.load(f)
                return Config.from_dict(config_data)
        return Config()
    except Exception as e:
        typer.echo(f"Error loading config: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def ingest(
    source: str = typer.Argument(..., help="Source path or URL to ingest"),
    source_type: str = typer.Argument(..., help="Type of source (pdf, audio, github, etc)"),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
):
    """Ingest a source into the RAG system."""
    try:
        config = load_config(config_file)
        rag = HawkinsRAG(config)
        result = rag.ingest(source, source_type)

        if result["success"]:
            typer.echo(f"Successfully ingested {source}")
            typer.echo(f"Created {result['chunks_created']} chunks")
        else:
            typer.echo(f"Error: {result['message']}", err=True)
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def query(
    question: str = typer.Argument(..., help="Question to ask the RAG system"),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
):
    """Query the RAG system."""
    try:
        config = load_config(config_file)
        rag = HawkinsRAG(config)
        result = rag.query(question)

        if result["success"]:
            typer.echo(result["response"])
        else:
            typer.echo(f"Error: {result['message']}", err=True)
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def list_sources(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
):
    """List all ingested sources."""
    try:
        config = load_config(config_file)
        rag = HawkinsRAG(config)
        sources = rag.list_sources()

        if sources:
            for source in sources:
                typer.echo(
                    f"Type: {source['properties']['source_type']}, "
                    f"Source: {source['properties']['source']}"
                )
        else:
            typer.echo("No sources found")
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def test_loaders(
    loader_types: Optional[List[str]] = typer.Option(
        None, "--loaders", "-l",
        help="Specific loader types to test (e.g., pdf,excel,json). If not provided, tests all available loaders."
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="Path to config file"
    ),
):
    """Test specified document loaders."""
    try:
        config = load_config(config_file)
        rag = HawkinsRAG(config)

        # Determine which loaders to test
        loaders_to_test = (
            loader_types[0].split(",") if loader_types
            else list(_LOADER_REGISTRY.keys())
        )

        typer.echo("Testing loaders...")
        for loader_type in loaders_to_test:
            try:
                if loader_type not in _LOADER_REGISTRY:
                    typer.echo(f"\nUnknown loader type: {loader_type}")
                    continue

                typer.echo(f"\nTesting {loader_type} loader...")
                loader = _LOADER_REGISTRY[loader_type]({})
                typer.echo("Status: Available ✓")

            except Exception as e:
                typer.echo(f"Error testing {loader_type} loader: {str(e)}")

    except Exception as e:
        typer.echo(f"Error during loader testing: {str(e)}", err=True)
        raise typer.Exit(1)

def main():
    """Entry point for the CLI application."""
    app()

if __name__ == "__main__":
    main()