import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler 
from sklearn.metrics import classification_report, confusion_matrix
from neural_network import FFNeuralNetwork

np.set_printoptions(threshold=np.inf)

def thermometer_encode(values, num_levels):
    thermometer = np.zeros((len(values), num_levels), dtype=np.float32)
    for i, v in enumerate(values):
        thermometer[i, :v+1] = 1.0  
    return thermometer

# Load data
train_df = pd.read_csv('competency_v2_train.csv')
test_df = pd.read_csv('competency_v2_test.csv')

# Shift labels from 1–5 to 0–4 for training with thermometer encoding
y_train = train_df['skill_level'].values.astype(int) - 1
y_test = test_df['skill_level'].values.astype(int) - 1
num_classes = 5

# Shift question_difficulty from 1–5 to 0–4 for thermometer encoding
train_qdiff = train_df['question_difficulty'].values.astype(int) - 1
test_qdiff = test_df['question_difficulty'].values.astype(int) - 1
num_qdiff_levels = 5

train_qdiff_thermo = thermometer_encode(train_qdiff, num_qdiff_levels)
test_qdiff_thermo = thermometer_encode(test_qdiff, num_qdiff_levels)

# Other features (excluding question_difficulty)
feature_cols_no_qdiff = [
    'time_spent_sec',
    'mcq_correct',
    'past_correct_pct'
]

# Build feature matrices
X_train = np.concatenate([
    train_df[feature_cols_no_qdiff].values.astype(np.float32),
    train_qdiff_thermo
], axis=1)

X_test = np.concatenate([
    test_df[feature_cols_no_qdiff].values.astype(np.float32),
    test_qdiff_thermo
], axis=1)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

input_dim = X_train.shape[1]

# Train and evaluate
skill_predictor = FFNeuralNetwork(input_dim=input_dim, num_classes=num_classes)
skill_predictor.train(X_train_scaled, y_train, epochs=50)
skill_predictor.evaluate(X_test_scaled, y_test)

# Predict and shift output back to 1–5
predictions = skill_predictor.predict(X_test_scaled)
predicted_classes = predictions.argmax(axis=1) + 1
print(predicted_classes)

# Statistics
y_pred = skill_predictor.predict(X_test_scaled).argmax(axis=1)
print(classification_report(y_test + 1, y_pred + 1))  # shift back to 1–5
print(confusion_matrix(y_test + 1, y_pred + 1))

