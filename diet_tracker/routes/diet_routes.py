import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from routes.auth_routes import login_required
from models import ProfileModel, FoodModel, FoodLogModel, WaterModel, MealPlanModel

diet_bp = Blueprint('diet', __name__)

@diet_bp.route('/food-tracker', methods=['GET', 'POST'])
@login_required
def food_tracker():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)

    # Date handling
    date_str = request.args.get('date', datetime.date.today().isoformat())
    try:
        log_date = datetime.date.fromisoformat(date_str).isoformat()
    except ValueError:
        log_date = datetime.date.today().isoformat()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_log':
            food_item_id = request.form.get('food_item_id')
            food_name = request.form.get('food_name', '').strip()
            meal_type = request.form.get('meal_type', 'breakfast').lower()
            grams = request.form.get('quantity_grams', 100)
            cal_100 = request.form.get('calories_per_100g', 0)
            p_100 = request.form.get('protein_per_100g', 0)
            c_100 = request.form.get('carbs_per_100g', 0)
            f_100 = request.form.get('fat_per_100g', 0)

            try:
                FoodLogModel.log_food(
                    user_id=user_id,
                    food_item_id=food_item_id if food_item_id else None,
                    food_name=food_name,
                    meal_type=meal_type,
                    grams=float(grams),
                    cal_100g=float(cal_100),
                    p_100g=float(p_100),
                    c_100g=float(c_100),
                    f_100g=float(f_100),
                    log_date=log_date
                )
                flash(f'Added {food_name} ({grams}g) to {meal_type.capitalize()}!', 'success')
            except Exception as e:
                flash(f'Error logging food: {str(e)}', 'error')

            return redirect(url_for('diet.food_tracker', date=log_date))

    # Fetch daily food entries
    logs = FoodLogModel.get_daily_logs(user_id, log_date)
    totals = FoodLogModel.get_daily_totals(user_id, log_date)

    # Available foods for dropdown / search
    foods = FoodModel.get_all(user_id=user_id)

    # Group logs by meal type
    meals = {
        'breakfast': [l for l in logs if l['meal_type'] == 'breakfast'],
        'lunch': [l for l in logs if l['meal_type'] == 'lunch'],
        'dinner': [l for l in logs if l['meal_type'] == 'dinner'],
        'snacks': [l for l in logs if l['meal_type'] == 'snacks']
    }

    # Meal subtotals
    meal_subtotals = {}
    for m_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
        m_logs = meals[m_type]
        meal_subtotals[m_type] = {
            'calories': round(sum(item['calories'] for item in m_logs), 1),
            'protein': round(sum(item['protein'] for item in m_logs), 1),
            'carbs': round(sum(item['carbs'] for item in m_logs), 1),
            'fat': round(sum(item['fat'] for item in m_logs), 1)
        }

    calorie_target = profile['daily_calorie_target'] if profile else 2000
    calories_remaining = max(0, round(calorie_target - totals['calories'], 1))

    return render_template(
        'food_tracker.html',
        profile=profile,
        log_date=log_date,
        foods=foods,
        meals=meals,
        meal_subtotals=meal_subtotals,
        totals=totals,
        calorie_target=calorie_target,
        calories_remaining=calories_remaining
    )


@diet_bp.route('/food-tracker/delete/<int:log_id>', methods=['POST'])
@login_required
def delete_food_log(log_id):
    user_id = session['user_id']
    date_str = request.form.get('date', datetime.date.today().isoformat())
    FoodLogModel.delete_log(log_id, user_id)
    flash('Food entry deleted.', 'info')
    return redirect(url_for('diet.food_tracker', date=date_str))


@diet_bp.route('/food-tracker/custom-food', methods=['POST'])
@login_required
def create_custom_food():
    user_id = session['user_id']
    name = request.form.get('name', '').strip()
    category = request.form.get('category', 'Custom').strip()
    cal = request.form.get('calories_per_100g', 0)
    p = request.form.get('protein_per_100g', 0)
    c = request.form.get('carbs_per_100g', 0)
    f = request.form.get('fat_per_100g', 0)

    if not name:
        flash('Food item name is required.', 'error')
        return redirect(url_for('diet.food_tracker'))

    try:
        FoodModel.add_custom(user_id, name, category, cal, p, c, f)
        flash(f'Custom food "{name}" added to your database!', 'success')
    except Exception as e:
        flash(f'Error adding custom food: {str(e)}', 'error')

    return redirect(url_for('diet.food_tracker'))


