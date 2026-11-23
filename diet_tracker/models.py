import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

class UserModel:
    @staticmethod
    def create_user(username, email, password):
        db = get_db()
        password_hash = generate_password_hash(password)
        try:
            cursor = db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username.strip(), email.strip().lower(), password_hash)
            )
            db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    @staticmethod
    def get_by_username(username):
        db = get_db()
        return db.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()

    @staticmethod
    def get_by_email(email):
        db = get_db()
        return db.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)


class ProfileModel:
    @staticmethod
    def calculate_nutrition(gender, age, height_cm, current_weight_kg, target_weight_kg, activity_level, fitness_goal):
        """
        Scientific calculations:
        - BMI = weight / (height/100)^2
        - BMR (Mifflin-St Jeor):
          Male: 10*weight + 6.25*height - 5*age + 5
          Female: 10*weight + 6.25*height - 5*age - 161
        - TDEE = BMR * activity_multiplier
        - Goal Adjustments:
          Weight Loss: TDEE - 500 (safe healthy deficit ~0.5kg/week)
          Weight Gain: TDEE + 500 (healthy surplus ~0.5kg/week)
          Muscle Building: TDEE + 250 (lean hypertrophy surplus)
          Maintenance: TDEE
        - Macro targets:
          Protein: 2.0g/kg for Muscle Building, 1.8g/kg for Loss/Gain, 1.6g/kg for Maintenance
          Fat: 25% of calories / 9 kcal/g
          Carbs: Remaining calories / 4 kcal/g
        - Water: 35ml per kg of bodyweight
        """
        height_m = height_cm / 100.0
        bmi = round(current_weight_kg / (height_m ** 2), 1)

        # BMR
        if str(gender).lower() == 'male':
            bmr = (10 * current_weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * current_weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        bmr = round(bmr, 0)

        # Activity multiplier
        activity_map = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        mult = activity_map.get(activity_level, 1.375)
        tdee = round(bmr * mult, 0)

        # Goal adjustment
        goal_lower = fitness_goal.lower()
        if 'loss' in goal_lower:
            daily_calories = max(1200, tdee - 500)
            protein_g = round(current_weight_kg * 1.8, 1)
        elif 'gain' in goal_lower:
            daily_calories = tdee + 500
            protein_g = round(current_weight_kg * 1.8, 1)
        elif 'muscle' in goal_lower:
            daily_calories = tdee + 250
            protein_g = round(current_weight_kg * 2.0, 1)
        else: # Maintenance
            daily_calories = tdee
            protein_g = round(current_weight_kg * 1.6, 1)

        daily_calories = round(daily_calories, 0)

        # Fat: 25% of calories
        fat_calories = daily_calories * 0.25
        fat_g = round(fat_calories / 9.0, 1)

        # Protein calories
        protein_calories = protein_g * 4.0

        # Carbs: remainder
        carbs_calories = max(0, daily_calories - fat_calories - protein_calories)
        carbs_g = round(carbs_calories / 4.0, 1)

        # Daily Water target in ml
        water_target = round(current_weight_kg * 35, 0)
        water_target = max(2000, min(5000, water_target))

        return {
            'bmi': bmi,
            'bmr': bmr,
            'tdee': tdee,
            'daily_calorie_target': daily_calories,
            'protein_target': protein_g,
            'carbs_target': carbs_g,
            'fat_target': fat_g,
            'water_target': water_target
        }

    @staticmethod
    def get_by_user_id(user_id):
        db = get_db()
        return db.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)).fetchone()

    @staticmethod
    def save_or_update(user_id, data):
        db = get_db()
        name = data.get('name', 'Fitness Enthusiast').strip()
        age = int(data.get('age', 25))
        gender = data.get('gender', 'male')
        height = float(data.get('height', 175.0))
        current_weight = float(data.get('current_weight', 70.0))
        target_weight = float(data.get('target_weight', 68.0))
        activity_level = data.get('activity_level', 'moderate')
        fitness_goal = data.get('fitness_goal', 'Muscle Building')
        experience_level = data.get('experience_level', 'Beginner')
        workout_location = data.get('workout_location', 'Both')
        workout_days = int(data.get('workout_days', 4))
        workout_time = int(data.get('workout_time', 45))

        calc = ProfileModel.calculate_nutrition(
            gender, age, height, current_weight, target_weight, activity_level, fitness_goal
        )

        existing = ProfileModel.get_by_user_id(user_id)
        if existing:
            db.execute('''
                UPDATE user_profiles SET
                    name = ?, age = ?, gender = ?, height = ?, current_weight = ?,
                    target_weight = ?, activity_level = ?, fitness_goal = ?,
                    experience_level = ?, workout_location = ?, workout_days = ?, workout_time = ?,
                    bmi = ?, bmr = ?, tdee = ?, daily_calorie_target = ?,
                    protein_target = ?, carbs_target = ?, fat_target = ?, water_target = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                name, age, gender, height, current_weight, target_weight, activity_level, fitness_goal,
                experience_level, workout_location, workout_days, workout_time,
                calc['bmi'], calc['bmr'], calc['tdee'], calc['daily_calorie_target'],
                calc['protein_target'], calc['carbs_target'], calc['fat_target'], calc['water_target'],
                user_id
            ))
        else:
            db.execute('''
                INSERT INTO user_profiles (
                    user_id, name, age, gender, height, current_weight, target_weight,
                    activity_level, fitness_goal, experience_level, workout_location, workout_days, workout_time,
                    bmi, bmr, tdee, daily_calorie_target, protein_target, carbs_target, fat_target, water_target
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, name, age, gender, height, current_weight, target_weight,
                activity_level, fitness_goal, experience_level, workout_location, workout_days, workout_time,
                calc['bmi'], calc['bmr'], calc['tdee'], calc['daily_calorie_target'],
                calc['protein_target'], calc['carbs_target'], calc['fat_target'], calc['water_target']
            ))

        # Also log current weight to weight_logs if not already logged today
        import datetime
        today = datetime.date.today().isoformat()
        weight_entry = db.execute(
            "SELECT id FROM weight_logs WHERE user_id = ? AND log_date = ?", (user_id, today)
        ).fetchone()
        if not weight_entry:
            db.execute(
                "INSERT INTO weight_logs (user_id, weight, notes, log_date) VALUES (?, ?, ?, ?)",
                (user_id, current_weight, 'Profile update', today)
            )

        db.commit()
        return ProfileModel.get_by_user_id(user_id)


