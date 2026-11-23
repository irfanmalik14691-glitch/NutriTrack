# ⚡ NutriTrack 3D — Futuristic Diet, Nutrition & Fitness Guidance Platform

A complete, production-grade, cinematic 3D web platform built with **Python Flask**, **SQLite**, **Three.js**, **Chart.js**, and modern **CSS3 Glassmorphism**. Designed as a high-performance fitness startup platform and an exemplary BTech CSE capstone portfolio project.

---

## 🌟 Key Feature Highlights

### 1. 🧬 Interactive 3D Human Muscle Anatomy Explorer
- **Anatomically Structured 3D Muscular Model**: Built with Three.js rendering real muscular geometry on a futuristic rotating pedestal with cinematic dark gym lighting.
- **Mouse Raycasting Selection**: Hover over muscle groups to trigger an emerald neon glow and floating anatomical HUD tooltip.
- **Selectable Groups**:
  - **Front**: Chest (Pectoralis Major/Minor), Front Deltoids, Biceps, Forearms, 6-Pack Abs, Obliques, Quadriceps, Calves.
  - **Back**: Trapezius, Latissimus Dorsi (Lats), Rear Deltoids, Triceps, Lower Back (Erector Spinae), Glutes, Hamstrings, Calves.
- **Camera Controls**: OrbitControls with drag-to-rotate, pinch/scroll zoom, pan, and one-click camera buttons for **Front View**, **Back View**, and **Reset View**.
- **Dynamic Biomechanical Prescription Panel**: Automatically queries the database via AJAX to display:
  - **Gym Machines & Weights**: Machine name, setup instructions, posture alignment, recommended sets & reps, rest times, common mistakes, and safety precautions.
  - **Home Calisthenics**: Zero-equipment bodyweight progressions, execution steps, and common error corrections.

### 2. 🥗 Smart Indian Diet & Food Tracker
- **Pre-populated Indian & Athletic Staples**: Roti (Whole Wheat Chapati), Basmati Rice, Brown Rice, Dal (Moong/Toor), Fresh Paneer, Low Fat Paneer, Cow Milk, Toned Milk, Curd / Dahi, Greek Yogurt, Whole Boiled Eggs, Egg Whites, Chicken Breast, Chicken Curry, Banana, Apple, Rolled Oats, Peanut Butter, Raw Almonds, Walnuts, Soya Chunks (Nutrela), Poha, Idli, Dosa, Rajma, Chole Masala, Sprouted Moong Salad, Fish, Whey Protein Isolate, Sattu, Sweet Potato, Mixed Vegetables, and Green Salad.
- **Dynamic Gram Portion Calculator**: Type any portion in grams (e.g., `150g` Paneer) to instantly compute calories, protein, carbs, and fats in real-time.
- **Meal Classification**: Breakfast, Lunch, Dinner, and Snacks with individual meal sub-totals.
- **Custom Food Creator**: Easily add personal recipes, local dishes, or custom protein powders.

### 3. 🔬 Scientific Nutrition Calculator (Mifflin-St Jeor)
- **Automatic Metric Calculations**:
  - **BMI**: $\text{weight (kg)} / (\text{height (m)})^2$ with clinical categorization.
  - **BMR (Mifflin-St Jeor)**:
    - *Men*: $10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age} + 5$
    - *Women*: $10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age} - 161$
  - **TDEE**: Adjusted for physical activity factor (Sedentary $1.2$, Light $1.375$, Moderate $1.55$, Active $1.725$, Very Active $1.9$).
  - **Daily Calorie Targets**:
    - *Weight Loss*: TDEE $- 500\text{ kcal}$ (safe healthy deficit $\approx 0.5\text{ kg/week}$)
    - *Weight Gain*: TDEE $+ 500\text{ kcal}$ (clean surplus $\approx 0.5\text{ kg/week}$)
    - *Muscle Building*: TDEE $+ 250\text{ kcal}$ (lean hypertrophy surplus)
    - *Maintenance*: TDEE (energy balance)
  - **Macronutrient Split**:
    - *Protein*: $1.8\text{g}$ to $2.0\text{g}$ per kg bodyweight.
    - *Fat*: $25\%$ of daily calories divided by $9\text{ kcal/g}$.
    - *Carbohydrates*: Remainder of caloric budget divided by $4\text{ kcal/g}$.
  - **Hydration Target**: Baseline estimated as $\text{Body Weight (kg)} \times 35\text{ ml}$.

