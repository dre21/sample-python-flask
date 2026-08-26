"""
Vercel entrypoint — exposes the Flask `app` variable for the serverless runtime.
Vercel auto-detects index.py and looks for the `app` variable.
"""

from app import init_app

app = init_app()
