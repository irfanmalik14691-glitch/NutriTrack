import os
import re
from flask import Blueprint, render_template, request, session, jsonify
from routes.auth_routes import login_required
from models import ProfileModel

assistant_bp = Blueprint('assistant', __name__)

def get_rule_based_response(prompt, profile):
    """
    Intelligent fitness & nutrition expert system that produces in-depth,
    practical advice when an external AI API key is not configured.
    """
    text = prompt.lower()
    name = profile['name'] if profile else 'Athlete'
    goal = profile['fitness_goal'] if profile else 'Muscle Building'
    weight = profile['current_weight'] if profile else 70

    # 1. Weight Gain / Bulking
    if any(k in text for k in ['gain weight', 'bulk', 'gain muscle', 'skinny', 'hardgainer', 'surplus']):
        cal_surplus = round((profile['tdee'] or 2200) + 400) if profile else 2600
        protein_need = round(weight * 1.8)
        return f"""### 🚀 Comprehensive Weight & Muscle Gain Strategy for {name}

To gain lean body weight without excessive fat accumulation:

1. **Energy Surplus**: You need to consume approximately **{cal_surplus} kcal/day** (a controlled 350–500 kcal surplus above your TDEE).
2. **Protein Target**: Consume **{protein_need}g of protein daily** (1.8g to 2.0g per kg of bodyweight).
3. **Calorie-Dense Indian Foods**:
   - **Morning Shake**: Oats (60g), whole milk (300ml), peanut butter (2 tbsp), 1 banana, and 1 scoop whey or 2 tbsp sattu powder (~750 kcal).
   - **Protein Staples**: Paneer (150g), whole eggs (3-4/day), boiled soya chunks (50g raw = 26g protein), roasted peanuts, almonds, and Greek yogurt / curd.
   - **Complex Carbs**: Brown or white basmati rice, rotis with ghee, boiled sweet potatoes, and bananas.
4. **Training Priority**:
   - Focus on compound movements: **Squats, Bench Press, Lat Pulldowns/Rows, and Overhead Presses**.
   - Train 4–5 days per week using **3–4 sets of 8–12 reps** with progressive overload (adding 1-2kg or 1 rep each week).
5. **Recovery**: Ensure 7.5 to 8.5 hours of quality sleep to maximize natural growth hormone and testosterone release."""

    # 2. Fat Loss / Cutting
    elif any(k in text for k in ['lose fat', 'cut', 'belly fat', 'weight loss', 'burn fat', 'calorie deficit', 'lean out']):
        cal_deficit = round((profile['tdee'] or 2200) - 500) if profile else 1800
        protein_need = round(weight * 2.0)
        return f"""### 🔥 Safe, Sustainable Fat Loss Blueprint for {name}

To shed body fat while strictly preserving your lean muscle tissue:

1. **Calculated Deficit**: Aim for **{cal_deficit} kcal/day** (a moderate, safe 400–500 kcal deficit). Never drop below 1200 kcal.
2. **Elevated Protein ({protein_need}g/day)**:
   - High protein prevents muscle catabolism during a deficit and has the highest thermic effect of food (TEF).
   - Opt for egg whites, chicken breast, low-fat paneer, boiled chana, sprouted moong salad, and whey protein.
3. **Volume Eating Strategy**:
   - Fill half your plate with raw cucumber, tomatoes, spinach, and vegetable sabzi (high fiber, low calorie density).
   - Drink 500ml water 15 minutes before every meal to boost satiety.
4. **Exercise Combination**:
   - **Weight Training (3-4 days/week)**: Heavy resistance training signals your body to hold onto muscle.
   - **Cardio / NEAT**: Walk 8,000–10,000 steps daily (low fatigue, high fat oxidation) + 15 mins of incline treadmill walking or jump rope post-workout.
5. **Realistic Timeline**: Aim for 0.4 to 0.7 kg of fat loss per week. Rapid weight drops usually represent water and lost muscle mass."""

    # 3. Gym Machines
    elif any(k in text for k in ['machine', 'gym machine', 'pec deck', 'lat pulldown', 'cable', 'smith machine', 'leg press']):
        return """### 🏋️ Essential Gym Machines & Target Muscle Guide

Here is how to optimize the top machines in your gym:

- **Chest Press Machine**: Targets Pectoralis Major. Set seat so handles align with mid-chest. Retract shoulder blades and press without locking elbows (3 sets x 10-12 reps).
- **Pec Deck / Butterfly**: Direct chest isolation. Keep a soft bend in elbows, imagine hugging a tree, and squeeze your pecs together for 1 sec at peak contraction (3 sets x 12-15 reps).
- **Lat Pulldown Machine**: Builds back width (V-taper). Pull bar to upper collarbone with elbows driving down and back; avoid leaning back more than 15 degrees (4 sets x 8-10 reps).
- **Seated Cable Row**: Mid-back & rhomboid thickness. Maintain upright posture, drive elbows past torso, and squeeze scapulae together (3 sets x 10-12 reps).
- **45-Degree Leg Press**: Heavy quad and glute builder. Place feet shoulder-width, lower carriage until knees reach 90 degrees, and drive through heels. *Never lock knees at the top!* (4 sets x 10-12 reps).
- **Leg Curl Machine**: Targets hamstrings. Pull heels all the way to glutes with controlled eccentric return (3 sets x 10-12 reps).
- **Cable Triceps Pushdown**: Horseshoe triceps definition. Pin elbows strictly against your ribcage; only your forearms should pivot (3 sets x 12-15 reps)."""

    # 4. Home Workouts
    elif any(k in text for k in ['home workout', 'no gym', 'bodyweight', 'pushup', 'squat', 'calisthenics', 'at home']):
        return """### 🏠 High-Impact Full-Body Home Workout Routine

No equipment required. Perform this routine as a circuit or straight sets:

1. **Chest & Triceps - Standard Push-ups**: 3 sets x 12–20 reps (elevate hands on sofa for beginner regression; elevate feet on chair for advanced overload).
2. **Back & Biceps - Doorway Pull-ups or Inverted Towel Rows**: 3 sets x 8–12 reps.
3. **Shoulders - Pike Push-ups**: 3 sets x 8–12 reps (hips hiked high into an inverted V to load the anterior and lateral deltoids).
4. **Quads & Glutes - Bodyweight Squats & Walking Lunges**: 4 sets x 15–20 reps (focus on full 90-degree knee bend depth).
5. **Hamstrings & Hips - Glute Bridges**: 3 sets x 20 reps (pause 2 seconds at the top contraction).
6. **Core - Forearm Plank**: 3 sets x 45–60 seconds hold (brace core and squeeze glutes like an iron board).

*Frequency*: Perform 3 to 4 days per week with 1 day of rest between sessions."""

    # 5. Protein & Supplements
    elif any(k in text for k in ['whey', 'protein powder', 'creatine', 'supplement', 'bcaa', 'multivitamin']):
        return """### 💊 Evidence-Based Supplementation Guide

1. **Creatine Monohydrate (5g/day)**:
   - The most scientifically validated performance supplement.
   - Increases intracellular phosphocreatine stores for greater strength, power output, and muscular fullness. Take 5g daily at any consistent time with water.
2. **Whey Protein**:
   - Convenient, fast-digesting high-quality protein with a full essential amino acid profile (rich in leucine).
   - Ideal post-workout or added to morning oats if whole food protein is difficult to meet.
3. **Caffeine / Pre-Workout**:
   - 100–200mg (or a strong cup of black coffee) 30 minutes before training increases central nervous system alertness and power output.
4. **Micronutrients**:
   - **Vitamin D3 (2000-5000 IU)**: Essential for bone density, immune function, and natural testosterone synthesis.
   - **Omega-3 Fish Oil**: Reduces joint inflammation and aids cardiovascular recovery."""

    # 6. Routine / Split / Schedule
    elif any(k in text for k in ['routine', 'split', 'workout plan', 'schedule', 'program', 'days']):
        return """### 📅 Recommended Workout Splits by Frequency

- **3 Days / Week -> Full Body Workout (Mon / Wed / Fri)**:
  - Best for beginners and busy schedules. Hit every major muscle group 3 times per week with high efficiency.
- **4 Days / Week -> Upper / Lower Split (Mon, Tue / Thu, Fri)**:
  - Gold standard for progressive overload and optimal 48-72 hour muscle protein synthesis recovery windows.
- **5 Days / Week -> Push / Pull / Legs / Upper / Lower**:
  - Superb hypertrophy split for intermediate trainees looking for specialized volume.
- **6 Days / Week -> Push / Pull / Legs (x2)**:
  - High frequency elite bodybuilding split. Requires strict nutrition, high caloric intake, and 8+ hours of sleep.

*Head over to the **Workout Planner** page in the left sidebar to generate your customized calendar!*"""

    # Generic comprehensive answer
    else:
        return f"""### 💡 NutriTrack Fitness Intelligence

Hello **{name}**! Based on your active goal of **{goal}**:

- **Energy Balance**: Your calculated daily metabolic target is **{profile['daily_calorie_target'] or 2200} kcal** with **{profile['protein_target'] or 140}g Protein**, **{profile['carbs_target'] or 250}g Carbs**, and **{profile['fat_target'] or 60}g Fats**.
- **Hydration**: Maintain at least **{profile['water_target'] or 2500} ml** of clean water daily to optimize cellular nutrient transport and workout endurance.
- **Workout Guidance**: Whether you train at home or in the gym, focus on progressive resistance, strict form, and 60–90 seconds rest between working sets.

*You can ask me specific questions such as:*
- "How do I gain weight with an Indian vegetarian diet?"
- "What is the best way to lose stubborn belly fat?"
- "How do I perform Lat Pulldowns correctly on the machine?"
- "Give me a home chest and arm workout without weights."
- "Should I take creatine monohydrate?"""


