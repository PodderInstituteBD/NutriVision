from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import uuid
from calculations import (
    calculate_bmi,
    calculate_bmr,
    calculate_daily_calories,
    calculate_food_calories,
    calculate_macros,
    load_food_database
)
from helpers import initialize_session, calculate_total_macros
from config import Config

app = Flask(__name__, template_folder="templates")
app.config.from_object(Config)

# Load food database once
food_data = load_food_database()

# =========================================
# Database Connection
# =========================================
def get_db_connection():
    try:
        conn = sqlite3.connect(app.config["DB_PATH"])
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        app.logger.error(f"Database connection error: {e}")
        return None

# =========================================
# Middleware / Helpers
# =========================================
def is_profile_complete():
    return bool(session.get("name"))

# =========================================
# Routes
# =========================================

@app.route("/")
def index():
    if is_profile_complete():
        return redirect(url_for("dashboard"))
    initialize_session(session)
    return render_template("index.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            age_raw = request.form.get("age")
            gender = request.form.get("gender")
            height_raw = request.form.get("height")
            weight_raw = request.form.get("weight")
            activity = request.form.get("activity")
            diet_mode = request.form.get("diet_mode")

            if not all([name, age_raw, gender, height_raw, weight_raw, activity, diet_mode]):
                flash("All fields including diet mode are required.", "error")
                return render_template("index.html")

            age = int(age_raw)
            height = float(height_raw)
            weight = float(weight_raw)

            bmi, bmi_category = calculate_bmi(weight, height)
            bmr = calculate_bmr(weight, height, age, gender)
            
            # Base calories
            base_daily_cal = calculate_daily_calories(bmr, activity)
            
            # Diet mode adjustments
            mode_adjustments = {
                "bulk": 300,
                "cut": -300,
                "weight_gain": 500,
                "weight_loss": -500
            }
            adjustment = mode_adjustments.get(diet_mode, 0)
            daily_cal = base_daily_cal + adjustment

            # Save in session
            session["name"] = name
            session["age"] = age
            session["gender"] = gender
            session["height"] = height
            session["weight"] = weight
            session["activity"] = activity
            session["diet_mode"] = diet_mode
            session["bmi"] = bmi
            session["bmi_category"] = bmi_category
            session["bmr"] = bmr
            session["daily_cal"] = daily_cal

            # Generate unique email to avoid IntegrityError
            unique_id = str(uuid.uuid4())[:8]
            email = f"{name.lower().replace(' ', '.')}.{unique_id}@demo.com"

            # Save in database
            conn = get_db_connection()
            if conn:
                conn.execute("""
                    INSERT INTO users 
                    (name, email, password, age, gender, height, weight, activity, bmi, bmr, daily_cal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    email,
                    "hashed_password",
                    age,
                    gender,
                    height,
                    weight,
                    activity,
                    bmi,
                    bmr,
                    daily_cal
                ))
                conn.commit()
                conn.close()

            return redirect(url_for("dashboard"))
        except ValueError:
            flash("Invalid numerical values provided.", "error")
            return render_template("index.html")
        except sqlite3.IntegrityError:
            # Fallback for extreme cases, though uuid should prevent this
            flash("Email already exists. Please try again.", "error")
            return render_template("index.html")
        except Exception as e:
            app.logger.error(f"Profile creation error: {e}")
            flash(f"Error creating profile: {str(e)}", "error")
            return render_template("index.html")

    if is_profile_complete():
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/food_entry", methods=["GET", "POST"])
def food_entry():
    if not is_profile_complete():
        flash("Please create your profile first.", "info")
        return redirect(url_for("index"))

    if "food_log" not in session:
        session["food_log"] = []

    if request.method == "POST":
        try:
            food_name = request.form.get("food_name")
            grams_raw = request.form.get("quantity")

            if not food_name or not grams_raw:
                flash("Food name and quantity are required.", "error")
                return redirect(url_for("food_entry"))

            grams = float(grams_raw)
            calories = calculate_food_calories(food_name, grams, food_data)
            macros = calculate_macros(food_name, grams, food_data)

            entry = {
                "name": food_name,
                "quantity": grams,
                "calories": calories,
                "protein": macros["protein"],
                "carbs": macros["carbs"],
                "fat": macros["fat"]
            }

            session["food_log"].append(entry)
            session.modified = True

            # Save to database (demo user id = 1)
            conn = get_db_connection()
            if conn:
                conn.execute("""
                    INSERT INTO food_log 
                    (user_id, food_name, quantity, calories, protein, carbs, fat)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    1,
                    food_name,
                    grams,
                    calories,
                    macros["protein"],
                    macros["carbs"],
                    macros["fat"]
                ))
                conn.commit()
                conn.close()

            flash(f"Added {food_name} to log.", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            app.logger.error(f"Food entry error: {e}")
            flash("Error adding food item.", "error")

    return render_template("food_entry.html", foods=food_data)

@app.route("/dashboard")
@app.route("/progress")
def dashboard():
    if not is_profile_complete():
        return redirect(url_for("index"))

    food_log = session.get("food_log", [])
    totals = calculate_total_macros(food_log)

    daily_cal = session.get("daily_cal", 0)
    total_cal = totals.get("calories", 0)
    remaining = round(daily_cal - total_cal, 2)
    
    progress_percent = 0
    if daily_cal > 0:
        progress_percent = min(round((total_cal / daily_cal) * 100, 2), 100)

    return render_template(
        "dashboard.html",
        user_name=session.get("name"),
        daily_cal=daily_cal,
        total_cal=total_cal,
        remaining=max(0, remaining),
        progress_percent=progress_percent,
        bmi=session.get("bmi", 0),
        bmi_category=session.get("bmi_category", "N/A"),
        diet_mode=session.get("diet_mode", "N/A"),
        totals=totals,
        food_log=food_log
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
