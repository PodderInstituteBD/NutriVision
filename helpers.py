# ==============================
# NutriVision Helper Functions
# ==============================

def initialize_session(session):
    """
    Initialize the default session structure for a new user.
    """
    if "food_log" not in session:
        session["food_log"] = []

    if "name" not in session:
        session["name"] = ""
    if "age" not in session:
        session["age"] = 0
    if "gender" not in session:
        session["gender"] = ""
    if "weight" not in session:
        session["weight"] = 0
    if "height" not in session:
        session["height"] = 0
    if "activity" not in session:
        session["activity"] = "sedentary"
    if "bmi" not in session:
        session["bmi"] = 0
    if "bmr" not in session:
        session["bmr"] = 0
    if "daily_cal" not in session:
        session["daily_cal"] = 0


def format_calories(value):
    """
    Format calorie value to two decimals and append 'kcal'.
    """
    return f"{round(value, 2)} kcal"


def format_macros(macros_dict):
    """
    Format protein, carbs, and fat dictionary for display.
    """
    return {
        "protein": round(macros_dict.get("protein", 0), 2),
        "carbs": round(macros_dict.get("carbs", 0), 2),
        "fat": round(macros_dict.get("fat", 0), 2)
    }


def calculate_total_macros(food_log):
    """
    Sum up all macros from the food log.
    """
    total = {"protein": 0, "carbs": 0, "fat": 0, "calories": 0}
    for item in food_log:
        total["protein"] += item.get("protein", 0)
        total["carbs"] += item.get("carbs", 0)
        total["fat"] += item.get("fat", 0)
        total["calories"] += item.get("calories", 0)
    return {k: round(v, 2) for k, v in total.items()}


def get_activity_multiplier(activity_level):
    """
    Return activity multiplier for daily calorie calculation.
    """
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    return multipliers.get(activity_level, 1.2)