@assistant_bp.route('/assistant')
@login_required
def assistant():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)
    return render_template('assistant.html', profile=profile)


@assistant_bp.route('/api/assistant/chat', methods=['POST'])
@login_required
def api_chat():
    user_id = session['user_id']
    profile = ProfileModel.get_by_user_id(user_id)

    data = request.get_json() or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'reply': 'Please type a question regarding nutrition, weight management, or fitness training.'})

    # Check if Gemini or OpenAI API Key is present in environment
    gemini_key = os.environ.get('GEMINI_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')

    # If external AI key is available, call it; otherwise use the intelligent rule-based expert engine
    if gemini_key:
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            sys_info = f"User Profile: Name={profile['name']}, Goal={profile['fitness_goal']}, Weight={profile['current_weight']}kg, Height={profile['height']}cm, Daily Calories={profile['daily_calorie_target']}kcal, Protein={profile['protein_target']}g."
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"You are NutriTrack AI, a professional sports nutritionist and CSCS certified personal trainer. {sys_info}. Answer the user accurately, motivatingly, and with clear actionable fitness and diet steps.\n\nUser Question: {message}"}
                        ]
                    }
                ]
            }
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                result_json = res.json()
                reply_text = result_json['candidates'][0]['content']['parts'][0]['text']
                return jsonify({'reply': reply_text})
        except Exception:
            pass # fallback to rule engine smoothly

    # Default robust rule-based engine
    reply = get_rule_based_response(message, profile)
    return jsonify({'reply': reply})
