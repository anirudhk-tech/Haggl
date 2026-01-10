#!/usr/bin/env python3
"""
IngredientAI Calling Agent - Main Entry Point

Usage:
    # Start the server
    python main.py serve --port 8001
    
    # Or use uvicorn directly
    uvicorn src.calling_agent.server:app --host 0.0.0.0 --port 8001 --reload
"""

import argparse
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Haggl Calling Agent"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the agent server")
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to listen on (default: 8001)"
    )
    serve_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    if args.command == "serve":
        import uvicorn
        uvicorn.run(
            "src.calling_agent.server:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
