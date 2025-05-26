"""The tauri-app."""

from pytauri import (
    BuilderArgs,
    builder_factory,
    context_factory,
)
from .baku_bridge import process_file


def main() -> int:
    """Run the tauri-app."""
    app = builder_factory().build(
        BuilderArgs(
            context=context_factory(),
            invoke_handler={
                "process_file": process_file
            },
        )
    )
    exit_code = app.run_return()
    return exit_code