@diet_bp.route('/api/food-search')
@login_required
def api_food_search():
    user_id = session['user_id']
    query = request.args.get('q', '').strip()
    items = FoodModel.get_all(search=query, user_id=user_id)
    data = []
    for item in items:
        data.append({
            'id': item['id'],
            'name': item['name'],
            'category': item['category'],
            'calories_per_100g': item['calories_per_100g'],
            'protein_per_100g': item['protein_per_100g'],
            'carbs_per_100g': item['carbs_per_100g'],
            'fat_per_100g': item['fat_per_100g'],
            'serving_unit': item['serving_unit']
        })
    return jsonify({'results': data})


@diet_bp.route('/water-tracker', methods=['GET', 'POST'])
@login_required
def water_tracker():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    today = datetime.date.today().isoformat()

    if request.method == 'POST':
        amount = request.form.get('amount_ml', 250)
        try:
            WaterModel.add_water(user_id, float(amount), today)
            flash(f'Logged {amount} ml of water!', 'success')
        except Exception as e:
            flash(f'Error logging water: {str(e)}', 'error')
        return redirect(url_for('diet.water_tracker'))

    water_today = WaterModel.get_daily_water(user_id, today)
    water_target = profile['water_target'] if profile else 2500
    water_target = max(1000, water_target)
    water_pct = min(100, round((water_today / water_target) * 100, 1))
    water_history = WaterModel.get_water_history(user_id, days=7)

    return render_template(
        'water_tracker.html',
        profile=profile,
        today=today,
        water_today=water_today,
        water_target=water_target,
        water_pct=water_pct,
        water_history=water_history
    )


@diet_bp.route('/meal-planner', methods=['GET', 'POST'])
@login_required
def meal_planner():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    foods = FoodModel.get_all(user_id=user_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_plan':
            plan_name = request.form.get('plan_name', 'My Meal Plan').strip()
            description = request.form.get('description', '').strip()
            plan_id = MealPlanModel.create_plan(user_id, plan_name, description)
            flash(f'Created meal plan template "{plan_name}"! Now add items to it.', 'success')
            return redirect(url_for('diet.meal_planner'))

        elif action == 'add_item':
            plan_id = request.form.get('plan_id')
            food_item_id = request.form.get('food_item_id')
            food_name = request.form.get('food_name', '')
            meal_type = request.form.get('meal_type', 'breakfast')
            grams = float(request.form.get('quantity_grams', 100))
            cal_100 = float(request.form.get('calories_per_100g', 0))
            p_100 = float(request.form.get('protein_per_100g', 0))
            c_100 = float(request.form.get('carbs_per_100g', 0))
            f_100 = float(request.form.get('fat_per_100g', 0))

            ratio = grams / 100.0
            MealPlanModel.add_plan_item(
                plan_id=plan_id,
                food_item_id=food_item_id,
                food_name=food_name,
                meal_type=meal_type,
                grams=grams,
                cal=round(cal_100 * ratio, 1),
                p=round(p_100 * ratio, 1),
                c=round(c_100 * ratio, 1),
                f=round(f_100 * ratio, 1)
            )
            flash(f'Added {food_name} to planned meals!', 'success')
            return redirect(url_for('diet.meal_planner'))

        elif action == 'log_to_diary':
            plan_id = request.form.get('plan_id')
            target_date = request.form.get('target_date', datetime.date.today().isoformat())
            MealPlanModel.log_plan_to_diary(user_id, plan_id, target_date)
            flash(f'Plan successfully logged to your Food Tracker for {target_date}!', 'success')
            return redirect(url_for('diet.food_tracker', date=target_date))

        elif action == 'delete_plan':
            plan_id = request.form.get('plan_id')
            MealPlanModel.delete_plan(plan_id, user_id)
            flash('Meal plan removed.', 'info')
            return redirect(url_for('diet.meal_planner'))

    saved_plans = MealPlanModel.get_user_plans(user_id)
    return render_template('meal_planner.html', profile=profile, foods=foods, saved_plans=saved_plans)
