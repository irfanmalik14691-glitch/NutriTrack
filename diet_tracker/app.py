import os
from flask import Flask, render_template
from dotenv import load_dotenv
from database import close_db, init_db
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp
from routes.diet_routes import diet_bp
from routes.fitness_routes import fitness_bp
from routes.progress_routes import progress_bp
from routes.assistant_routes import assistant_bp

# Load environment variables if .env exists
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nutritrack-super-secret-key-2026-cse-btech')

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(diet_bp)
    app.register_blueprint(fitness_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(assistant_bp)

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Custom Jinja filters
    @app.template_filter('round_val')
    def round_val_filter(val, decimals=1):
        try:
            return round(float(val), decimals)
        except (ValueError, TypeError):
            return val

    # 404 & 500 Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content='<div class="glass-card text-center my-5 p-5"><h2>Page Not Found (404)</h2><p class="text-muted">The requested fitness resource does not exist.</p><a href="/" class="btn-primary-glow">Back to Safety</a></div>'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('base.html', content='<div class="glass-card text-center my-5 p-5"><h2>System Error (500)</h2><p class="text-muted">An internal error occurred. Please refresh or try again.</p><a href="/dashboard" class="btn-primary-glow">Back to Dashboard</a></div>'), 500

    # Ensure DB is created and seeded
    with app.app_context():
        init_db(app)

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"============================================================")
    print(f"  NutriTrack 3D Fitness & Diet Platform Running on:")
    print(f"  Local URL: http://127.0.0.1:{port}")
    print(f"============================================================")
    app.run(host='0.0.0.0', port=port, debug=True)
