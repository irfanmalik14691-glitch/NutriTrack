import datetime
import io
import csv
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from routes.auth_routes import login_required
from models import ProfileModel, WeightModel, FoodLogModel, WaterModel, WorkoutTrackerModel
from database import get_db

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/progress', methods=['GET', 'POST'])
@login_required
def progress():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    today = datetime.date.today().isoformat()

    if request.method == 'POST':
        weight = request.form.get('weight')
        log_date = request.form.get('log_date', today)
        notes = request.form.get('notes', '').strip()

        try:
            WeightModel.record_weight(user_id, float(weight), log_date, notes)
            flash(f'Logged weight of {weight} kg for {log_date}!', 'success')
        except Exception as e:
            flash(f'Error logging weight: {str(e)}', 'error')

        return redirect(url_for('progress.progress'))

    # Load weight history
    history = WeightModel.get_history(user_id, limit=30)
    current_wt = profile['current_weight'] if profile else 70.0
    target_wt = profile['target_weight'] if profile else 68.0

    # Chart arrays
    chart_dates = [h['log_date'] for h in history]
    chart_weights = [h['weight'] for h in history]

    # Nutrition trend past 14 days
    trend_dates = []
    trend_cals = []
    trend_proteins = []
    for i in range(13, -1, -1):
        d = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
        day_label = (datetime.date.today() - datetime.timedelta(days=i)).strftime('%b %d')
        t = FoodLogModel.get_daily_totals(user_id, d)
        trend_dates.append(day_label)
        trend_cals.append(t['calories'])
        trend_proteins.append(t['protein'])

    return render_template(
        'progress.html',
        profile=profile,
        today=today,
        history=history,
        current_wt=current_wt,
        target_wt=target_wt,
        chart_dates=chart_dates,
        chart_weights=chart_weights,
        trend_dates=trend_dates,
        trend_cals=trend_cals,
        trend_proteins=trend_proteins
    )


@progress_bp.route('/reports')
@login_required
def reports():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    today = datetime.date.today().isoformat()

    # Calculate 7-day averages
    total_cal = 0
    total_p = 0
    total_c = 0
    total_f = 0
    total_w = 0

    daily_breakdown = []
    for i in range(6, -1, -1):
        cur_date = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
        day_name = (datetime.date.today() - datetime.timedelta(days=i)).strftime('%A (%b %d)')
        t = FoodLogModel.get_daily_totals(user_id, cur_date)
        w = WaterModel.get_daily_water(user_id, cur_date)

        total_cal += t['calories']
        total_p += t['protein']
        total_c += t['carbs']
        total_f += t['fat']
        total_w += w

        daily_breakdown.append({
            'date': cur_date,
            'day_name': day_name,
            'calories': t['calories'],
            'protein': t['protein'],
            'carbs': t['carbs'],
            'fat': t['fat'],
            'water': w
        })

    avg_cal = round(total_cal / 7.0, 1)
    avg_p = round(total_p / 7.0, 1)
    avg_c = round(total_c / 7.0, 1)
    avg_f = round(total_f / 7.0, 1)
    avg_w = round(total_w / 7.0, 0)

    workout_stats = WorkoutTrackerModel.get_stats(user_id)

    return render_template(
        'reports.html',
        profile=profile,
        today=today,
        avg_cal=avg_cal,
        avg_p=avg_p,
        avg_c=avg_c,
        avg_f=avg_f,
        avg_w=avg_w,
        daily_breakdown=daily_breakdown,
        workout_stats=workout_stats
    )


@progress_bp.route('/export/food-logs')
@login_required
def export_food_logs():
    user_id = session['user_id']
    db = get_db()
    logs = db.execute('''
        SELECT log_date, meal_type, food_name, quantity_grams, calories, protein, carbs, fat, logged_at
        FROM food_logs
        WHERE user_id = ?
        ORDER BY log_date DESC, id DESC
    ''', (user_id,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Meal Type', 'Food Item', 'Quantity (g)', 'Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Logged At'])

    for row in logs:
        writer.writerow([
            row['log_date'],
            row['meal_type'].capitalize(),
            row['food_name'],
            row['quantity_grams'],
            row['calories'],
            row['protein'],
            row['carbs'],
            row['fat'],
            row['logged_at']
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=nutritrack_food_logs_{datetime.date.today().isoformat()}.csv"}
    )


@progress_bp.route('/export/weight-logs')
@login_required
def export_weight_logs():
    user_id = session['user_id']
    db = get_db()
    logs = db.execute('''
        SELECT log_date, weight, notes, logged_at
        FROM weight_logs
        WHERE user_id = ?
        ORDER BY log_date DESC
    ''', (user_id,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Weight (kg)', 'Notes', 'Logged At'])

    for row in logs:
        writer.writerow([row['log_date'], row['weight'], row['notes'] or '', row['logged_at']])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=nutritrack_weight_history_{datetime.date.today().isoformat()}.csv"}
    )


@progress_bp.route('/export/workout-logs')
@login_required
def export_workout_logs():
    user_id = session['user_id']
    db = get_db()
    logs = db.execute('''
        SELECT s.workout_date, s.session_name, w.exercise_name, w.set_number, w.weight_kg, w.completed_reps
        FROM workout_set_logs w
        JOIN workout_sessions s ON w.session_id = s.id
        WHERE w.user_id = ?
        ORDER BY s.workout_date DESC, w.id ASC
    ''', (user_id,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Session Name', 'Exercise', 'Set Number', 'Weight (kg)', 'Reps Completed'])

    for row in logs:
        writer.writerow([row['workout_date'], row['session_name'], row['exercise_name'], row['set_number'], row['weight_kg'], row['completed_reps']])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=nutritrack_workouts_{datetime.date.today().isoformat()}.csv"}
    )
