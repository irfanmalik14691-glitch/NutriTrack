import datetime
from flask import Blueprint, render_template, session, redirect, url_for, Response
from routes.auth_routes import login_required
from models import ProfileModel, FoodLogModel, WaterModel, WeightModel, WorkoutTrackerModel, FoodModel

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    # If user is already logged in, they can still view landing or jump straight to dashboard
    return render_template('landing.html', is_logged_in='user_id' in session)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    today = datetime.date.today().isoformat()

    # Get user profile & metabolic calculations
    profile = ProfileModel.get_by_user_id(user_id)
    if not profile:
        profile = ProfileModel.save_or_update(user_id, {
            'name': session.get('username', 'Athlete'),
            'age': 25,
            'gender': 'male',
            'height': 175.0,
            'current_weight': 70.0,
            'target_weight': 68.0,
            'activity_level': 'moderate',
            'fitness_goal': 'Muscle Building'
        })

    # Get Today's Food Logs & Totals
    today_logs = FoodLogModel.get_daily_logs(user_id, today)
    daily_totals = FoodLogModel.get_daily_totals(user_id, today)

    # Break down today's meals by category
    meals = {
        'breakfast': [l for l in today_logs if l['meal_type'] == 'breakfast'],
        'lunch': [l for l in today_logs if l['meal_type'] == 'lunch'],
        'dinner': [l for l in today_logs if l['meal_type'] == 'dinner'],
        'snacks': [l for l in today_logs if l['meal_type'] == 'snacks']
    }

    # Water consumed today
    water_today = WaterModel.get_daily_water(user_id, today)

    # Workout stats
    workout_stats = WorkoutTrackerModel.get_stats(user_id)

    # Calorie targets & remaining
    calorie_target = profile['daily_calorie_target'] or 2200
    calories_consumed = daily_totals['calories']
    calories_remaining = max(0, round(calorie_target - calories_consumed, 1))
    calorie_pct = min(100, round((calories_consumed / calorie_target) * 100, 1)) if calorie_target > 0 else 0

    # Macro percentages
    protein_target = profile['protein_target'] or 140
    carbs_target = profile['carbs_target'] or 250
    fat_target = profile['fat_target'] or 60

    protein_pct = min(100, round((daily_totals['protein'] / protein_target) * 100, 1)) if protein_target > 0 else 0
    carbs_pct = min(100, round((daily_totals['carbs'] / carbs_target) * 100, 1)) if carbs_target > 0 else 0
    fat_pct = min(100, round((daily_totals['fat'] / fat_target) * 100, 1)) if fat_target > 0 else 0

    # Water percentage
    water_target = profile['water_target'] or 2500
    water_pct = min(100, round((water_today / water_target) * 100, 1)) if water_target > 0 else 0

    # Weight progress
    curr_weight = profile['current_weight']
    tgt_weight = profile['target_weight']
    weight_diff = round(tgt_weight - curr_weight, 1)

    # Weekly calorie intake for chart (past 7 days)
    chart_days = []
    chart_calories = []
    for i in range(6, -1, -1):
        day_date = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
        day_name = (datetime.date.today() - datetime.timedelta(days=i)).strftime('%a')
        tots = FoodLogModel.get_daily_totals(user_id, day_date)
        chart_days.append(day_name)
        chart_calories.append(tots['calories'])

    return render_template(
        'dashboard.html',
        profile=profile,
        today=today,
        meals=meals,
        daily_totals=daily_totals,
        calories_consumed=calories_consumed,
        calorie_target=calorie_target,
        calories_remaining=calories_remaining,
        calorie_pct=calorie_pct,
        protein_target=protein_target,
        carbs_target=carbs_target,
        fat_target=fat_target,
        protein_pct=protein_pct,
        carbs_pct=carbs_pct,
        fat_pct=fat_pct,
        water_today=water_today,
        water_target=water_target,
        water_pct=water_pct,
        weight_diff=weight_diff,
        workout_stats=workout_stats,
        chart_days=chart_days,
        chart_calories=chart_calories
    )

@main_bp.route('/sitemap.xml')
def sitemap():
    pages = [
        url_for('main.landing', _external=True)
    ]

    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

    for page in pages:
        xml += f'<url><loc>{page}</loc></url>'

    xml += '</urlset>'

    return Response(xml, mimetype='application/xml')