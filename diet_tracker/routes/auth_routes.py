from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from models import UserModel, ProfileModel

auth_bp = Blueprint('auth', __name__)

def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic validations
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('register.html', username=username, email=email)

        if not email or '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html', username=username, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html', username=username, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html', username=username, email=email)

        if UserModel.get_by_username(username):
            flash('Username already registered. Please choose another or login.', 'error')
            return render_template('register.html', username=username, email=email)

        if UserModel.get_by_email(email):
            flash('Email already registered. Please login.', 'error')
            return render_template('register.html', username=username, email=email)

        user_id = UserModel.create_user(username, email, password)
        if user_id:
            session.clear()
            session['user_id'] = user_id
            session['username'] = username

            # Create default profile
            ProfileModel.save_or_update(user_id, {
                'name': username.capitalize(),
                'age': 25,
                'gender': 'male',
                'height': 175.0,
                'current_weight': 70.0,
                'target_weight': 68.0,
                'activity_level': 'moderate',
                'fitness_goal': 'Muscle Building'
            })

            flash('Welcome to NutriTrack! Your account and customized metabolic profile have been created.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('An error occurred during registration. Please try again.', 'error')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()
        password = request.form.get('password', '')

        if not login_input or not password:
            flash('Please provide both username/email and password.', 'error')
            return render_template('login.html', login_input=login_input)

        user = UserModel.get_by_username(login_input)
        if not user:
            user = UserModel.get_by_email(login_input)

        if user and UserModel.verify_password(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']

            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username/email or password.', 'error')
            return render_template('login.html', login_input=login_input)

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.landing'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = UserModel.get_by_id(user_id)
    profile_data = ProfileModel.get_by_user_id(user_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', 25)
        gender = request.form.get('gender', 'male')
        height = request.form.get('height', 175)
        current_weight = request.form.get('current_weight', 70)
        target_weight = request.form.get('target_weight', 68)
        activity_level = request.form.get('activity_level', 'moderate')
        fitness_goal = request.form.get('fitness_goal', 'Muscle Building')
        experience_level = request.form.get('experience_level', 'Beginner')
        workout_location = request.form.get('workout_location', 'Both')
        workout_days = request.form.get('workout_days', 4)
        workout_time = request.form.get('workout_time', 45)

        try:
            profile_data = ProfileModel.save_or_update(user_id, {
                'name': name or user['username'],
                'age': int(age),
                'gender': gender,
                'height': float(height),
                'current_weight': float(current_weight),
                'target_weight': float(target_weight),
                'activity_level': activity_level,
                'fitness_goal': fitness_goal,
                'experience_level': experience_level,
                'workout_location': workout_location,
                'workout_days': int(workout_days),
                'workout_time': int(workout_time)
            })
            flash('Profile and nutrition targets successfully updated!', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')

    return render_template('profile.html', user=user, profile=profile_data)
