import json

# ==============================
# Load Food Database
# ==============================

def load_food_database(path="data/food_database.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)["foods"]
    except Exception:
        return []


# ==============================
# BMI Calculation
# ==============================

def calculate_bmi(weight_kg, height_cm):
    if height_cm <= 0:
        return 0, "Invalid"

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 24.9:
        category = "Normal"
    elif bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obese"

    return round(bmi, 2), category


# ==============================
# BMR Calculation
# Mifflin-St Jeor Equation
# ==============================

def calculate_bmr(weight_kg, height_cm, age, gender):
    if gender.lower() == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    elif gender.lower() == "female":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        return 0


# ==============================
# Daily Calorie Needs
# ==============================

def calculate_daily_calories(bmr, activity_level):
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    multiplier = activity_multipliers.get(activity_level, 1.2)
    return round(bmr * multiplier, 2)


# ==============================
# Food Calorie Calculation
# ==============================

def calculate_food_calories(food_name, grams, food_data):
    for food in food_data:
        if food["name"].lower() == food_name.lower():
            return round((food["calories_per_100g"] / 100) * grams, 2)
    return 0


# ==============================
# Macronutrient Calculation
# ==============================

def calculate_macros(food_name, grams, food_data):
    for food in food_data:
        if food["name"].lower() == food_name.lower():
            factor = grams / 100
            return {
                "protein": round(food["protein_g"] * factor, 2),
                "carbs": round(food["carbs_g"] * factor, 2),
                "fat": round(food["fat_g"] * factor, 2)
            }
    return {"protein": 0, "carbs": 0, "fat": 0}