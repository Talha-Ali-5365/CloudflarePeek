"""Command-line interface for CloudflarePeek."""

import logging
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from . import __version__
from .core.detector import behind_cloudflare
from .core.scraper import peek

# --- Typer App Initialization ---
app = typer.Typer(
    name="cloudflare-peek",
    help="A powerful Python utility to scrape any website, even those behind Cloudflare, with a fallback to OCR.",
    add_completion=False,
)
console = Console()

# --- Utility Functions ---
def version_callback(value: bool):
    """Prints the version of the package."""
    if value:
        console.print(f"CloudflarePeek Version: {__version__}", style="bold green")
        raise typer.Exit()

def setup_logging(verbose: bool):
    """Configure logging based on verbosity."""
    log_level = "DEBUG" if verbose else "INFO"

    # Configure root logger for rich, colorful output
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )
    # Set the specific logger for cloudflare_peek
    logging.getLogger("cloudflare_peek").setLevel(log_level)


# --- CLI Commands ---

@app.command()
def scrape(
    url: str = typer.Argument(..., help="The URL of the website to scrape"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Save the scraped content to a file."),
    force_ocr: bool = typer.Option(False, "--force-ocr", help="Force OCR method instead of attempting fast scraping."),
    no_headless: bool = typer.Option(False, "--no-headless", help="Run the browser in non-headless mode for debugging."),
    timeout: int = typer.Option(120, "--timeout", help="Page load timeout in seconds for OCR method."),
    scroll_pause: float = typer.Option(1.0, "--scroll-pause", help="Pause time in seconds between scrolls."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose (DEBUG) logging."),
):
    """
    Scrape a website, automatically handling Cloudflare protection.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        logger.info("🚀 Starting scrape for: %s", url)
        # Convert timeout to milliseconds for the peek function
        content = peek(
            url,
            force_ocr=force_ocr,
            timeout=timeout * 1000,
            headless=not no_headless,
            scroll_pause=scroll_pause,
        )

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            console.print(f"✅ Content saved to [bold green]{output_file}[/bold green]")
        else:
            console.print("\n--- Scraped Content ---", style="bold yellow")
            console.print(content)
            console.print("--- End Content ---", style="bold yellow")

    except Exception as e:
        logger.error("❌ An error occurred: %s", e)
        raise typer.Exit(code=1)

@app.command()
def check_cloudflare(
    url: str = typer.Argument(..., help="The URL of the website to check."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose (DEBUG) logging."),
):
    """
    Check if a website is protected by Cloudflare.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    logger.info("🔍 Checking Cloudflare status for: %s", url)
    is_protected = behind_cloudflare(url)

    if is_protected:
        console.print("🛡️  [bold yellow]Result:[/bold yellow] The website is likely protected by Cloudflare.")
    else:
        console.print("✅  [bold green]Result:[/bold green] The website does not appear to be protected by Cloudflare.")

@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show the application's version and exit."),
):
    """
    CloudflarePeek CLI main entry point.
    """
    pass

if __name__ == "__main__":
    app() 