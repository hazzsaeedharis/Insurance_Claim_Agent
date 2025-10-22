#!/usr/bin/env python
"""
Insurance Claim Processing System - Main Entry Point

Start the application with: python run.py

This provides a simple, clean entry point following best practices.
"""

import sys
import os
import webbrowser
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))


def print_banner():
    """Display startup banner."""
    print("""
    ================================================================
                                                                    
         Insurance Claim Processing System                          
         AI-Powered Document Analysis & Claim Processing            
                                                                    
    ================================================================
    """)


def check_requirements():
    """Check if required packages are installed."""
    required = ["fastapi", "uvicorn", "pydantic", "groq", "openai", "pinecone"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def check_api_keys():
    """Check if at least one AI service is configured."""
    from backend.config import validate_api_keys
    
    api_status = validate_api_keys()
    
    print("\nAPI Key Status:")
    print(f"   - Groq:     {'[OK] Configured' if api_status['groq'] else '[X] Not set'}")
    print(f"   - OpenAI:   {'[OK] Configured' if api_status['openai'] else '[X] Not set'}")
    print(f"   - Gemini:   {'[OK] Configured' if api_status['gemini'] else '[X] Not set'}")
    print(f"   - Pinecone: {'[OK] Configured' if api_status['pinecone'] else '[X] Not set'}")
    
    if not any([api_status['groq'], api_status['openai'], api_status['gemini']]):
        print("\n[WARNING] No AI service configured!")
        print("   Set at least one of: GROQ_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY")
        print("   Example: set GROQ_API_KEY=your_key_here")
        return False
    
    return True


def main():
    """Main entry point."""
    print_banner()
    
    # Check requirements
    print("[>] Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    
    # Check API keys
    if not check_api_keys():
        print("\n[WARNING] Starting anyway, but AI features won't work properly.")
    
    # Import and run the API
    #import backend.api
    from backend.config import get_settings
    import uvicorn
    
    settings = get_settings()
    
    print(f"\n[>] Starting server...")
    print(f"   - API:      http://localhost:{settings.api_port}")
    print(f"   - Docs:     http://localhost:{settings.api_port}/docs")
    print(f"   - Frontend: Open frontend/index.html in your browser")
    print(f"\n   Press CTRL+C to stop the server\n")
    
    # Optional: Open browser automatically
    if "--open" in sys.argv:
        webbrowser.open(f"http://localhost:{settings.api_port}/docs")
    
    # Run the server
    try:
        uvicorn.run(
            "backend.api:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug_mode,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)


if __name__ == "__main__":
    main()