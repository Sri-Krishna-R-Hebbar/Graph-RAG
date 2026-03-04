import os
from web.app import app

# Render provides PORT env variable
port = os.getenv("PORT", "10000")
app.config["SERVER_NAME"] = f"0.0.0.0:{port}"

# Gunicorn looks for this
application = app