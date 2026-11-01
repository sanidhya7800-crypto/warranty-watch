"""TinyFish SDK integration test.

Runs a small browser-automation task against Hacker News and prints the run
status and the extracted result. The API key is loaded from a local .env file
via python-dotenv and is never printed.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from tinyfish import AuthenticationError, RunStatus, SDKError, TinyFish

# .env lives next to this script (the project root).
ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

ENV_VAR = "TINYFISH_API_KEY"
TARGET_URL = "https://news.ycombinator.com/"
GOAL = (
    "Open the Hacker News homepage and extract the top 3 stories. "
    "For each story, return its title, its points, and its URL."
)


def missing_key_message(path: Path) -> str:
    return (
        "TINYFISH_API_KEY is not set. No API call was made.\n"
        "Paste your TinyFish API key into this file:\n"
        f"    {path}\n"
        "It should look like:\n"
        "    TINYFISH_API_KEY=your-key-here\n"
        "Then re-run the test."
    )


def main() -> int:
    # Check for the key without ever printing its value.
    api_key = os.environ.get(ENV_VAR)
    if not api_key or not api_key.strip():
        print(missing_key_message(ENV_FILE), file=sys.stderr)
        return 1

    print("Starting TinyFish agent run...")
    print(f"Target: {TARGET_URL}")
    print(f"Goal:   {GOAL}")
    print("-" * 60)

    try:
        # The SDK can also read TINYFISH_API_KEY from the environment, but we
        # pass it explicitly so the failure mode stays ours to control.
        client = TinyFish(api_key=api_key)
        response = client.agent.run(goal=GOAL, url=TARGET_URL)
    except AuthenticationError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        print(f"Check the key in: {ENV_FILE}", file=sys.stderr)
        return 2
    except SDKError as exc:
        print(f"TinyFish SDK error: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # last resort; the key is never printed
        print(f"Unexpected error ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 4

    print(f"Status:      {response.status}")
    print(f"Run ID:      {response.run_id}")
    print(f"Steps taken: {response.num_of_steps}")

    if response.status == RunStatus.COMPLETED:
        print("Result:")
        if response.result is not None:
            print(json.dumps(response.result, indent=2, default=str))
        else:
            print("  (no result returned)")
        return 0

    print("Run did not complete successfully.")
    if response.error is not None:
        print(f"Error code:     {response.error.code}")
        print(f"Error message:  {response.error.message}")
        print(f"Error category: {response.error.category}")
        if response.error.help_message:
            print(f"Help:           {response.error.help_message}")
        if response.error.help_url:
            print(f"Help URL:       {response.error.help_url}")
    else:
        print("No error details were returned.")
    return 5


if __name__ == "__main__":
    raise SystemExit(main())