class FoodModel:
    @staticmethod
    def get_all(search=None, user_id=None):
        db = get_db()
        query = "SELECT * FROM food_items WHERE is_custom = 0"
        params = []
        if user_id:
            query = "SELECT * FROM food_items WHERE is_custom = 0 OR created_by = ?"
            params.append(user_id)

        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search.strip()}%")

        query += " ORDER BY name ASC"
        return db.execute(query, params).fetchall()

    @staticmethod
    def get_by_id(food_id):
        db = get_db()
        return db.execute("SELECT * FROM food_items WHERE id = ?", (food_id,)).fetchone()

    @staticmethod
    def add_custom(user_id, name, category, cal, protein, carbs, fat):
        db = get_db()
        cursor = db.execute('''
            INSERT INTO food_items (name, category, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_custom, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        ''', (name.strip(), category.strip(), float(cal), float(protein), float(carbs), float(fat), user_id))
        db.commit()
        return cursor.lastrowid


class FoodLogModel:
    @staticmethod
    def log_food(user_id, food_item_id, food_name, meal_type, grams, cal_100g, p_100g, c_100g, f_100g, log_date):
        ratio = float(grams) / 100.0
        cal = round(float(cal_100g) * ratio, 1)
        p = round(float(p_100g) * ratio, 1)
        c = round(float(c_100g) * ratio, 1)
        f = round(float(f_100g) * ratio, 1)

        db = get_db()
        cursor = db.execute('''
            INSERT INTO food_logs (user_id, food_item_id, food_name, meal_type, quantity_grams, calories, protein, carbs, fat, log_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, food_item_id, food_name, meal_type.lower(), float(grams), cal, p, c, f, log_date))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_daily_logs(user_id, log_date):
        db = get_db()
        return db.execute('''
            SELECT * FROM food_logs
            WHERE user_id = ? AND log_date = ?
            ORDER BY id ASC
        ''', (user_id, log_date)).fetchall()

    @staticmethod
    def get_daily_totals(user_id, log_date):
        db = get_db()
        row = db.execute('''
            SELECT
                COALESCE(SUM(calories), 0) as total_calories,
                COALESCE(SUM(protein), 0) as total_protein,
                COALESCE(SUM(carbs), 0) as total_carbs,
                COALESCE(SUM(fat), 0) as total_fat
            FROM food_logs
            WHERE user_id = ? AND log_date = ?
        ''', (user_id, log_date)).fetchone()
        return {
            'calories': round(row['total_calories'], 1),
            'protein': round(row['total_protein'], 1),
            'carbs': round(row['total_carbs'], 1),
            'fat': round(row['total_fat'], 1)
        }

    @staticmethod
    def delete_log(log_id, user_id):
        db = get_db()
        db.execute("DELETE FROM food_logs WHERE id = ? AND user_id = ?", (log_id, user_id))
        db.commit()


class WaterModel:
    @staticmethod
    def add_water(user_id, amount_ml, log_date):
        db = get_db()
        db.execute('''
            INSERT INTO water_logs (user_id, amount_ml, log_date)
            VALUES (?, ?, ?)
        ''', (user_id, float(amount_ml), log_date))
        db.commit()

    @staticmethod
    def get_daily_water(user_id, log_date):
        db = get_db()
        row = db.execute('''
            SELECT COALESCE(SUM(amount_ml), 0) as total
            FROM water_logs
            WHERE user_id = ? AND log_date = ?
        ''', (user_id, log_date)).fetchone()
        return round(row['total'], 0)

    @staticmethod
    def get_water_history(user_id, days=7):
        db = get_db()
        return db.execute('''
            SELECT log_date, SUM(amount_ml) as total_ml
            FROM water_logs
            WHERE user_id = ?
            GROUP BY log_date
            ORDER BY log_date DESC
            LIMIT ?
        ''', (user_id, days)).fetchall()


class WeightModel:
    @staticmethod
    def record_weight(user_id, weight, log_date, notes=''):
        db = get_db()
        # update or insert for that date
        existing = db.execute("SELECT id FROM weight_logs WHERE user_id = ? AND log_date = ?", (user_id, log_date)).fetchone()
        if existing:
            db.execute("UPDATE weight_logs SET weight = ?, notes = ? WHERE id = ?", (float(weight), notes, existing['id']))
        else:
            db.execute("INSERT INTO weight_logs (user_id, weight, notes, log_date) VALUES (?, ?, ?, ?)", (user_id, float(weight), notes, log_date))

        # Also update current_weight in user_profiles if this is the most recent date
        db.execute("UPDATE user_profiles SET current_weight = ? WHERE user_id = ?", (float(weight), user_id))
        db.commit()

    @staticmethod
    def get_history(user_id, limit=30):
        db = get_db()
        return db.execute('''
            SELECT log_date, weight, notes
            FROM weight_logs
            WHERE user_id = ?
            ORDER BY log_date ASC
            LIMIT ?
        ''', (user_id, limit)).fetchall()


class MealPlanModel:
    @staticmethod
    def create_plan(user_id, plan_name, description=''):
        db = get_db()
        cursor = db.execute("INSERT INTO meal_plans (user_id, plan_name, description) VALUES (?, ?, ?)", (user_id, plan_name.strip(), description.strip()))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def add_plan_item(plan_id, food_item_id, food_name, meal_type, grams, cal, p, c, f):
        db = get_db()
        db.execute('''
            INSERT INTO meal_plan_items (meal_plan_id, food_item_id, food_name, meal_type, quantity_grams, calories, protein, carbs, fat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (plan_id, food_item_id, food_name, meal_type.lower(), float(grams), float(cal), float(p), float(c), float(f)))
        db.commit()

    @staticmethod
    def get_user_plans(user_id):
        db = get_db()
        plans = db.execute("SELECT * FROM meal_plans WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
        result = []
        for p in plans:
            items = db.execute("SELECT * FROM meal_plan_items WHERE meal_plan_id = ?", (p['id'],)).fetchall()
            tot_cal = sum(item['calories'] for item in items)
            tot_p = sum(item['protein'] for item in items)
            tot_c = sum(item['carbs'] for item in items)
            tot_f = sum(item['fat'] for item in items)
            result.append({
                'id': p['id'],
                'plan_name': p['plan_name'],
                'description': p['description'],
                'items': items,
                'total_calories': round(tot_cal, 1),
                'total_protein': round(tot_p, 1),
                'total_carbs': round(tot_c, 1),
                'total_fat': round(tot_f, 1)
            })
        return result

    @staticmethod
    def log_plan_to_diary(user_id, plan_id, target_date):
        db = get_db()
        items = db.execute("SELECT * FROM meal_plan_items WHERE meal_plan_id = ?", (plan_id,)).fetchall()
        for item in items:
            db.execute('''
                INSERT INTO food_logs (user_id, food_item_id, food_name, meal_type, quantity_grams, calories, protein, carbs, fat, log_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, item['food_item_id'], item['food_name'], item['meal_type'], item['quantity_grams'], item['calories'], item['protein'], item['carbs'], item['fat'], target_date))
        db.commit()

    @staticmethod
    def delete_plan(plan_id, user_id):
        db = get_db()
        db.execute("DELETE FROM meal_plans WHERE id = ? AND user_id = ?", (plan_id, user_id))
        db.commit()


class ExerciseModel:
    @staticmethod
    def get_all(muscle=None, location=None, equipment=None, difficulty=None, search=None):
        db = get_db()
        query = "SELECT * FROM exercises WHERE 1=1"
        params = []
        if muscle:
            query += " AND (muscle_group LIKE ? OR secondary_muscles LIKE ?)"
            params.extend([f"%{muscle}%", f"%{muscle}%"])
        if location and location.lower() != 'both':
            query += " AND (location = ? OR location = 'Both')"
            params.append(location)
        if equipment:
            query += " AND equipment = ?"
            params.append(equipment)
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        if search:
            query += " AND (name LIKE ? OR machine_name LIKE ? OR muscle_group LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        query += " ORDER BY muscle_group ASC, name ASC"
        return db.execute(query, params).fetchall()

    @staticmethod
    def get_by_slug(slug):
        db = get_db()
        return db.execute("SELECT * FROM exercises WHERE slug = ?", (slug,)).fetchone()

    @staticmethod
    def get_by_muscle(muscle_name):
        db = get_db()
        return db.execute(
            "SELECT * FROM exercises WHERE muscle_group LIKE ? OR secondary_muscles LIKE ? ORDER BY name ASC",
            (f"%{muscle_name}%", f"%{muscle_name}%")
        ).fetchall()


class WorkoutTrackerModel:
    @staticmethod
    def log_session(user_id, session_name, workout_date, duration_minutes=45, notes=''):
        db = get_db()
        cursor = db.execute('''
            INSERT INTO workout_sessions (user_id, session_name, workout_date, duration_minutes, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_name, workout_date, duration_minutes, notes))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def log_set(session_id, user_id, exercise_id, exercise_name, set_num, target_reps, completed_reps, weight_kg, log_date):
        db = get_db()
        cursor = db.execute('''
            INSERT INTO workout_set_logs (session_id, user_id, exercise_id, exercise_name, set_number, target_reps, completed_reps, weight_kg, log_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, exercise_id, exercise_name, set_num, target_reps, completed_reps, float(weight_kg), log_date))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_user_sessions(user_id, limit=10):
        db = get_db()
        sessions = db.execute('''
            SELECT * FROM workout_sessions
            WHERE user_id = ?
            ORDER BY workout_date DESC, id DESC
            LIMIT ?
        ''', (user_id, limit)).fetchall()
        result = []
        for s in sessions:
            sets = db.execute('''
                SELECT * FROM workout_set_logs WHERE session_id = ? ORDER BY exercise_name, set_number
            ''', (s['id'],)).fetchall()
            result.append({
                'session': s,
                'sets': sets,
                'total_sets': len(sets)
            })
        return result

    @staticmethod
    def get_stats(user_id):
        db = get_db()
        total_sessions = db.execute("SELECT COUNT(*) FROM workout_sessions WHERE user_id = ?", (user_id,)).fetchone()[0]
        total_sets = db.execute("SELECT COUNT(*) FROM workout_set_logs WHERE user_id = ?", (user_id,)).fetchone()[0]

        # PRs (max weight per exercise)
        prs = db.execute('''
            SELECT exercise_name, MAX(weight_kg) as max_weight, MAX(completed_reps) as max_reps
            FROM workout_set_logs
            WHERE user_id = ? AND weight_kg > 0
            GROUP BY exercise_name
            ORDER BY max_weight DESC
            LIMIT 5
        ''', (user_id,)).fetchall()

        # Workouts this week (last 7 days)
        recent_count = db.execute('''
            SELECT COUNT(*) FROM workout_sessions
            WHERE user_id = ? AND workout_date >= date('now', '-7 days')
        ''', (user_id,)).fetchone()[0]

        return {
            'total_workouts': total_sessions,
            'total_sets': total_sets,
            'weekly_completed': recent_count,
            'personal_records': prs
        }

    @staticmethod
    def generate_workout_plan(fitness_goal, days_per_week, experience, equipment):
        """
        Generates structured 3, 4, 5, or 6-day workout splits.
        """
        is_gym = equipment in ['Gym', 'Both']

        if days_per_week <= 3:
            split_name = "3-Day Full Body Frequency"
            schedule = [
                {
                    "day": "Monday - Full Body Power A",
                    "focus": "Chest, Back, Quads, Core",
                    "exercises": [
                        {"name": "Barbell Flat Bench Press" if is_gym else "Standard Push-ups", "sets": 3, "reps": "8-10", "rest": "90s"},
                        {"name": "Lat Pulldown Machine" if is_gym else "Pull-ups / Chin-ups", "sets": 3, "reps": "10-12", "rest": "75s"},
                        {"name": "45-Degree Leg Press Machine" if is_gym else "Bodyweight Air Squats", "sets": 3, "reps": "10-12", "rest": "90s"},
                        {"name": "Seated Shoulder Press Machine" if is_gym else "Pike Push-ups", "sets": 3, "reps": "10-12", "rest": "60s"},
                        {"name": "Core Plank (Isometric Hold)", "sets": 3, "reps": "45-60s", "rest": "45s"}
                    ]
                },
                {"day": "Tuesday - Active Rest / Mobility & Cardio", "focus": "Recovery & 8,000 Steps", "exercises": []},
                {
                    "day": "Wednesday - Full Body Hypertrophy B",
                    "focus": "Shoulders, Hamstrings, Lats, Arms",
                    "exercises": [
                        {"name": "Incline Dumbbell / Barbell Bench Press" if is_gym else "Incline Push-ups", "sets": 3, "reps": "8-12", "rest": "75s"},
                        {"name": "Seated Cable Row" if is_gym else "Pull-ups / Chin-ups", "sets": 3, "reps": "10-12", "rest": "60s"},
                        {"name": "Seated / Lying Leg Curl Machine" if is_gym else "Walking / Reverse Lunges", "sets": 3, "reps": "12-15", "rest": "60s"},
                        {"name": "Dumbbell Alternating Bicep Curl", "sets": 3, "reps": "10-12", "rest": "60s"},
                        {"name": "Cable Triceps Pushdown" if is_gym else "Assisted Dips", "sets": 3, "reps": "12-15", "rest": "60s"}
                    ]
                },
                {"day": "Thursday - Rest & Hydration", "focus": "Nutrition & Muscle Repair", "exercises": []},
                {
                    "day": "Friday - Full Body Functional C",
                    "focus": "Legs, Upper Push/Pull, Abs",
                    "exercises": [
                        {"name": "Smith Machine Squats" if is_gym else "Bodyweight Air Squats", "sets": 4, "reps": "8-10", "rest": "90s"},
                        {"name": "Pec Deck / Butterfly Machine" if is_gym else "Standard Push-ups", "sets": 3, "reps": "12-15", "rest": "60s"},
                        {"name": "T-Bar Row" if is_gym else "Pull-ups / Chin-ups", "sets": 3, "reps": "8-10", "rest": "75s"},
                        {"name": "Standing / Seated Calf Raise Machine" if is_gym else "Glute Bridges", "sets": 4, "reps": "15-20", "rest": "45s"},
                        {"name": "Hanging Leg / Knee Raises" if is_gym else "Abdominal Crunches", "sets": 3, "reps": "12-15", "rest": "60s"}
                    ]
                },
                {"day": "Saturday - Rest / Light Recreation", "focus": "Active Recovery", "exercises": []},
                {"day": "Sunday - Full Rest & Meal Prep", "focus": "Weekly Review & Target Setup", "exercises": []}
            ]
        elif days_per_week == 4:
            split_name = "4-Day Upper / Lower Hypertrophy Split"
            schedule = [
                {
                    "day": "Monday - Upper Body Strength",
                    "focus": "Chest, Back, Shoulders, Arms",
                    "exercises": [
                        {"name": "Barbell Flat Bench Press" if is_gym else "Standard Push-ups", "sets": 4, "reps": "6-8", "rest": "90s"},
                        {"name": "Lat Pulldown Machine" if is_gym else "Pull-ups / Chin-ups", "sets": 4, "reps": "8-10", "rest": "90s"},
                        {"name": "Seated Shoulder Press Machine" if is_gym else "Pike Push-ups", "sets": 3, "reps": "8-10", "rest": "75s"},
                        {"name": "Dumbbell Alternating Bicep Curl", "sets": 3, "reps": "10-12", "rest": "60s"},
                        {"name": "Cable Triceps Pushdown" if is_gym else "Assisted Dips", "sets": 3, "reps": "10-12", "rest": "60s"}
                    ]
                },
                {
                    "day": "Tuesday - Lower Body Strength & Core",
                    "focus": "Quads, Hamstrings, Glutes, Calves",
                    "exercises": [
                        {"name": "45-Degree Leg Press Machine" if is_gym else "Bodyweight Air Squats", "sets": 4, "reps": "8-10", "rest": "90s"},
                        {"name": "Seated / Lying Leg Curl Machine" if is_gym else "Walking / Reverse Lunges", "sets": 3, "reps": "10-12", "rest": "60s"},
                        {"name": "Leg Extension Machine" if is_gym else "Glute Bridges", "sets": 3, "reps": "12-15", "rest": "60s"},
                        {"name": "Standing / Seated Calf Raise Machine", "sets": 4, "reps": "15-20", "rest": "45s"},
                        {"name": "Hanging Leg / Knee Raises" if is_gym else "Core Plank", "sets": 3, "reps": "12-15", "rest": "60s"}
                    ]
                },
                {"day": "Wednesday - Rest & Recovery", "focus": "Stretching, Mobility, High Protein Nutrition", "exercises": []},
                {
                    "day": "Thursday - Upper Body Hypertrophy",
                    "focus": "Upper Chest, Mid-Back, Side Delts, Arms",
                    "exercises": [
                        {"name": "Incline Dumbbell / Barbell Bench Press" if is_gym else "Incline Push-ups", "sets": 3, "reps": "10-12", "rest": "75s"},
                        {"name": "Seated Cable Row" if is_gym else "Pull-ups", "sets": 3, "reps": "10-12", "rest": "75s"},
                        {"name": "Lateral Raise Machine" if is_gym else "Pike Push-ups", "sets": 4, "reps": "12-15", "rest": "45s"},
                        {"name": "Face Pull (Cable)" if is_gym else "Standard Push-ups", "sets": 3, "reps": "15-20", "rest": "45s"},
                        {"name": "Dumbbell Hammer Curl", "sets": 3, "reps": "10-12", "rest": "60s"}
                    ]
                },
                {
                    "day": "Friday - Lower Body Hypertrophy & Abs",
                    "focus": "Squat Pattern, Hamstrings, Calves, Abs",
                    "exercises": [
                        {"name": "Smith Machine Squats" if is_gym else "Bodyweight Air Squats", "sets": 4, "reps": "10-12", "rest": "90s"},
                        {"name": "Hip Abduction / Adduction Machine" if is_gym else "Walking / Reverse Lunges", "sets": 3, "reps": "15-20", "rest": "45s"},
                        {"name": "Back Extension (Hyperextension)", "sets": 3, "reps": "12-15", "rest": "60s"},
                        {"name": "Ab Crunch Machine" if is_gym else "Abdominal Crunches", "sets": 3, "reps": "15-20", "rest": "45s"}
                    ]
                },
                {"day": "Saturday - Active Rest / Walking", "focus": "Cardio & Recovery", "exercises": []},
                {"day": "Sunday - Full Rest", "focus": "Rest & Macro Preparation", "exercises": []}
            ]
        elif days_per_week == 5:
            split_name = "5-Day Push / Pull / Legs / Upper / Lower Split"
            schedule = [
                {"day": "Monday - Push (Chest, Shoulders, Triceps)", "focus": "Upper Body Pressing", "exercises": [
                    {"name": "Barbell Flat Bench Press" if is_gym else "Standard Push-ups", "sets": 4, "reps": "8-10", "rest": "90s"},
                    {"name": "Seated Shoulder Press Machine" if is_gym else "Pike Push-ups", "sets": 3, "reps": "10-12", "rest": "75s"},
                    {"name": "Pec Deck / Butterfly Machine" if is_gym else "Incline Push-ups", "sets": 3, "reps": "12-15", "rest": "60s"},
                    {"name": "Lateral Raise Machine", "sets": 3, "reps": "12-15", "rest": "45s"},
                    {"name": "Cable Triceps Pushdown", "sets": 3, "reps": "10-12", "rest": "60s"}
                ]},
                {"day": "Tuesday - Pull (Back, Rear Delts, Biceps)", "focus": "Upper Body Pulling", "exercises": [
                    {"name": "Lat Pulldown Machine" if is_gym else "Pull-ups", "sets": 4, "reps": "8-10", "rest": "90s"},
                    {"name": "Seated Cable Row", "sets": 3, "reps": "10-12", "rest": "75s"},
                    {"name": "Face Pull (Cable)", "sets": 3, "reps": "15-20", "rest": "45s"},
                    {"name": "Bicep Curl Machine", "sets": 3, "reps": "10-12", "rest": "60s"},
                    {"name": "Dumbbell Hammer Curl", "sets": 3, "reps": "10-12", "rest": "60s"}
                ]},
                {"day": "Wednesday - Legs & Abs", "focus": "Quads, Hamstrings, Core", "exercises": [
                    {"name": "45-Degree Leg Press Machine" if is_gym else "Bodyweight Air Squats", "sets": 4, "reps": "10-12", "rest": "90s"},
                    {"name": "Leg Extension Machine", "sets": 3, "reps": "12-15", "rest": "60s"},
                    {"name": "Seated / Lying Leg Curl Machine", "sets": 3, "reps": "10-12", "rest": "60s"},
                    {"name": "Standing / Seated Calf Raise Machine", "sets": 4, "reps": "15-20", "rest": "45s"},
                    {"name": "Hanging Leg / Knee Raises", "sets": 3, "reps": "12-15", "rest": "60s"}
                ]},
                {"day": "Thursday - Rest / Active Mobility", "focus": "Hydration & Muscle Recovery", "exercises": []},
                {"day": "Friday - Upper Body Focus", "focus": "Chest, Back, Arms", "exercises": [
                    {"name": "Incline Dumbbell / Barbell Bench Press", "sets": 3, "reps": "8-10", "rest": "75s"},
                    {"name": "T-Bar Row", "sets": 3, "reps": "8-10", "rest": "75s"},
                    {"name": "Overhead Cable Triceps Extension", "sets": 3, "reps": "12-15", "rest": "60s"},
                    {"name": "Dumbbell Alternating Bicep Curl", "sets": 3, "reps": "10-12", "rest": "60s"}
                ]},
                {"day": "Saturday - Lower Body & Core", "focus": "Hips, Glutes, Abs", "exercises": [
                    {"name": "Smith Machine Squats" if is_gym else "Lunges", "sets": 4, "reps": "8-10", "rest": "90s"},
                    {"name": "Glute Bridges", "sets": 3, "reps": "15-20", "rest": "45s"},
                    {"name": "Ab Crunch Machine" if is_gym else "Plank", "sets": 3, "reps": "15-20", "rest": "45s"}
                ]},
                {"day": "Sunday - Rest Day", "focus": "Weekly Rest & Nutrition Prep", "exercises": []}
            ]
        else: # 6 days
            split_name = "6-Day Push / Pull / Legs (PPL x 2) Elite Split"
            schedule = [
                {"day": "Monday - Push A", "focus": "Chest Heavy, Front Delts, Triceps", "exercises": [
                    {"name": "Barbell Flat Bench Press" if is_gym else "Standard Push-ups", "sets": 4, "reps": "6-8", "rest": "90s"},
                    {"name": "Seated Shoulder Press Machine", "sets": 3, "reps": "8-10", "rest": "75s"},
                    {"name": "Pec Deck / Butterfly Machine", "sets": 3, "reps": "12-15", "rest": "60s"},
                    {"name": "Cable Triceps Pushdown", "sets": 3, "reps": "10-12", "rest": "60s"}
                ]},
                {"day": "Tuesday - Pull A", "focus": "Lats Heavy, Upper Back, Biceps", "exercises": [
                    {"name": "Lat Pulldown Machine" if is_gym else "Pull-ups", "sets": 4, "reps": "8-10", "rest": "90s"},
                    {"name": "Seated Cable Row", "sets": 3, "reps": "10-12", "rest": "75s"},
                    {"name": "Face Pull (Cable)", "sets": 3, "reps": "15-20", "rest": "45s"},
                    {"name": "Dumbbell Alternating Bicep Curl", "sets": 3, "reps": "10-12", "rest": "60s"}
                ]},
                {"day": "Wednesday - Legs A", "focus": "Quad Dominant, Calves, Abs", "exercises": [
                    {"name": "45-Degree Leg Press Machine" if is_gym else "Squats", "sets": 4, "reps": "8-10", "rest": "90s"},
                    {"name": "Leg Extension Machine", "sets": 3, "reps": "12-15", "rest": "60s"},
                    {"name": "Standing / Seated Calf Raise Machine", "sets": 4, "reps": "15-20", "rest": "45s"},
                    {"name": "Core Plank (Isometric Hold)", "sets": 3, "reps": "60s", "rest": "45s"}
                ]},
                {"day": "Thursday - Push B", "focus": "Incline Chest, Side Delts, Triceps Stretch", "exercises": [
                    {"name": "Incline Dumbbell / Barbell Bench Press", "sets": 4, "reps": "8-10", "rest": "75s"},
                    {"name": "Lateral Raise Machine", "sets": 4, "reps": "12-15", "rest": "45s"},
                    {"name": "Standing Cable Crossover", "sets": 3, "reps": "12-15", "rest": "60s"},
                    {"name": "Overhead Cable Triceps Extension", "sets": 3, "reps": "10-12", "rest": "60s"}
                ]},
                {"day": "Friday - Pull B", "focus": "Thick Back, Rear Delts, Biceps Brachialis", "exercises": [
                    {"name": "T-Bar Row", "sets": 4, "reps": "8-10", "rest": "90s"},
                    {"name": "Reverse Pec Deck (Rear Delt Fly)", "sets": 3, "reps": "12-15", "rest": "45s"},
                    {"name": "Bicep Curl Machine", "sets": 3, "reps": "10-12", "rest": "60s"},
                    {"name": "Dumbbell Hammer Curl", "sets": 3, "reps": "10-12", "rest": "60s"}
                ]},
                {"day": "Saturday - Legs B", "focus": "Hamstring & Glute Focus, Calves, Abs", "exercises": [
                    {"name": "Smith Machine Squats", "sets": 4, "reps": "10-12", "rest": "90s"},
                    {"name": "Seated / Lying Leg Curl Machine", "sets": 4, "reps": "10-12", "rest": "60s"},
                    {"name": "Back Extension (Hyperextension Bench)", "sets": 3, "reps": "12-15", "rest": "60s"},
                    {"name": "Hanging Leg / Knee Raises", "sets": 3, "reps": "12-15", "rest": "60s"}
                ]},
                {"day": "Sunday - Total Rest & Recovery", "focus": "Full Body Repair & Sleep", "exercises": []}
            ]

        return {
            'split_name': split_name,
            'schedule': schedule
        }
