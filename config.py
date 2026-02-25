import os

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_default_secret_key")

    # Debug mode (set False in production)
    DEBUG = True

    # Database path (SQLite)
    DB_PATH = os.environ.get("DB_PATH", "nutri.db")

    # Optional: Food API configuration (if you decide to use online API)
    NUTRITION_API_KEY = os.environ.get("NUTRITION_API_KEY", "")
    NUTRITION_API_URL = os.environ.get("NUTRITION_API_URL", "https://api.edamam.com/api/food-database/v2/parser")

    # Default activity levels (used in calorie calculation)
    ACTIVITY_LEVELS = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
