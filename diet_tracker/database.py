import sqlite3
import os
from flask import g

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'diet_tracker.db')

def get_db():
    if 'db' not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app=None):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create tables
    cursor.executescript('''
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        height REAL NOT NULL,
        current_weight REAL NOT NULL,
        target_weight REAL NOT NULL,
        activity_level TEXT NOT NULL,
        fitness_goal TEXT NOT NULL,
        experience_level TEXT DEFAULT 'Beginner',
        workout_location TEXT DEFAULT 'Both',
        workout_days INTEGER DEFAULT 4,
        workout_time INTEGER DEFAULT 45,
        bmi REAL,
        bmr REAL,
        tdee REAL,
        daily_calorie_target REAL,
        protein_target REAL,
        carbs_target REAL,
        fat_target REAL,
        water_target REAL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS food_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        calories_per_100g REAL NOT NULL,
        protein_per_100g REAL NOT NULL,
        carbs_per_100g REAL NOT NULL,
        fat_per_100g REAL NOT NULL,
        serving_unit TEXT DEFAULT 'grams',
        is_custom INTEGER DEFAULT 0,
        created_by INTEGER REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS food_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        food_item_id INTEGER REFERENCES food_items(id) ON DELETE SET NULL,
        food_name TEXT NOT NULL,
        meal_type TEXT NOT NULL,
        quantity_grams REAL NOT NULL,
        calories REAL NOT NULL,
        protein REAL NOT NULL,
        carbs REAL NOT NULL,
        fat REAL NOT NULL,
        log_date DATE NOT NULL,
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS water_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        amount_ml REAL NOT NULL,
        log_date DATE NOT NULL,
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS weight_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        weight REAL NOT NULL,
        notes TEXT,
        log_date DATE NOT NULL,
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS meal_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        plan_name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS meal_plan_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meal_plan_id INTEGER NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
        food_item_id INTEGER REFERENCES food_items(id) ON DELETE SET NULL,
        food_name TEXT NOT NULL,
        meal_type TEXT NOT NULL,
        quantity_grams REAL NOT NULL,
        calories REAL NOT NULL,
        protein REAL NOT NULL,
        carbs REAL NOT NULL,
        fat REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        muscle_group TEXT NOT NULL,
        secondary_muscles TEXT,
        location TEXT NOT NULL,
        equipment TEXT NOT NULL,
        machine_name TEXT,
        difficulty TEXT NOT NULL,
        recommended_sets INTEGER DEFAULT 3,
        recommended_reps TEXT DEFAULT '10-12',
        rest_seconds INTEGER DEFAULT 60,
        technique TEXT NOT NULL,
        step_by_step TEXT NOT NULL,
        posture_tips TEXT NOT NULL,
        common_mistakes TEXT NOT NULL,
        safety_precautions TEXT NOT NULL,
        icon_type TEXT
    );

    CREATE TABLE IF NOT EXISTS workout_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        session_name TEXT NOT NULL,
        workout_date DATE NOT NULL,
        duration_minutes INTEGER DEFAULT 45,
        notes TEXT,
        is_completed INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS workout_set_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        exercise_id INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
        exercise_name TEXT NOT NULL,
        set_number INTEGER NOT NULL,
        target_reps INTEGER,
        completed_reps INTEGER,
        weight_kg REAL,
        is_completed INTEGER DEFAULT 1,
        log_date DATE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS user_workout_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        split_type TEXT NOT NULL,
        schedule_json TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Seed Default Indian & International Foods
    cursor.execute("SELECT COUNT(*) FROM food_items WHERE is_custom = 0")
    if cursor.fetchone()[0] == 0:
        default_foods = [
            # Common Indian Staples requested & essential
            ('Roti (Whole Wheat Chapati)', 'Indian Staples', 297, 11.0, 56.0, 3.5, 'grams'),
            ('Rice (Cooked White Basmati)', 'Indian Staples', 130, 2.7, 28.0, 0.3, 'grams'),
            ('Brown Rice (Cooked)', 'Indian Staples', 111, 2.6, 23.0, 0.9, 'grams'),
            ('Dal (Cooked Yellow Moong/Toor)', 'Indian Staples', 116, 7.5, 17.5, 1.8, 'grams'),
            ('Paneer (Fresh Indian Cottage Cheese)', 'Dairy', 296, 18.3, 3.4, 23.0, 'grams'),
            ('Low Fat Paneer', 'Dairy', 170, 25.0, 4.0, 6.0, 'grams'),
            ('Cow Milk (Whole)', 'Dairy', 62, 3.2, 4.8, 3.4, 'grams'),
            ('Toned Milk (3% fat)', 'Dairy', 58, 3.1, 4.7, 3.0, 'grams'),
            ('Curd / Dahi (Plain)', 'Dairy', 60, 3.5, 4.7, 3.0, 'grams'),
            ('Greek Yogurt (Hung Curd)', 'Dairy', 97, 10.0, 3.6, 5.0, 'grams'),
            ('Eggs (Whole Boiled)', 'Protein', 155, 13.0, 1.1, 11.0, 'grams'),
            ('Egg Whites (Boiled)', 'Protein', 52, 11.0, 0.7, 0.2, 'grams'),
            ('Chicken Breast (Cooked, Skinless)', 'Protein', 165, 31.0, 0.0, 3.6, 'grams'),
            ('Chicken Curry (Indian Style)', 'Protein', 180, 19.0, 4.5, 9.5, 'grams'),
            ('Banana (Fresh)', 'Fruits', 89, 1.1, 22.8, 0.3, 'grams'),
            ('Apple (Fresh with Skin)', 'Fruits', 52, 0.3, 13.8, 0.2, 'grams'),
            ('Rolled Oats (Raw)', 'Grains', 389, 16.9, 66.3, 6.9, 'grams'),
            ('Peanut Butter (Natural Unsweetened)', 'Snacks', 588, 25.0, 20.0, 50.0, 'grams'),
            ('Almonds (Raw)', 'Snacks', 579, 21.2, 21.6, 49.9, 'grams'),
            ('Walnuts', 'Snacks', 654, 15.2, 13.7, 65.2, 'grams'),
            ('Soya Chunks (Nutrela Raw)', 'Protein', 345, 52.0, 33.0, 0.5, 'grams'),
            ('Soya Chunks Curry (Cooked)', 'Protein', 140, 18.0, 10.0, 3.0, 'grams'),
            ('Poha (Flattened Rice Cooked)', 'Indian Staples', 130, 2.5, 23.0, 3.0, 'grams'),
            ('Idli (Steamed Rice & Urad)', 'Indian Staples', 132, 4.5, 26.0, 1.0, 'grams'),
            ('Dosa (Plain, Crisp)', 'Indian Staples', 168, 3.9, 29.0, 3.7, 'grams'),
            ('Rajma (Cooked Kidney Bean Curry)', 'Indian Staples', 127, 8.7, 22.8, 0.5, 'grams'),
            ('Chole / Chana Masala (Cooked)', 'Indian Staples', 164, 8.9, 27.4, 2.6, 'grams'),
            ('Sprouted Moong Salad', 'Indian Staples', 105, 7.0, 19.0, 0.8, 'grams'),
            ('Fish (Rohu/Katla Grilled)', 'Protein', 102, 19.7, 0.0, 2.3, 'grams'),
            ('Whey Protein Isolate (Dry Powder)', 'Protein', 370, 80.0, 3.0, 1.5, 'grams'),
            ('Sattu (Roasted Gram Flour)', 'Indian Staples', 413, 20.6, 64.0, 7.2, 'grams'),
            ('Sweet Potato (Boiled)', 'Vegetables', 86, 1.6, 20.1, 0.1, 'grams'),
            ('Green Salad (Cucumber, Tomato, Onion)', 'Vegetables', 20, 0.8, 4.0, 0.2, 'grams'),
            ('Mixed Vegetable Sabzi (Dry)', 'Vegetables', 95, 2.2, 10.5, 5.0, 'grams')
        ]
        cursor.executemany('''
            INSERT INTO food_items (name, category, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, serving_unit, is_custom)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        ''', default_foods)

    # Seed Default Home & Gym Exercises with Complete Step-by-Step, Posture, and Machine Specs
    cursor.execute("SELECT COUNT(*) FROM exercises")
    if cursor.fetchone()[0] == 0:
        default_exercises = [
            # CHEST - Gym
            (
                'Barbell Flat Bench Press', 'bench-press', 'Chest', 'Triceps, Front Deltoids', 'Gym', 'Barbell', 'Flat Bench Press Rack',
                'Intermediate', 4, '8-12', 90,
                'Foundational compound movement for overall pectoral thickness and upper body pushing strength.',
                '1. Lie flat on the bench with eyes directly under the bar.\n2. Grip bar slightly wider than shoulder-width with wrists straight.\n3. Unrack, lower the bar smoothly to mid-chest while tucking elbows at 45 degrees.\n4. Drive through palms and feet to press bar back up.',
                'Keep 5 points of contact: head, upper back, glutes on bench, and both feet planted firmly on the floor. Maintain a natural slight arch in lower back.',
                'Flaring elbows out at 90 degrees (causes rotator cuff impingement); bouncing the barbell off the sternum; lifting glutes off the bench.',
                'Always use safety collars; utilize safety spotter pins or request a spotter for heavy sets.',
                'dumbbell'
            ),
            (
                'Incline Dumbbell / Barbell Bench Press', 'incline-bench-press', 'Chest', 'Upper Clavicular Pectoral, Front Deltoids', 'Gym', 'Dumbbells', 'Adjustable Bench (30-45 deg)',
                'Intermediate', 3, '8-10', 75,
                'Targets the upper chest (clavicular head) for a full, aesthetic chest shelf.',
                '1. Set bench to a 30 to 45 degree angle.\n2. Retract scapula, press weights straight up above upper chest.\n3. Lower dumbbells under control until elbows reach chest depth.\n4. Squeeze upper chest hard at the top without clanking dumbbells.',
                'Set the incline no higher than 45 degrees to avoid shifting load predominantly to front deltoids. Keep wrists aligned over forearms.',
                'Setting bench angle too steep (>60 degrees turning it into a shoulder press); over-arching lower back.',
                'Do not let dumbbells drift backwards behind the head. Drop safely to thighs if reaching muscular failure.',
                'dumbbell'
            ),
            (
                'Seated Chest Press Machine', 'chest-press-machine', 'Chest', 'Pectoralis Major, Anterior Deltoids, Triceps', 'Gym', 'Machine', 'Chest Press Machine',
                'Beginner', 3, '10-12', 60,
                'Superb machine for safe, isolated pectoral overload with a fixed guided path suitable for all fitness levels.',
                '1. Adjust seat height so handles align with mid-chest level.\n2. Sit back firmly against pad, plant feet flat, and grasp handles.\n3. Exhale and press handles forward until arms are extended (do not lock elbows).\n4. Inhale and slowly return weights over 2-3 seconds until you feel a gentle chest stretch.',
                'Keep shoulder blades pinned to the back pad throughout the repetition. Maintain neutral wrists.',
                'Setting seat too high or too low, stressing the shoulder joint; letting weights slam on the stack between reps.',
                'Use the foot assist pedal to bring handles into starting position safely without overstretching shoulder capsules.',
                'cogs'
            ),
            (
                'Pec Deck / Butterfly Machine', 'pec-deck-machine', 'Chest', 'Sternal Pectoralis, Anterior Deltoid', 'Gym', 'Machine', 'Pec Deck / Fly Machine',
                'Beginner', 3, '12-15', 60,
                'High-tension isolation machine providing constant tension across the entire chest horizontal adduction arc.',
                '1. Adjust seat so elbows and forearms rest comfortably against pads at mid-chest level (arms roughly 90 degrees).\n2. Sit tall, chest up, core engaged.\n3. Bring pads together in front of your chest in a smooth hugging motion.\n4. Squeeze pectorals for 1 full second at peak contraction, then slowly resist back.',
                'Imagine hugging a large barrel. Focus on driving your elbows together rather than using hand grip pressure.',
                'Allowing the weight to pull elbows too far back past the shoulder plane; shrugging shoulders up.',
                'Never set the start range beyond your active shoulder flexibility to prevent anterior shoulder capsule strain.',
                'heart'
            ),
            (
                'Standing Cable Crossover', 'cable-crossover', 'Chest', 'Lower & Mid Pectoralis, Serratus', 'Gym', 'Cables', 'Dual Adjustable Cable Column',
                'Intermediate', 3, '12-15', 60,
                'Versatile cable exercise offering continuous mechanical tension throughout the complete range of motion.',
                '1. Set pulleys at top or mid height. Attach single D-handles.\n2. Take a small step forward in a staggered stance, slight forward torso lean.\n3. With a slight bend in elbows, sweep handles down and together across mid-torso.\n4. Cross wrists slightly at peak squeeze for maximum inner-pectoral recruitment.',
                'Maintain consistent slight elbow bend throughout the movement; do not turn it into a press.',
                'Swinging the torso forward and back to gain momentum; letting cable stack snap back violently.',
                'Ensure both cable pins are securely locked into the weight stack at identical pin heights.',
                'exchange-alt'
            ),

            # CHEST - Home
            (
                'Standard Push-ups', 'push-ups', 'Chest', 'Triceps, Core, Front Deltoids', 'Home', 'Bodyweight', 'None',
                'Beginner', 3, '12-20', 60,
                'The king of upper body home bodyweight pressing exercises, training chest, triceps, and anterior core stability.',
                '1. Place hands on floor slightly wider than shoulder width, fingers spread.\n2. Form a straight line from heels to head.\n3. Lower your chest until it hovers 1 inch off the ground, elbows at 45 degrees.\n4. Push the floor away dynamically to return to top plank.',
                'Squeeze glutes and brace abs tightly so lower back does not sag. Keep neck neutral looking 6 inches ahead of hands.',
                'Flaring elbows outward like a T-shape; drooping hips or hiking glutes into the air; half reps.',
                'If wrists hurt, perform on knuckles, push-up bars, or dumbbells on the floor.',
                'child'
            ),
            (
                'Incline Push-ups (Hands Elevated)', 'incline-push-ups', 'Chest', 'Lower Pectoralis, Triceps', 'Home', 'Bodyweight', 'Sturdy Chair / Sofa / Countertop',
                'Beginner', 3, '10-15', 45,
                'Beginner-friendly push-up variation reducing bodyweight resistance while reinforcing correct pushing mechanics.',
                '1. Place hands on a secure elevated surface like a bed frame, couch, or table.\n2. Step back into a strong plank line.\n3. Lower chest to the edge of the surface smoothly.\n4. Press back up while maintaining rigid spine posture.',
                'Maintain tight core and glute activation. Adjust elevation height to match strength level.',
                'Bending at hips rather than the whole body moving as a single rigid board.',
                'Ensure the elevated surface is solid and will not slide on the floor.',
                'child'
            ),

            # BACK - Gym
            (
                'Lat Pulldown Machine', 'lat-pulldown', 'Back', 'Latissimus Dorsi, Biceps, Rear Deltoids, Rhomboids', 'Gym', 'Machine', 'Cable Lat Pulldown Machine',
                'Beginner', 4, '10-12', 75,
                'Essential vertical pulling movement for developing V-taper back width and posture support.',
                '1. Adjust thigh pad securely over legs so feet remain flat on the ground.\n2. Grasp wide bar with overhand grip just outside shoulder width.\n3. Lean back 10-15 degrees, drive elbows down and back toward your hip pockets.\n4. Pull bar to upper chest/collarbone, hold contraction for 1 second, then control back up.',
                'Lead the movement by depressing your shoulder blades first, then bending elbows. Focus on pulling with elbows, not wrists.',
                'Pulling bar behind the neck (dangerous for cervical spine); leaning back excessively (>45 degrees) turning it into a row.',
                'Do not let the weight stack pull your shoulders up aggressively into your ears at the top.',
                'arrows-alt-v'
            ),
            (
                'Seated Cable Row', 'seated-cable-row', 'Back', 'Rhomboids, Middle Trapezius, Latissimus Dorsi, Erectors', 'Gym', 'Cables', 'Low Row Cable Station',
                'Beginner', 3, '10-12', 60,
                'Horizontal cable pull that thickens the mid-back and corrects rounded shoulders.',
                '1. Sit on bench, place feet on footrests with slight knee bend.\n2. Grasp close-grip V-bar attachment, push back with legs into upright posture.\n3. Pull handle toward lower abdomen/belly button while driving elbows back.\n4. Squeeze shoulder blades together firmly, then extend arms with control.',
                'Keep chest proud and shoulders back. Avoid excessive rocking of the lower back.',
                'Rounding lower back into flexion under load; swinging torso backwards to yank heavy weight.',
                'Keep a slight knee bend; never lock out knees forcefully on the footplates.',
                'bars'
            ),
            (
                'T-Bar Row', 't-bar-row', 'Back', 'Latissimus Dorsi, Trapezius, Rhomboids, Spinal Erectors', 'Gym', 'Barbell', 'T-Bar Row Machine / Landmine Platform',
                'Intermediate', 3, '8-10', 90,
                'Heavy compound back builder delivering high overload to the mid and upper back.',
                '1. Straddle the bar or stand on the T-bar platform with feet shoulder-width.\n2. Hinge at hips to a 45-degree angle with a flat, neutral spine.\n3. Grip handles, pull weight directly into upper abdomen.\n4. Retract scapulae at the apex, then lower weights smoothly without rounding back.',
                'Brace core like taking a punch. Keep weight centered over midfoot.',
                'Using momentum and standing fully upright during the pull; rounding lumbar spine.',
                'Keep neck neutral with spine; do not crane neck upwards.',
                'layer-group'
            ),
            (
                'Assisted Pull-up Machine', 'assisted-pull-up-machine', 'Back', 'Latissimus Dorsi, Biceps, Core', 'Gym', 'Machine', 'Assisted Dip & Pull-up Station',
                'Beginner', 3, '8-10', 75,
                'Counter-weighted machine allowing trainees to build pull-up strength and muscle memory gradually.',
                '1. Select counter-weight pin (higher pin weight = easier assistance).\n2. Step or place knees securely onto the padded platform.\n3. Take wide overhand grip on pull-up handles.\n4. Pull body upward until chin clears the bar level, pause, then lower under full control.',
                'Keep chest elevated and shoulders down. Do not swing knees on the pad.',
                'Setting assistance too low and violently kicking legs; failing to achieve full extension at bottom.',
                'Always step off with one foot first while holding the platform securely to prevent snap-back.',
                'level-up-alt'
            ),
            (
                'Back Extension (Hyperextension Bench)', 'back-extension', 'Back', 'Spinal Erectors, Glutes, Hamstrings', 'Gym', 'Machine', '45-Degree Hyperextension Bench',
                'Beginner', 3, '12-15', 60,
                'Strengthens the posterior chain and lumbar erectors to bulletproof lower back against injury.',
                '1. Position hip thighs on pad just below hip crease so you can bend freely at waist.\n2. Cross arms over chest or behind head.\n3. Lower upper body forward into hinge until hamstrings are stretched.\n4. Contract glutes and lower back to raise torso in line with legs.',
                'Move in a smooth controlled arc. Squeeze glutes at top.',
                'Hyperextending spine backwards past neutral; jerking upper body with ballistic momentum.',
                'Do not hold heavy dumbbells until bodyweight mastery is achieved with 15 clean reps.',
                'redo'
            ),

            # BACK - Home
            (
                'Pull-ups / Chin-ups', 'pull-ups', 'Back', 'Lats, Biceps, Forearms, Upper Back', 'Home', 'Bodyweight', 'Doorway Pull-up Bar',
                'Intermediate', 3, '6-10', 90,
                'The gold-standard upper body vertical pull using pure bodyweight on a doorway or park bar.',
                '1. Grasp pull-up bar with overhand grip wider than shoulders.\n2. Hang with arms straight and core braced.\n3. Drive elbows down to your ribs, pulling chin over the bar.\n4. Lower down with full control until arms are extended.',
                'Engage lats by depressing shoulders before bending elbows. Avoid swinging or kipping.',
                'Kipping legs; not going all the way down (half reps); shrugging shoulders up.',
                'Ensure doorway pull-up bar is safely clamped and load-tested before hanging full weight.',
                'arrow-up'
            ),

            # SHOULDERS - Gym
            (
                'Seated Shoulder Press Machine', 'shoulder-press-machine', 'Shoulders', 'Anterior & Medial Deltoids, Triceps', 'Gym', 'Machine', 'Overhead Shoulder Press Machine',
                'Beginner', 3, '10-12', 75,
                'Safely targets shoulder overhead pressing power with stabilized back support.',
                '1. Adjust seat so handles start at about ear/chin height.\n2. Sit back against pad, feet planted, grip handles firmly.\n3. Press overhead smoothly until arms are almost fully extended.\n4. Lower handles slowly back to ear level over 2 seconds.',
                'Keep elbows directly beneath wrists throughout. Maintain ribcage down.',
                'Arching lower back off the pad to turn it into an incline chest press; locking out elbows violently.',
                'Avoid dropping weights below shoulder height if you have limited shoulder mobility.',
                'cube'
            ),
            (
                'Seated Dumbbell Shoulder Press', 'dumbbell-shoulder-press', 'Shoulders', 'Deltoids (Front & Side), Triceps, Upper Traps', 'Gym', 'Dumbbells', 'Adjustable Bench (80 deg)',
                'Intermediate', 3, '8-10', 75,
                'Classic free-weight overhead builder developing unilateral shoulder strength and stability.',
                '1. Sit on bench angled at 75-80 degrees, kick dumbbells up to shoulder height with knees.\n2. Turn palms slightly inward at a 30-degree scaption plane.\n3. Press dumbbells upward together over mid-head.\n4. Lower smoothly until dumbbells tap top of deltoids.',
                'Press in the natural scapular plane rather than elbows flared flat in the frontal plane.',
                'Colliding dumbbells loudly at top; pressing weight forwards instead of vertically.',
                'Keep core tight to protect lower back. Drop dumbbells safely to knees if failing.',
                'dumbbell'
            ),
            (
                'Lateral Raise Machine', 'lateral-raise-machine', 'Shoulders', 'Lateral Deltoids (Side Shoulders)', 'Gym', 'Machine', 'Lateral Deltoid Machine',
                'Beginner', 3, '12-15', 60,
                'Isolates side delts for capped 3D round shoulder width with continuous resistance curve.',
                '1. Sit upright with chest pad support or back support.\n2. Rest side of forearms/elbows against padded lever arms.\n3. Raise arms out to sides until elbows reach shoulder height (parallel to floor).\n4. Hold at the top for half a second, then lower with resistance.',
                'Think of pushing pads out toward the walls rather than lifting with traps.',
                'Using momentum or swinging torso; hiking shoulders up to neck with trapezius dominance.',
                'Do not raise elbows higher than shoulder level to avoid impingement.',
                'expand-arrows-alt'
            ),
            (
                'Reverse Pec Deck (Rear Delt Fly)', 'reverse-pec-deck', 'Shoulders', 'Posterior Deltoids, Rhomboids, Trapezius', 'Gym', 'Machine', 'Rear Delt Fly / Reverse Pec Deck Machine',
                'Beginner', 3, '12-15', 60,
                'Critical posture machine targeting neglected rear shoulder heads for complete 3D deltoid development.',
                '1. Sit facing the machine pad with chest pressed gently against it.\n2. Adjust handles so arms are horizontal with shoulders.\n3. Grasp neutral or horizontal handles with loose grip.\n4. Sweep arms horizontally back in a wide arc, squeezing the back of your shoulders.',
                'Focus strictly on pulling with rear delts. Keep shoulders down away from ears.',
                'Bending elbows excessively and pulling with biceps; shrugging upper traps.',
                'Start with moderate weight; rear delts respond best to controlled hypertrophy tempos.',
                'history'
            ),
            (
                'Face Pull (Cable)', 'face-pull', 'Shoulders', 'Rear Deltoids, Rotator Cuff (External Rotators), Lower Traps', 'Gym', 'Cables', 'Cable Column with Rope Attachment',
                'Beginner', 3, '15-20', 60,
                'The ultimate shoulder health and posture exercise, strengthening external rotators.',
                '1. Set cable pulley to eye height with double rope attachment.\n2. Grip rope ends with thumbs pointing backward.\n3. Step back, pull rope toward nose/eyes while separating hands apart.\n4. End in a double biceps pose with knuckles facing backward, holding 1 second.',
                'Drive elbows high and back; externally rotate forearms at the peak contraction.',
                'Pulling downwards to the chest; using heavy body sway; allowing elbows to drop.',
                'Keep weight moderate; this is an endurance and corrective muscle pattern.',
                'mask'
            ),

            # SHOULDERS - Home
            (
                'Pike Push-ups', 'pike-push-ups', 'Shoulders', 'Anterior Deltoids, Triceps, Upper Chest', 'Home', 'Bodyweight', 'Floor / Mat',
                'Intermediate', 3, '8-12', 60,
                'Home bodyweight overhead press mimicking handstand push-up strength.',
                '1. Start in standard push-up, walk feet forward and hike hips up into an inverted V-shape.\n2. Keep legs straight or soft knees, head tucked between arms.\n3. Lower top of head diagonally forward toward the floor between hands.\n4. Press backward and up back into the V-pike.',
                'Keep hips high directly above shoulders to maximize vertical shoulder loading.',
                'Flaring elbows out; pressing backwards rather than up; letting hips drop into plank.',
                'Place a soft cushion or mat beneath head for safety.',
                'mountain'
            ),

            # BICEPS - Gym & Home
            (
                'Bicep Curl Machine', 'bicep-curl-machine', 'Biceps', 'Biceps Brachii, Brachialis', 'Gym', 'Machine', 'Arm Curl Machine',
                'Beginner', 3, '10-12', 60,
                'Fixed-path arm curl isolating the biceps without cheating or shoulder swaying.',
                '1. Adjust seat so armpits rest snugly against top of the angled arm pad.\n2. Grip handles with palms facing up.\n3. Curl handles up toward shoulders while elbows stay stationary on pad.\n4. Squeeze biceps hard at top, lower slowly over 2-3 seconds.',
                'Keep triceps glued to the pad throughout the entire movement. Do not lift elbows.',
                'Sliding elbows off the pad; lifting torso backwards off the seat.',
                'Do not let the weight stack crash at the bottom; stop just before hyper-extending elbows.',
                'hand-rock'
            ),
            (
                'Dumbbell Alternating Bicep Curl', 'dumbbell-curl', 'Biceps', 'Biceps Brachii, Brachioradialis', 'Gym', 'Dumbbells', 'Dumbbells',
                'Beginner', 3, '10-12', 60,
                'Classic arm builder allowing full supination (turning palm outward) for peak biceps peak.',
                '1. Stand tall with dumbbells at sides, palms facing inward.\n2. Curl one dumbbell up, rotating wrist so palm faces ceiling at midpoint.\n3. Squeeze bicep at shoulder level without moving elbow forward.\n4. Lower under control and alternate arms.',
                'Keep elbows tucked by ribcage. Maintain erect posture.',
                'Swinging hips or leaning back to fling weights upward; letting elbows swing forward.',
                'Select a weight you can control with zero torso momentum.',
                'dumbbell'
            ),
            (
                'Dumbbell Hammer Curl', 'hammer-curl', 'Biceps', 'Brachialis, Brachioradialis (Forearm Thickness)', 'Gym', 'Dumbbells', 'Dumbbells',
                'Beginner', 3, '10-12', 60,
                'Neutral grip curl that pushes the biceps up and builds impressive forearm thickness.',
                '1. Hold dumbbells at sides with palms facing each other (neutral grip).\n2. Keep wrists straight, curl dumbbells up toward shoulders like swinging a hammer.\n3. Squeeze brachialis at peak, lower with steady tempo.',
                'Keep palms facing inwards through the entire range of motion.',
                'Using momentum; bending wrists backward during the curl.',
                'Breathe out during the curl, breathe in during descent.',
                'hammer'
            ),
            (
                'Preacher Curl (Barbell/Dumbbell)', 'preacher-curl', 'Biceps', 'Biceps Short Head (Inner Peak)', 'Gym', 'Barbell', 'Preacher Curl Bench & EZ Bar',
                'Intermediate', 3, '8-10', 60,
                'Eliminates all momentum, isolating the lower biceps stretch and strict hypertrophy.',
                '1. Sit at preacher bench, chest against support, armpits at apex.\n2. Grasp EZ-bar with underhand grip.\n3. Curl bar up until forearms are near vertical.\n4. Lower bar with strict control until arms are almost fully extended.',
                'Maintain strict upper arm contact with pad.',
                'Dropping bar fast into hyperextended elbows (risk of biceps tendon strain); lifting off seat.',
                'Never bounce weight at the bottom. Use moderate controllable weight.',
                'pray'
            ),

            # TRICEPS - Gym & Home
            (
                'Cable Triceps Pushdown', 'cable-pushdown', 'Triceps', 'Triceps Lateral & Medial Heads', 'Gym', 'Cables', 'Cable Station (V-bar or Straight Bar / Rope)',
                'Beginner', 3, '10-12', 60,
                'The staple triceps isolation exercise delivering horseshoe triceps definition.',
                '1. Attach straight bar or rope to high cable pulley.\n2. Stand with slight forward hinge, pin elbows to your ribcage sides.\n3. Push bar/rope down until elbows are fully extended.\n4. Squeeze triceps hard for 1 second, then let bar return up to chest height while elbows stay pinned.',
                'Only the forearms should move; keep upper arms locked vertically beside your torso.',
                'Letting elbows flare forward and back like a row; using body weight to press bar down.',
                'Keep wrists neutral without breaking or rolling under heavy resistance.',
                'compress-arrows-alt'
            ),
            (
                'Triceps Extension Machine', 'triceps-extension-machine', 'Triceps', 'Triceps All Three Heads', 'Gym', 'Machine', 'Seated Triceps Machine',
                'Beginner', 3, '10-12', 60,
                'Provides stabilized guided pressing targeting triceps with minimal wrist strain.',
                '1. Sit upright, place elbows on the padded incline surface.\n2. Grasp handles, extend arms fully downward to push levers.\n3. Contract triceps at full extension.\n4. Slowly return under tension to 90 degrees.',
                'Keep elbows stable on the pads without shifting outwards.',
                'Lifting off seat; snapping elbow joints hard into hyperextension.',
                'Smooth controlled tempo on the eccentric (return) phase.',
                'cog'
            ),
            (
                'Overhead Cable Triceps Extension', 'overhead-cable-extension', 'Triceps', 'Triceps Long Head (Arm Mass)', 'Gym', 'Cables', 'Low/Mid Cable with Rope',
                'Intermediate', 3, '12-15', 60,
                'Places the triceps long head on maximum stretch for optimal muscular hypertrophy.',
                '1. Attach rope to low or mid pulley. Face away from cable station, pull rope overhead.\n2. Take a split stance for balance, lean slightly forward.\n3. With elbows pointing forward near ears, extend arms forward and overhead.\n4. Spread rope ends apart at full lockout, then return slowly behind head.',
                'Keep upper arms stationary near head; do not flare elbows wide out.',
                'Arching lower back under the overhead load; letting cable pull elbows backward uncontrollably.',
                'Brace core to keep spine stable.',
                'arrow-circle-up'
            ),
            (
                'Assisted Dips / Parallel Bar Dips', 'assisted-dips', 'Triceps', 'Triceps, Lower Chest, Front Delts', 'Gym', 'Machine', 'Assisted Dip Machine / Dip Station',
                'Intermediate', 3, '8-10', 75,
                'Heavy compound pushing movement that develops thick triceps and lower chest.',
                '1. Mount dip bars, arms straight, torso upright (upright torso targets triceps).\n2. Lower body by bending elbows until upper arms are parallel to floor (90 degrees).\n3. Drive through palms to push body back to starting position.',
                'Keep elbows tucked close to sides rather than flared out wide.',
                'Going too deep past 90 degrees if shoulders lack flexibility; swinging legs.',
                'Use knee assist platform until 10 clean bodyweight dips can be performed.',
                'sort-amount-down'
            ),

            # LEGS - Gym & Home
            (
                '45-Degree Leg Press Machine', 'leg-press-machine', 'Legs', 'Quadriceps, Glutes, Hamstrings', 'Gym', 'Machine', '45-Degree Sled Leg Press Machine',
                'Beginner', 4, '10-12', 90,
                'Premier heavy lower body mass builder without spinal loading required by back squats.',
                '1. Sit deep into seat with lower back and hips firmly pressed against pad.\n2. Place feet shoulder-width apart in middle of footplate.\n3. Disengage safety levers, lower carriage smoothly until knees bend to 90 degrees.\n4. Press sled back up through heels and midfoot. Stop just before knees lock out.',
                'Keep knees tracking in line with toes. Keep lower back glued to the backrest.',
                'Allowing hips/glutes to curl off the pad at bottom (causes severe lumbar disc compression); locking out knees violently.',
                'Always leave the safety stop brackets engaged at a height that prevents entrapment.',
                'th-large'
            ),
            (
                'Leg Extension Machine', 'leg-extension-machine', 'Legs', 'Quadriceps (Rectus Femoris Isolation)', 'Gym', 'Machine', 'Seated Leg Extension Machine',
                'Beginner', 3, '12-15', 60,
                'Isolates all 4 heads of the quadriceps for defined muscle separation and knee stability.',
                '1. Adjust back pad so knees align directly with machine pivot axis.\n2. Position shin pad just above the ankles.\n3. Extend legs upward until straight, squeezing quads hard at the top.\n4. Lower weight smoothly over 2-3 seconds.',
                'Hold peak quad contraction for 1 second on every rep. Keep hips seated.',
                'Kicking weight explosively with momentum; letting weights crash down.',
                'If you experience anterior knee discomfort, keep repetitions smooth and avoid hyper-locking.',
                'angle-double-up'
            ),
            (
                'Seated / Lying Leg Curl Machine', 'leg-curl-machine', 'Legs', 'Hamstrings (Biceps Femoris), Calves', 'Gym', 'Machine', 'Leg Curl Machine',
                'Beginner', 3, '10-12', 60,
                'Direct hamstring flexion machine critical for knee joint balance and preventing hamstring pulls.',
                '1. Adjust lever so padded roll rests against lower calves/Achilles tendon.\n2. Align knees with the machine pivot point.\n3. Curl legs down/back as far as possible toward glutes.\n4. Pause for a second at peak contraction, then resist slowly back to starting position.',
                'Keep toes pulled toward shins (dorsiflexion) to maximize hamstring tension.',
                'Lifting hips off the bench; performing fast uncontrolled kicks.',
                'Keep thighs flat against pad throughout.',
                'undo'
            ),
            (
                'Smith Machine Squats', 'smith-machine-squats', 'Legs', 'Quadriceps, Glutes, Adductors', 'Gym', 'Machine', 'Smith Machine',
                'Beginner', 4, '8-10', 90,
                'Guided squat exercise that allows variable foot placements to target quads or glutes with built-in safety hooks.',
                '1. Position bar on upper traps. Place feet shoulder-width slightly out in front of the bar.\n2. Rotate bar to unhook safeties.\n3. Squat down by sitting back and bending knees until thighs are parallel to floor.\n4. Drive through midfoot and heels to return to standing.',
                'Keep chest proud, core braced. Rotate wrists at any moment to re-engage safety hooks.',
                'Allowing knees to cave inward (valgus); rounding upper back.',
                'Always test safety stop collars at bottom height before adding weight.',
                'shield-alt'
            ),
            (
                'Standing / Seated Calf Raise Machine', 'calf-raise-machine', 'Legs', 'Gastrocnemius, Soleus (Calf Mass)', 'Gym', 'Machine', 'Calf Raise Machine',
                'Beginner', 4, '15-20', 45,
                'Builds dense calf muscle and strengthens Achilles tendons through complete range of motion.',
                '1. Place balls of feet on edge of platform, heels hanging off.\n2. Lower heels down deep into a full calf stretch (pause 1 sec).\n3. Rise up on balls of feet as high as possible into peak contraction (pause 1 sec).\n4. Repeat with slow controlled tempo.',
                'Full stretch at the bottom and hard peak squeeze at the top are essential for calf growth.',
                'Bouncing rapidly using Achilles tendon elasticity instead of muscular contraction; bending knees on standing variation.',
                'Keep core tight and spine aligned under the shoulder pads.',
                'shoe-prints'
            ),
            (
                'Hip Abduction / Adduction Machine', 'hip-abduction-machine', 'Legs', 'Gluteus Medius, Gluteus Minimus, Outer Hips', 'Gym', 'Machine', 'Hip Abductor Machine',
                'Beginner', 3, '15-20', 45,
                'Strengthens the hip stabilizers and glute medius, improving squat mechanics and hip aesthetics.',
                '1. Sit back into seat, place outer knees against the pads.\n2. Press legs outward against resistance as far as possible.\n3. Hold wide position for 1 second, then slowly bring legs together without weights touching.',
                'Stay seated tall or lean slightly forward from hips to recruit different glute fibers.',
                'Jerking weight outwards with body momentum; snapping legs together.',
                'Use moderate weight with high repetitions (15-20 reps).',
                'arrows-alt-h'
            ),

            # LEGS - Home
            (
                'Bodyweight Air Squats', 'squats', 'Legs', 'Quadriceps, Glutes, Hamstrings, Core', 'Home', 'Bodyweight', 'Floor',
                'Beginner', 3, '15-25', 60,
                'Foundational lower body movement pattern building leg strength, mobility, and knee joint resilience.',
                '1. Stand with feet shoulder-width, toes turned out 15-30 degrees.\n2. Reach arms forward for balance, initiate squat by breaking at hips and knees simultaneously.\n3. Descend until thighs are at least parallel to floor.\n4. Drive through full foot to stand up, squeezing glutes at top.',
                'Keep chest upright and weight distributed across whole foot (tripod foot). Keep knees over toes.',
                'Heels rising off ground; knees collapsing inward; rounding lower back into "butt wink".',
                'Hold a chair or doorframe for balance if learning proper depth.',
                'male'
            ),
            (
                'Walking / Reverse Lunges', 'lunges', 'Legs', 'Quadriceps, Glutes, Hamstrings, Balance', 'Home', 'Bodyweight', 'Floor',
                'Beginner', 3, '12-16 total', 60,
                'Unilateral leg movement correcting muscle imbalances and improving hip stability.',
                '1. Stand tall with feet together.\n2. Step one foot backwards and lower hips until both knees form 90-degree angles.\n3. Keep front knee behind front toe, hover back knee 1 inch off floor.\n4. Push through front heel to return to start and switch legs.',
                'Maintain an upright torso and engaged core. Step wide enough to maintain 90-degree knee joints.',
                'Slamming back knee into floor; front knee tracking wildly inward.',
                'Perform next to a wall if balance is difficult.',
                'walking'
            ),
            (
                'Glute Bridges', 'glute-bridges', 'Legs', 'Gluteus Maximus, Hamstrings, Core', 'Home', 'Bodyweight', 'Floor / Mat',
                'Beginner', 3, '15-20', 45,
                'Direct glute activation exercise relieving lower back tightness and strengthening hips.',
                '1. Lie on back with knees bent and feet flat on floor hip-width apart, arms by sides.\n2. Drive through heels to raise hips toward ceiling until thighs and torso align.\n3. Squeeze glutes intensely at top for 2 seconds.\n4. Lower hips with control until hovering just above floor.',
                'Focus on tucking pelvis and firing glutes without overarching lower back.',
                'Pushing with lower back instead of glutes; feet placed too far from body.',
                'Keep feet flat and knees steady without falling inward.',
                'wave-square'
            ),

            # ABS - Gym & Home
            (
                'Ab Crunch Machine', 'ab-crunch-machine', 'Abs', 'Rectus Abdominis (Six-Pack Core)', 'Gym', 'Machine', 'Seated Abdominal Crunch Machine',
                'Beginner', 3, '12-15', 60,
                'Weighted core machine allowing progressive overload for deep abdominal muscle thickness.',
                '1. Sit in machine with back against pad, adjust chest or shoulder pads.\n2. Grasp handles above or beside shoulders, secure feet under foot rollers.\n3. Contract abdominals to crunch torso forward, curling ribcage toward pelvis.\n4. Pause at peak contraction, then slowly return under control.',
                'Focus on flexing the spine with abdominal contraction rather than pulling with arms or hip flexors.',
                'Pulling violently with arms and shoulders; arching violently at top.',
                'Breathe out forcefully as you crunch, breathe in as you open.',
                'crosshairs'
            ),
            (
                'Cable Kneeling Crunch', 'cable-crunch', 'Abs', 'Rectus Abdominis, Obliques', 'Gym', 'Cables', 'Cable Pulley with Rope',
                'Intermediate', 3, '12-15', 60,
                'High-tension abdominal exercise that protects the lower back while providing heavy core loading.',
                '1. Attach rope to high pulley, kneel on floor a few feet from stack.\n2. Hold rope ends by ears/jaw.\n3. Keeping hips fixed in place, round spine and curl elbows down toward knees/thighs.\n4. Squeeze abs hard at bottom, slowly return.',
                'Do not sit back on your heels during the crunch; hips must stay high and motionless.',
                'Turning it into a hip hinge by sitting down; pulling with arms instead of spinal flexion.',
                'Use a foam pad or mat beneath knees for comfort.',
                'compress'
            ),
            (
                'Hanging Leg / Knee Raises', 'hanging-leg-raises', 'Abs', 'Lower Rectus Abdominis, Hip Flexors, Grip Strength', 'Gym', 'Bodyweight', 'Pull-up Bar / Captain\'s Chair',
                'Intermediate', 3, '10-15', 60,
                'Exceptional lower core exercise that decompress the spine while building incredible abdominal strength.',
                '1. Hang from pull-up bar with overhand grip (or mount Captain\'s chair on forearms).\n2. Brace core, roll pelvis upwards, and raise knees/legs toward chest.\n3. Pause for a second at top, then lower legs with complete control without swinging.',
                'The key is posterior pelvic tilt: curl the pelvis toward your face rather than just lifting thighs with hips.',
                'Swinging body like a pendulum; arching back wildly at the bottom.',
                'Start with bent-knee raises before progressing to straight legs.',
                'grip-vertical'
            ),
            (
                'Core Plank (Isometric Hold)', 'plank', 'Abs', 'Transverse Abdominis, Rectus Abdominis, Lower Back, Glutes', 'Home', 'Bodyweight', 'Floor / Mat',
                'Beginner', 3, '45-60 sec', 45,
                'Premier anti-extension core stability exercise training the abdominal wall to brace and protect the spine.',
                '1. Rest on forearms and balls of feet, elbows directly under shoulders.\n2. Maintain a straight body line from head to heels.\n3. Pull belly button toward spine, squeeze glutes, and push floor away with shoulder blades.\n4. Hold position while breathing steadily.',
                'Imagine pulling your elbows and toes toward each other to maximize abdominal tension.',
                'Hips sagging down (strains lumbar spine); pike hips high into the air; holding breath.',
                'If lower back aches, drop knees briefly to reset correct pelvic alignment.',
                'minus'
            ),
            (
                'Abdominal Crunches', 'crunches', 'Abs', 'Upper Rectus Abdominis', 'Home', 'Bodyweight', 'Floor / Mat',
                'Beginner', 3, '15-25', 45,
                'Safe spinal flexion targeting the upper abdominal region.',
                '1. Lie on back, knees bent, feet flat on floor. Place hands lightly behind ears (do not pull neck).\n2. Exhale and lift shoulder blades 2-3 inches off the ground, curling ribs toward hips.\n3. Hold peak contraction for 1 second.\n4. Lower shoulder blades back down with control.',
                'Keep chin off chest (imagine holding an apple under chin).',
                'Yanking neck with hands; using momentum to bounce up and down.',
                'Maintain eyes focused diagonally up toward the ceiling.',
                'circle'
            ),

            # FULL BODY - Home
            (
                'Burpees (Full Body Calorie Burn)', 'burpees', 'Full Body', 'Pectorals, Quads, Deltoids, Core, Cardio', 'Home', 'Bodyweight', 'Floor',
                'Intermediate', 3, '10-15', 60,
                'High-intensity metabolic conditioner that torches calories, elevates heart rate, and builds total body endurance.',
                '1. Stand with feet shoulder-width.\n2. Squat down and place hands on floor.\n3. Kick feet back into a push-up position, lower chest to floor.\n4. Press up, jump feet back to hands, and leap vertically with arms overhead.',
                'Land softly on balls of feet. Move with an even rhythmic cadence.',
                'Letting hips sag down during the push-up; landing heavily on stiff joints.',
                'Step back instead of jumping back if low-impact option is needed for joints.',
                'bolt'
            )
        ]
        cursor.executemany('''
            INSERT INTO exercises (name, slug, muscle_group, secondary_muscles, location, equipment, machine_name,
                                  difficulty, recommended_sets, recommended_reps, rest_seconds, technique,
                                  step_by_step, posture_tips, common_mistakes, safety_precautions, icon_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_exercises)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
