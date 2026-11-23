import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from routes.auth_routes import login_required
from models import ProfileModel, ExerciseModel, WorkoutTrackerModel

fitness_bp = Blueprint('fitness', __name__)

@fitness_bp.route('/fitness-goals')
@login_required
def fitness_goals():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    return render_template('fitness_goals.html', profile=profile)


@fitness_bp.route('/home-workouts')
@login_required
def home_workouts():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    muscle = request.args.get('muscle')

    exercises = ExerciseModel.get_all(muscle=muscle, location='Home')
    muscle_groups = ['Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps', 'Legs', 'Abs', 'Full Body']

    return render_template(
        'home_workouts.html',
        profile=profile,
        exercises=exercises,
        selected_muscle=muscle,
        muscle_groups=muscle_groups
    )


@fitness_bp.route('/gym-workouts')
@login_required
def gym_workouts():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    muscle = request.args.get('muscle', 'Chest')

    exercises = ExerciseModel.get_all(muscle=muscle, location='Gym')
    muscle_groups = ['Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps', 'Legs', 'Abs']

    return render_template(
        'gym_workouts.html',
        profile=profile,
        exercises=exercises,
        selected_muscle=muscle,
        muscle_groups=muscle_groups
    )


@fitness_bp.route('/exercises')
@login_required
def exercise_library():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)

    search = request.args.get('search')
    muscle = request.args.get('muscle')
    location = request.args.get('location')
    equipment = request.args.get('equipment')
    difficulty = request.args.get('difficulty')

    exercises = ExerciseModel.get_all(
        muscle=muscle,
        location=location,
        equipment=equipment,
        difficulty=difficulty,
        search=search
    )

    muscle_groups = ['Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps', 'Legs', 'Abs', 'Full Body']
    equipments = ['Bodyweight', 'Machine', 'Dumbbells', 'Barbell', 'Cables']
    difficulties = ['Beginner', 'Intermediate', 'Advanced']

    return render_template(
        'exercise_library.html',
        profile=profile,
        exercises=exercises,
        search=search,
        selected_muscle=muscle,
        selected_location=location,
        selected_equipment=equipment,
        selected_difficulty=difficulty,
        muscle_groups=muscle_groups,
        equipments=equipments,
        difficulties=difficulties
    )


@fitness_bp.route('/workout-planner', methods=['GET', 'POST'])
@login_required
def workout_planner():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)

    # Defaults from profile
    goal = profile['fitness_goal'] if profile else 'Muscle Building'
    days = int(request.args.get('days', profile['workout_days'] if profile else 4))
    experience = request.args.get('experience', profile['experience_level'] if profile else 'Beginner')
    equipment = request.args.get('equipment', profile['workout_location'] if profile else 'Both')

    if request.method == 'POST':
        days = int(request.form.get('workout_days', 4))
        experience = request.form.get('experience_level', 'Beginner')
        equipment = request.form.get('workout_location', 'Both')

        # Update profile preferences
        from database import get_db
        db = get_db()
        db.execute('''
            UPDATE user_profiles SET
                workout_days = ?, experience_level = ?, workout_location = ?
            WHERE user_id = ?
        ''', (days, experience, equipment, user_id))
        db.commit()
        flash('Workout planner preferences updated!', 'success')
        return redirect(url_for('fitness.workout_planner', days=days, experience=experience, equipment=equipment))

    plan_data = WorkoutTrackerModel.generate_workout_plan(
        fitness_goal=goal,
        days_per_week=days,
        experience=experience,
        equipment=equipment
    )

    return render_template(
        'workout_planner.html',
        profile=profile,
        goal=goal,
        days=days,
        experience=experience,
        equipment=equipment,
        plan=plan_data
    )


@fitness_bp.route('/workout-tracker', methods=['GET', 'POST'])
@login_required
def workout_tracker():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    today = datetime.date.today().isoformat()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'log_set':
            session_name = request.form.get('session_name', 'Upper Body Session').strip()
            exercise_name = request.form.get('exercise_name', 'Bench Press').strip()
            set_number = int(request.form.get('set_number', 1))
            weight_kg = float(request.form.get('weight_kg', 0))
            reps = int(request.form.get('completed_reps', 10))
            workout_date = request.form.get('workout_date', today)

            # Find or create session for today
            from database import get_db
            db = get_db()
            sess = db.execute('''
                SELECT id FROM workout_sessions
                WHERE user_id = ? AND workout_date = ? AND session_name = ?
            ''', (user_id, workout_date, session_name)).fetchone()

            if sess:
                session_id = sess['id']
            else:
                session_id = WorkoutTrackerModel.log_session(user_id, session_name, workout_date)

            WorkoutTrackerModel.log_set(
                session_id=session_id,
                user_id=user_id,
                exercise_id=None,
                exercise_name=exercise_name,
                set_num=set_number,
                target_reps=reps,
                completed_reps=reps,
                weight_kg=weight_kg,
                log_date=workout_date
            )
            flash(f'Logged Set {set_number} for {exercise_name}: {weight_kg}kg x {reps} reps!', 'success')
            return redirect(url_for('fitness.workout_tracker'))

    # Load sessions and PR stats
    recent_sessions = WorkoutTrackerModel.get_user_sessions(user_id, limit=8)
    stats = WorkoutTrackerModel.get_stats(user_id)
    exercises = ExerciseModel.get_all()

    return render_template(
        'workout_tracker.html',
        profile=profile,
        today=today,
        recent_sessions=recent_sessions,
        stats=stats,
        exercises=exercises
    )


