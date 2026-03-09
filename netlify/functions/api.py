import os
import sys

# Add the project root to sys.path
# The function is in netlify/functions/api.py
# So root is three levels up (api.py -> functions -> netlify -> root)
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import serverless_wsgi
from app import app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

