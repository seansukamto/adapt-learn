import tensorflow as tf
# warnings from the below improt statements are ignored: if you have installed tensorflow there should be no problem
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Dense, Flatten, Dropout, BatchNormalization # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from tensorflow.keras.losses import SparseCategoricalCrossentropy # type: ignore
from tensorflow.keras.metrics import SparseCategoricalAccuracy # type: ignore
from tensorflow.keras.callbacks import EarlyStopping # type: ignore

import pandas as pd
import numpy as np

# Do not use this class directly! Use the class DifficultyPredictor
class FFNeuralNetwork:
    def __init__(self, input_dim, num_classes):
        # Building and compiling the model
        self.model = Sequential([
            Dense(64, activation='relu', input_shape=(input_dim,)),
            BatchNormalization(),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(num_classes, activation='softmax')
            ])
        
        self.model.compile(optimizer=Adam(),
                loss=SparseCategoricalCrossentropy(),
                metrics=[SparseCategoricalAccuracy()]
                )

    # Train the model
    def train(self, x_train, y_train, epochs):
        self.model.fit(
            x_train, y_train, epochs=epochs, 
            validation_split=0.1,
            callbacks=[EarlyStopping(patience=5, restore_best_weights=True)]
        )

    # Evaluate the model
    def evaluate(self, x_test, y_test):
        test_loss, test_acc = self.model.evaluate(x_test, y_test)
        print(f'\nTest accuracy: {test_acc}')
        
    # Make Predictions
    def predict(self, x_val):
        prediction = self.model.predict(x_val)
        
        return prediction