@fitness_bp.route('/3d-anatomy')
@login_required
def muscle_anatomy():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    return render_template('muscle_anatomy.html', profile=profile)


@fitness_bp.route('/api/muscle-exercises/<muscle>')
@login_required
def api_muscle_exercises(muscle):
    from database import get_db
    db = get_db()
    m_clean = muscle.lower().replace('_', '-').strip()

    # Specialized queries for anatomical precision
    specific_keywords = {
        'front-deltoids': ['Front Deltoid', 'Anterior Deltoid', 'Anterior & Medial', 'Shoulder Press', 'Pike Push-up'],
        'side-deltoids': ['Lateral Raise', 'Lateral Deltoid', 'Side Shoulder', 'Dumbbell Shoulder Press'],
        'rear-deltoids': ['Rear Deltoid', 'Posterior Deltoid', 'Reverse Pec Deck', 'Face Pull'],
        'chest': ['Chest', 'Pectoral', 'Bench Press', 'Push-up'],
        'biceps': ['Bicep', 'Biceps Brachii', 'Brachialis', 'Curl'],
        'triceps': ['Tricep', 'Pushdown', 'Extension Machine', 'Dips'],
        'forearms': ['Forearm', 'Brachioradialis', 'Hammer Curl', 'Grip'],
        'abs': ['Abs', 'Abdominal', 'Rectus Abdominis', 'Plank', 'Crunch'],
        'obliques': ['Oblique', 'Plank', 'Twist', 'Crunch'],
        'quadriceps': ['Quad', 'Quadriceps', 'Rectus Femoris', 'Leg Press', 'Leg Extension', 'Squat'],
        'quads': ['Quad', 'Quadriceps', 'Rectus Femoris', 'Leg Press', 'Leg Extension', 'Squat'],
        'calves': ['Calf', 'Calves', 'Gastrocnemius', 'Soleus'],
        'glutes': ['Glute', 'Gluteus', 'Hip Abduction', 'Glute Bridge', 'Lunge'],
        'hamstrings': ['Hamstring', 'Biceps Femoris', 'Leg Curl'],
        'lats': ['Lat', 'Latissimus', 'Pulldown', 'Pull-up', 'Cable Row'],
        'traps': ['Trap', 'Trapezius', 'Shrug', 'T-Bar', 'Face Pull'],
        'lower-back': ['Spinal Erector', 'Erectors', 'Lower Back', 'Back Extension', 'Hyperextension']
    }

    keywords = specific_keywords.get(m_clean)
    if keywords:
        where_clauses = []
        params = []
        for kw in keywords:
            where_clauses.append("(name LIKE ? OR muscle_group LIKE ? OR secondary_muscles LIKE ?)")
            params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
        query = f"SELECT * FROM exercises WHERE {' OR '.join(where_clauses)} ORDER BY name ASC"
        exercises = db.execute(query, params).fetchall()
    else:
        # Fallback to general muscle group
        muscle_map = {
            'shoulders': 'Shoulders',
            'back': 'Back',
            'legs': 'Legs'
        }
        target_group = muscle_map.get(m_clean, m_clean.capitalize())
        exercises = ExerciseModel.get_by_muscle(target_group)

    gym_list = []
    home_list = []

    for ex in exercises:
        item = {
            'id': ex['id'],
            'name': ex['name'],
            'muscle_group': ex['muscle_group'],
            'secondary': ex['secondary_muscles'],
            'location': ex['location'],
            'equipment': ex['equipment'],
            'machine_name': ex['machine_name'],
            'difficulty': ex['difficulty'],
            'sets': ex['recommended_sets'],
            'reps': ex['recommended_reps'],
            'rest': ex['rest_seconds'],
            'technique': ex['technique'],
            'steps': ex['step_by_step'],
            'posture': ex['posture_tips'],
            'mistakes': ex['common_mistakes'],
            'safety': ex['safety_precautions']
        }
        if ex['location'] in ['Gym', 'Both']:
            gym_list.append(item)
        if ex['location'] in ['Home', 'Both']:
            home_list.append(item)

    return jsonify({
        'muscle': m_clean.replace('-', ' ').title(),
        'gym_exercises': gym_list,
        'home_exercises': home_list
    })
