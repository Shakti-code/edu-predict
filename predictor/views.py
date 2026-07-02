from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import StudentPrediction
import pandas as pd
import joblib
import json
import os

# Load model and metrics once on server startup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'model.pkl')
METRICS_PATH = os.path.join(BASE_DIR, 'model', 'model_metrics.json')

model = None
metrics = None

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")

if os.path.exists(METRICS_PATH):
    try:
        with open(METRICS_PATH, 'r') as f:
            metrics = json.load(f)
    except Exception as e:
        print(f"Error loading metrics: {e}")

def get_grade_class(score):
    if score >= 85:
        return 'Excellent', 'grade-excellent'
    elif score >= 70:
        return 'Good', 'grade-good'
    elif score >= 50:
        return 'Pass', 'grade-pass'
    else:
        return 'Fail', 'grade-fail'

def generate_recommendations(input_data, current_prediction):
    recs = []
    
    # What-if study hours recommendation
    current_study = float(input_data['Study_Hours'].iloc[0])
    if current_prediction < 95 and current_study < 10:
        # Let's find how many study hours would achieve a higher grade
        improved_study = current_study
        predicted_score = current_prediction
        target_score = min(95.0, current_prediction + 5.0)
        
        # Binary search or simple step loop to find the required study hours
        temp_data = input_data.copy()
        for hours in [x * 0.5 for x in range(int(current_study * 2) + 1, 21)]:
            temp_data['Study_Hours'] = hours
            try:
                pred = model.predict(temp_data)[0]
                if pred > current_prediction + 2.0:  # significant improvement
                    improved_study = hours
                    predicted_score = pred
                    break
            except Exception:
                break
                
        if improved_study > current_study:
            recs.append({
                'category': 'Study Hours',
                'icon': 'book-open',
                'current': f"{current_study} hrs/day",
                'target': f"{improved_study} hrs/day",
                'benefit': f"Increase predicted score from {current_prediction:.1f}% to {predicted_score:.1f}%"
            })
            
    # What-if attendance recommendation
    current_attendance = float(input_data['Attendance'].iloc[0])
    if current_prediction < 95 and current_attendance < 95:
        target_attendance = min(100.0, current_attendance + 10.0)
        temp_data = input_data.copy()
        temp_data['Attendance'] = target_attendance
        try:
            pred = model.predict(temp_data)[0]
            if pred > current_prediction + 1.0:
                recs.append({
                    'category': 'Attendance',
                    'icon': 'user-check',
                    'current': f"{current_attendance:.1f}%",
                    'target': f"{target_attendance:.1f}%",
                    'benefit': f"Increase predicted score by {pred - current_prediction:.1f}%"
                })
        except Exception:
            pass

    # Sleep hours check
    current_sleep = float(input_data['Sleep_Hours'].iloc[0])
    if current_sleep < 7.0:
        recs.append({
            'category': 'Sleep Hygiene',
            'icon': 'moon',
            'current': f"{current_sleep} hrs/night",
            'target': "7.5 - 8.5 hrs/night",
            'benefit': "Better cognitive retention, focus, and reduced exam stress."
        })

    # Parental Support check
    parental = input_data['Parental_Support'].iloc[0]
    if parental == 'Low':
        recs.append({
            'category': 'Support System',
            'icon': 'users',
            'current': 'Low Support',
            'target': 'Active Mentorship',
            'benefit': "Engage with academic counselors or peer study groups to boost performance."
        })

    return recs

@login_required
def index(request):
    return render(request, 'predictor/index.html')

@login_required
def predict(request):
    global model
    if not model:
        # Try reloading model if it wasn't loaded
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
        else:
            return render(request, 'predictor/error.html', {'error': 'ML Model not trained. Please run training script.'})
            
    if request.method == 'POST':
        try:
            # Extract inputs from POST
            study_hours = float(request.POST.get('study_hours', 5.0))
            attendance = float(request.POST.get('attendance', 80.0))
            sleep_hours = float(request.POST.get('sleep_hours', 7.0))
            parental_support = request.POST.get('parental_support', 'Medium')
            extracurricular = request.POST.get('extracurricular', 'No')
            internet_access = request.POST.get('internet_access', 'Yes')
            previous_grade = float(request.POST.get('previous_grade', 70.0))
            
            # Create a dataframe matching structure expected by model preprocessor
            input_dict = {
                'Study_Hours': [study_hours],
                'Attendance': [attendance],
                'Sleep_Hours': [sleep_hours],
                'Parental_Support': [parental_support],
                'Extracurricular': [extracurricular],
                'Internet_Access': [internet_access],
                'Previous_Grade': [previous_grade]
            }
            
            input_df = pd.DataFrame(input_dict)
            
            # Run prediction
            predicted_score = float(model.predict(input_df)[0])
            predicted_score = min(100.0, max(0.0, predicted_score))
            
            # Save to database
            StudentPrediction.objects.create(
                user=request.user,
                study_hours=study_hours,
                attendance=attendance,
                sleep_hours=sleep_hours,
                parental_support=parental_support,
                extracurricular=extracurricular,
                internet_access=internet_access,
                previous_grade=previous_grade,
                predicted_score=round(predicted_score, 1)
            )
            
            grade_class, grade_style = get_grade_class(predicted_score)
            recommendations = generate_recommendations(input_df, predicted_score)
            
            context = {
                'study_hours': study_hours,
                'attendance': attendance,
                'sleep_hours': sleep_hours,
                'parental_support': parental_support,
                'extracurricular': extracurricular,
                'internet_access': internet_access,
                'previous_grade': previous_grade,
                'predicted_score': round(predicted_score, 1),
                'grade_class': grade_class,
                'grade_style': grade_style,
                'recommendations': recommendations
            }
            
            return render(request, 'predictor/results.html', context)
        except Exception as e:
            return render(request, 'predictor/index.html', {'error': f"Prediction error: {str(e)}"})
            
    return render(request, 'predictor/index.html')

@login_required
def dashboard(request):
    global metrics
    if not metrics:
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, 'r') as f:
                metrics = json.load(f)
        else:
            metrics = {
                'r2_score': 'N/A',
                'mae': 'N/A',
                'rmse': 'N/A',
                'feature_importance': [],
                'dataset_size': 'N/A'
            }
            
    recent_predictions = StudentPrediction.objects.filter(user=request.user)[:10]
            
    return render(request, 'predictor/dashboard.html', {
        'metrics': metrics,
        'recent_predictions': recent_predictions
    })
