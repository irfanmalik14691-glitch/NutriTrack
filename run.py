import sys
import os

# Add diet_tracker to path
current_dir = os.path.dirname(os.path.abspath(__file__))
tracker_dir = os.path.join(current_dir, 'diet_tracker')
if tracker_dir not in sys.path:
    sys.path.insert(0, tracker_dir)

from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"============================================================")
    print(f"  NutriTrack 3D Fitness & Diet Platform Running on:")
    print(f"  Local URL: http://127.0.0.1:{port}")
    print(f"============================================================")
    app.run(host='0.0.0.0', port=port, debug=True)
