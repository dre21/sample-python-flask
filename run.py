"""
Entry point for the Flask application.

Usage:
    flask run          (auto-discovers this via FLASK_APP)
    python run.py      (direct execution)
    gunicorn run:app   (production)
"""

from app import init_app

app = init_app()

if __name__ == '__main__':
    app.run(debug=True)
