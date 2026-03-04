import os
from app import app

port = int(os.environ.get("PORT", 10000))

if __name__ != "__main__":
    # Tell Gunicorn to bind correctly
    app.config["SERVER_NAME"] = f"0.0.0.0:{port}"