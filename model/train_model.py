import pandas as pd
import numpy as np
import os
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

def train():
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'student_data.csv')
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please run generate_data.py first.")
        
    df = pd.read_csv(csv_path)
    
    # Define features and target
    X = df.drop(columns=['Final_Grade', 'Grade_Class'])
    y = df['Final_Grade']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Identify column types
    numerical_cols = ['Study_Hours', 'Attendance', 'Sleep_Hours', 'Previous_Grade']
    categorical_cols = ['Parental_Support', 'Extracurricular', 'Internet_Access']
    
    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(drop='first'), categorical_cols)
        ])
    
    # Define model pipeline
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Train model
    print("Training Random Forest Regressor model...")
    model_pipeline.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model_pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"Model Evaluation:")
    print(f"R² Score: {r2:.4f}")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    
    # Get feature importances
    regressor = model_pipeline.named_steps['regressor']
    
    # Extract feature names after one-hot encoding
    cat_encoder = model_pipeline.named_steps['preprocessor'].named_transformers_['cat']
    encoded_cat_cols = list(cat_encoder.get_feature_names_out(categorical_cols))
    all_feature_names = numerical_cols + encoded_cat_cols
    
    importances = regressor.feature_importances_
    feature_importance_dict = dict(zip(all_feature_names, importances.tolist()))
    
    # Sort feature importances
    sorted_importance = sorted(feature_importance_dict.items(), key=lambda item: item[1], reverse=True)
    
    # Save model and preprocessor pipeline
    model_pkl_path = os.path.join(base_dir, 'model.pkl')
    joblib.dump(model_pipeline, model_pkl_path)
    print(f"Model pipeline saved to {model_pkl_path}")
    
    # Save training metrics and feature importances for Django dashboard
    metrics = {
        'r2_score': round(r2, 4),
        'mae': round(mae, 4),
        'rmse': round(rmse, 4),
        'feature_importance': sorted_importance,
        'dataset_size': len(df),
        'train_size': len(X_train),
        'test_size': len(X_test)
    }
    
    metrics_json_path = os.path.join(base_dir, 'model_metrics.json')
    with open(metrics_json_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Metrics saved to {metrics_json_path}")

if __name__ == '__main__':
    train()
