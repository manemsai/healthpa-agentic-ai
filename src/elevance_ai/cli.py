"""Command-line entrypoints for Elevance AI."""


def main() -> None:
    """Provide a simple console entrypoint for the package."""

    print("Elevance AI foundation is installed. Start the API with: uvicorn apps.api.main:app --reload")
