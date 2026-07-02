# Student Performance Prediction System (AIML Final Year Project)

An interactive, responsive Machine Learning web application designed to predict a student's final percentage and grade category based on study habits, sleep patterns, attendance rates, and parental support. Built with **Django** (Backend), **Vanilla CSS** (Premium Glassmorphic UI), and **Scikit-Learn** (Random Forest ML Regressor).

---

## 🚀 Quick Start Guide

### 1. Open in VS Code
1. Extract the downloaded ZIP archive `student_performance_prediction.zip` to a folder of your choice.
2. Launch Visual Studio Code (VS Code).
3. Go to **File > Open Folder...** and select the extracted project folder.

### 2. Install Dependencies
Open the VS Code Terminal (**Ctrl + `** or **Terminal > New Terminal**) and execute:
```bash
pip install -r requirements.txt
```
*(Note: Use `py -m pip install -r requirements.txt` on Windows if standard pip refers to a different Python installation).*

### 3. Initialize Django Database
Before running the server, apply database migrations:
```bash
python manage.py migrate
```
*(Note: If you have multiple python versions, use `py manage.py migrate`)*

### 4. Run the Development Server
Start the Django web server:
```bash
python manage.py runserver
```
Once the server starts, open your web browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🧠 Machine Learning Model Pipeline

The ML model uses a **Random Forest Regressor** trained on a generated dataset of 1,000 students to identify relationships between student lifestyle choices and final grades.

If you ever wish to modify parameters or retrain the model:
1. **Regenerate Synthetic Dataset:**
   ```bash
   py model/generate_data.py
   ```
   This generates student attributes and exports them to `model/student_data.csv`.

2. **Retrain the Model:**
   ```bash
   py model/train_model.py
   ```
   This trains the Random Forest model and outputs:
   - `model/model.pkl` (the saved model pipeline)
   - `model/model_metrics.json` (performance metrics & feature importances shown on the dashboard)

---

## 📁 Project Structure

```text
student_prediction/
│
├── model/                     # Machine Learning Code
│   ├── generate_data.py       # Script to simulate student dataset
│   ├── train_model.py         # ML model training script
│   ├── student_data.csv       # Training dataset
│   ├── model.pkl              # Saved trained Random Forest pipeline
│   └── model_metrics.json     # Saved evaluation metrics & feature importances
│
├── student_prediction/        # Django Core Configuration
│   ├── settings.py            # Global project settings (database, apps)
│   ├── urls.py                # Main URL router
│   └── ...
│
├── predictor/                 # Django App (Predictor logic)
│   ├── templates/predictor/   # HTML views
│   │   ├── base.html          # Shared layout with glassmorphic shell
│   │   ├── index.html         # User input page (sliders/radios)
│   │   ├── results.html       # Prediction score and AI recommendations
│   │   ├── dashboard.html     # Model metrics & Feature importance charts
│   │   └── error.html         # User feedback error page
│   ├── static/predictor/css/  # Custom styles
│   │   └── style.css          # Beautiful dark glassmorphism stylesheet
│   ├── urls.py                # App-specific URL routes
│   └── views.py               # Main prediction & recommendation logic
│
├── requirements.txt           # Python dependency file
├── package_project.py         # Script to ZIP the project to your Downloads folder
└── README.md                  # This documentation file
```

---

## 🌟 Key Features
- **Predictive Intelligence:** Accurately calculates predicted final score percentage using 7 lifestyle and academic variables.
- **Dynamic AI Recommendation Engine:** Run what-if simulations to show students *exactly* how increasing study hours or improving attendance by specific increments increases their predicted grade class.
- **Glassmorphic Analytics Dashboard:** Interactive charts showing model statistics (R² Score, MAE, RMSE) and animated feature importances.
