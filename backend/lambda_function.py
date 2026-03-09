from mangum import Mangum
from app import app as main_app # Import the FastAPI app from app.py

print("FASTAPI APP LOADED")

# The handler should wrap the main_app
handler = Mangum(main_app)