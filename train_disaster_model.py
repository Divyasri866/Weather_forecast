# weather_app/ml/train_disaster_model.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

# Sample training data – You can expand this with real-world data
data = pd.DataFrame({
    'temperature': [30, 22, 40, 35, 25, 45, 18],
    'humidity': [80, 60, 30, 90, 55, 25, 95],
    'rain_probability': [90, 20, 10, 95, 30, 5, 100],
    'wind_speed': [15, 5, 20, 25, 10, 30, 12],
    'disaster': ['Flood', 'None', 'Drought', 'Flood', 'None', 'Drought', 'Flood']
})

X = data[['temperature', 'humidity', 'rain_probability', 'wind_speed']]
y = data['disaster']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'ml', 'disaster_model.pkl')
joblib.dump(model, model_path)

print("✅ Disaster prediction model trained and saved at:", model_path)
