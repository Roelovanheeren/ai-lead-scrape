import typer
import uvicorn

from backend.core.settings import get_settings

app = typer.Typer()


@app.command()
def dev(host: str = "0.0.0.0", port: int = 8000):
    """Run development server"""
    uvicorn.run("backend.app:app", host=host, port=port, reload=True)


@app.command()
def test():
    """Run pytest suite"""
    import subprocess

    subprocess.run(["pytest", "-q"], check=False)


if __name__ == "__main__":
    app()