### 4. 🎯 Fitness Goals Master Guide (Weight Gain & Fat Loss)
- **Weight Gain Blueprint**: Clean caloric surplus guidelines, affordable Indian mass-building meals (Desi Power Shake, Paneer Bhurji with Rotis, Soya Chunks & Egg Pulao, Sattu), progressive overload rules, and recovery principles.
- **Safe Fat Loss Blueprint**: Moderate deficit strategy, muscle-sparing high protein intake ($1.8\text{g}-2.0\text{g/kg}$), high-satiety Indian meals (Sprouted Moong Salad, Egg White Scrambles, Grilled Paneer/Chicken, Cucumber Raita), and NEAT cardio steps.
- **Maintenance & Body Recomposition**: Energy balance and body re-partitioning protocols.

### 5. 🏋️ Gym Machines & Home Workouts Guides
- **Gym Training Section**: Dedicated guides for Chest Press Machine, Pec Deck, Lat Pulldown, Seated Cable Row, T-Bar Row, Assisted Pull-up, Shoulder Press Machine, Lateral Raise Machine, Cable Triceps Pushdown, 45-Degree Leg Press, Leg Extension, Leg Curl, Smith Machine Squats, Calf Raise, and Ab Crunch Machine.
- **Home Calisthenics Section**: Bodyweight progressions for Push-ups, Incline Push-ups, Squats, Lunges, Planks, Crunches, Glute Bridges, Pike Push-ups, Burpees, and Pull-ups.

### 6. 📅 Algorithmic Workout Planner
- Generates 3-Day Full Body, 4-Day Upper/Lower, 5-Day PPLUL, or 6-Day PPL $\times 2$ splits customized to user experience, workout location (Home vs Gym), and available days.
- Full weekly calendar view (Monday through Sunday) with sets, reps, and rest intervals.

### 7. 📝 Sets & Reps Gym Tracker
- Log session sets in real time: exercise, set number, weight in kg, completed reps.
- Automated Personal Records (PRs) detection tracking max weight lifted per movement.
- Full workout session history saved in SQLite.

### 8. 💧 Smart Hydration Tracker
- Cylindrical animated water container with glowing liquid level matching daily hydration progress.
- Quick logging buttons (+250ml, +500ml, +750ml, +1000ml) and custom inputs.
- 7-day hydration history with target achievement badges.

### 9. 📊 Analytics, Reports & Permanent CSV Data Export
- Weekly Calorie Intake bar chart and Macro Breakdown doughnut chart powered by **Chart.js**.
- 14-day Calorie & Protein trajectory chart.
- Permanent CSV Data Exports:
  - `nutritrack_food_logs.csv`
  - `nutritrack_weight_history.csv`
  - `nutritrack_workouts.csv`

### 10. 🤖 AI Athletic & Nutrition Assistant
- Embedded conversational fitness assistant capable of answering questions on nutrition, Indian diets, gym machines, bulking, cutting, creatine, and workout routines.
- Supports external Gemini or OpenAI API keys if configured, and comes equipped with an extensive, highly intelligent rule-based expert engine fallback.

---

## 💻 Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11+, Flask 3.1, Werkzeug (Password Hashing & Sessions) |
| **Database** | SQLite3 (Normalized tables with foreign keys and cascade deletes) |
| **3D Graphics** | Three.js (r128), OrbitControls, Raycasting, Custom Mesh Sculpting |
| **Data Visualizations** | Chart.js |
| **Animations** | GSAP 3.12 (GreenSock Animation Platform) |
| **Styling** | Vanilla CSS3 (Glassmorphism, CSS Grid, Custom Scrollbars, Neon Emerald Accents) |
| **Typography & Icons** | Google Fonts (Outfit, Plus Jakarta Sans, JetBrains Mono), FontAwesome 6 |

---

## 🚀 How to Run in Visual Studio Code (VS Code)

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** &rarr; **Open Folder...**
3. Select `c:\Users\irfan\OneDrive\Documents\diet management`.

