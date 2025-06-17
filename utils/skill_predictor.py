import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler 
from sklearn.metrics import classification_report, confusion_matrix
from neural_network import FFNeuralNetwork

"""Since the resulting matrices are huge, use this to get the full representation instead of seeing a ...
    np.set_printoptions(threshold=np.inf)
"""

def thermometer_encode(values, num_levels):
    thermometer = np.zeros((len(values), num_levels), dtype=np.float32)
    for i, v in enumerate(values):
        thermometer[i, :v+1] = 1.0  
    return thermometer

# Scaler object to scale input features for faster training
scaler = StandardScaler()

class SkillPredictor:
    """Note: SkillPredictor is meant to be process and trained ONCE: as a result if a new dataset is used, make a new object.
        However, predict() can be called multiple times.
    """
    def __init__(self, train_data_name="competency_v2_train.csv", test_data_name="competency_v2_test.csv"):
        """ Creates a SkillPredictor object 
            1. Initialises the train and test data set (make sure to get the location right!)
            2. Processes them into input feature vectors of R^d, where d is the number of features
        """
        # Initialises training and testing datasets
        self.train_df = pd.read_csv(train_data_name)
        self.test_df = pd.read_csv(test_data_name)
        self.skill_predictor = None # Uninitialised
        self.num_classes = 0 # Default
        
    def process_datasets_and_train(self):
        # Shift labels by -1 for training with thermometer encoding:
        # Why: Question diffculty and skill are between 1 and x, but to be used in the nn they are required to be between 0 and x-1
        y_train = self.train_df['skill_level'].values.astype(int) - 1
        y_test = self.test_df['skill_level'].values.astype(int) - 1
        self.num_classes = max(y_train.max(), y_test.max()) + 1

        train_qdiff = self.train_df['question_difficulty'].values.astype(int) - 1
        test_qdiff = self.test_df['question_difficulty'].values.astype(int) - 1
        # This must match num_classes
        num_qdiff_levels = self.num_classes
        
        # Perofrming thermometer encoding
        train_qdiff_thermo = thermometer_encode(train_qdiff, num_qdiff_levels)
        test_qdiff_thermo = thermometer_encode(test_qdiff, num_qdiff_levels)
        
        # Other features that do not require hermometer encoding
        feature_cols_no_qdiff = [
            'time_spent_sec',
            'mcq_correct',
            'past_correct_pct'
        ]

        # Building feature matrices
        X_train = np.concatenate([
            self.train_df[feature_cols_no_qdiff].values.astype(np.float32),
            train_qdiff_thermo
        ], axis=1)

        X_test = np.concatenate([
            self.test_df[feature_cols_no_qdiff].values.astype(np.float32),
            test_qdiff_thermo
        ], axis=1)

        # Scale features
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        input_dim = X_train.shape[1]

        # Train and return self.skill_predictor
        self.skill_predictor = FFNeuralNetwork(input_dim=input_dim, num_classes=self.num_classes)
        self.skill_predictor.train(X_train_scaled, y_train, epochs=50)
        
        # Return training statistics
        y_pred = self.skill_predictor.predict(X_test_scaled).argmax(axis=1)
        print(classification_report(y_test + 1, y_pred + 1))  # shift back to 1–5
        print(confusion_matrix(y_test + 1, y_pred + 1))
        
        return self.skill_predictor

    def predict(self, raw_df):
        """
        This method uses the (assumed to be) trained neural model to determine the skill increment: 
        this is to be used in the computation of the new skill level via a moving average.
        
        Predict skill levels from a raw DataFrame (with columns like the training data).
        Returns predicted skill levels in the range between 1 to num_classes.
        """
        # Extract and thermometer encode question difficulty
        num_qdiff_levels = self.num_classes
        qdiff = raw_df['question_difficulty'].values.astype(int) - 1
        qdiff_thermo = thermometer_encode(qdiff, num_qdiff_levels)

        # Other features (excluding question difficulty)
        feature_cols_no_qdiff = [
            'time_spent_sec',
            'mcq_correct',
            'past_correct_pct'
        ]
        
        # creating input feature vector 
        X = np.concatenate([
            raw_df[feature_cols_no_qdiff].values.astype(np.float32),
            qdiff_thermo
        ], axis=1)

        # Scale features
        X_scaled = scaler.transform(X)

        # Predict and shift output back to 1–num_classes
        predictions = self.skill_predictor.predict(X_scaled)
        predicted_classes = predictions.argmax(axis=1) + 1
        
        return predicted_classes


# Call this function to get a sample of the workings of this class!
def sample_main():
    predictor = SkillPredictor()
    predictor.process_datasets_and_train()
    
    test_df = pd.read_csv("competency_v2_test.csv")
    predicted_skill_levels = predictor.predict(test_df)

    print("Predicted skill levels for test set:")
    print(predicted_skill_levels)
    
## sample_main()
