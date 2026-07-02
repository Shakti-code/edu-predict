import pandas as pd
import numpy as np
import os

def generate_student_data(num_samples=1000, seed=42):
    np.random.seed(seed)
    
    # Generate features
    study_hours = np.random.uniform(1.0, 10.0, num_samples)
    attendance = np.random.uniform(50.0, 100.0, num_samples)
    sleep_hours = np.random.uniform(4.0, 10.0, num_samples)
    
    parental_support_choices = ['Low', 'Medium', 'High']
    parental_support = np.random.choice(parental_support_choices, num_samples, p=[0.2, 0.5, 0.3])
    
    extracurricular = np.random.choice(['Yes', 'No'], num_samples, p=[0.4, 0.6])
    internet_access = np.random.choice(['Yes', 'No'], num_samples, p=[0.8, 0.2])
    
    # Previous grade: correlated with study hours and attendance
    base_prev = 45 + (study_hours * 3.5) + ((attendance - 50) * 0.4)
    previous_grade = base_prev + np.random.normal(0, 5, num_samples)
    previous_grade = np.clip(previous_grade, 30, 100)
    
    # Map parental support to numbers for formula
    parental_support_map = {'Low': 0, 'Medium': 1, 'High': 2}
    parental_val = np.array([parental_support_map[x] for x in parental_support])
    
    # Map binary features
    extra_val = np.array([1 if x == 'Yes' else 0 for x in extracurricular])
    internet_val = np.array([1 if x == 'Yes' else 0 for x in internet_access])
    
    # Calculate Final Grade based on features with some noise
    final_grade = (
        0.4 * previous_grade +
        2.5 * study_hours +
        0.3 * (attendance - 50) +
        1.5 * sleep_hours +
        3.0 * parental_val +
        2.0 * extra_val +
        2.0 * internet_val +
        np.random.normal(0, 3, num_samples)
    )
    # Clip final grade between 0 and 100
    final_grade = np.clip(final_grade, 0, 100)
    
    # Define Grade Class
    grade_class = []
    for g in final_grade:
        if g >= 85:
            grade_class.append('Excellent')
        elif g >= 70:
            grade_class.append('Good')
        elif g >= 50:
            grade_class.append('Pass')
        else:
            grade_class.append('Fail')
            
    df = pd.DataFrame({
        'Study_Hours': np.round(study_hours, 1),
        'Attendance': np.round(attendance, 1),
        'Sleep_Hours': np.round(sleep_hours, 1),
        'Parental_Support': parental_support,
        'Extracurricular': extracurricular,
        'Internet_Access': internet_access,
        'Previous_Grade': np.round(previous_grade, 1),
        'Final_Grade': np.round(final_grade, 1),
        'Grade_Class': grade_class
    })
    
    return df

if __name__ == '__main__':
    print("Generating student performance dataset...")
    df = generate_student_data()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    csv_path = os.path.join(os.path.dirname(__file__), 'student_data.csv')
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path}")
    print(df.head())
    print("\nGrade distribution:")
    print(df['Grade_Class'].value_counts())