### Step 2: Open Terminal in VS Code
- Open the built-in terminal by pressing ``Ctrl + ` `` (Backtick) or going to **Terminal** &rarr; **New Terminal**.

### Step 3: Verify Python Installation
In the terminal, run:
```powershell
python --version
```
*(Python 3.11+ is installed on your system at `C:\Users\irfan\AppData\Local\Programs\Python\Python311`).*

### Step 4: Install Dependencies (If not already installed)
```powershell
pip install -r requirements.txt
```

### Step 5: Start the Website Server
Run either command:
```powershell
python run.py
```
*or*
```powershell
cd diet_tracker
python app.py
```

### Step 6: Open the Website in Your Browser
Open your browser (Chrome, Edge, Brave, etc.) and navigate to:
```
http://127.0.0.1:5000
```

---

## 📂 Project Directory Structure

```
diet management/
│
├── run.py                          # Top-level application entrypoint
├── requirements.txt                # Python package dependencies
├── README.md                       # Complete documentation & guide
│
└── diet_tracker/
    ├── app.py                      # Flask factory, blueprint registration & error handlers
    ├── database.py                 # SQLite schema creation & seed database initialization
    ├── models.py                   # Data models, metabolic math & query engines
    ├── requirements.txt            # Dependency list
    │
    ├── instance/
    │   └── diet_tracker.db         # Persistent SQLite database file
    │
    ├── routes/
    │   ├── __init__.py
    │   ├── auth_routes.py          # Register, Login, Logout, Profile update
    │   ├── main_routes.py          # Landing page & Dashboard controller
    │   ├── diet_routes.py          # Food tracker, Water tracker, Meal planner
    │   ├── fitness_routes.py       # 3D Anatomy, Fitness goals, Home/Gym workouts, Planner
    │   ├── progress_routes.py      # Weight tracking, Reports, CSV Exports
    │   └── assistant_routes.py     # AI Fitness Assistant & Chat API
    │
    ├── static/
    │   ├── css/
    │   │   └── style.css           # Premium dark & neon green glassmorphism design system
    │   └── js/
    │       ├── main.js             # Mobile drawer, auto-dismiss alerts, live grams calculator
    │       ├── three_hero.js       # 3D interactive floating dumbbell & particle hero
    │       ├── muscle_anatomy.js   # 3D Human Muscular Anatomy raycasting & exercise HUD
    │       └── assistant.js        # AI Chatbot interactive interface
    │
    └── templates/
        ├── base.html               # Master layout with sidebar navigation & top bar
        ├── landing.html            # Cinematic full-screen 3D hero landing page
        ├── login.html              # Secure glassmorphism sign-in
        ├── register.html           # Account creation with instant metabolic onboarding
        ├── dashboard.html          # Fitness Command Center with 3D cards & Chart.js
        ├── food_tracker.html       # Smart Indian diet diary & grams portion calculator
        ├── meal_planner.html       # Reusable meal templates & 1-click diary logger
        ├── water_tracker.html      # Animated hydration bottle & quick ml logger
        ├── muscle_anatomy.html     # Interactive 3D Human Muscle Anatomy Explorer
        ├── fitness_goals.html      # Weight Gain, Fat Loss, and Maintenance guides
        ├── home_workouts.html      # Calisthenics & bodyweight exercise directory
        ├── gym_workouts.html       # Gym machine specifications, posture & safety guide
        ├── exercise_library.html   # Searchable 40+ exercise database with multi-filters
        ├── workout_planner.html    # 3, 4, 5, 6-day split generator & weekly calendar
        ├── workout_tracker.html    # Sets & Reps Gym Logger with Personal Records (PRs)
        ├── progress.html           # Weight trajectory charts & 14-day calorie trends
        ├── reports.html            # 7-day intake averages & CSV data export center
        ├── assistant.html          # AI Fitness Assistant live chat
        └── profile.html            # Biometric settings, BMR/TDEE math & disclaimer
```

---

## 🛡️ Security & Architecture Details
- **Password Hashing**: Uses Werkzeug's PBKDF2 with SHA-256 password hashing.
- **Session Security**: Server-side session authentication with `login_required` decorators.
- **Relational Integrity**: Foreign keys enabled (`PRAGMA foreign_keys = ON`) with cascading deletes.
- **SQL Injection Prevention**: $100\%$ parameterized SQL queries.
- **Zero Dummy Data**: Real dynamic calculations bound directly to SQLite records.
