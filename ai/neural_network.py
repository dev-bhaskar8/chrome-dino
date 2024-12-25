import tensorflow as tf
import numpy as np

class DinoNeuralNetwork:
    def __init__(self):
        self.model = self._build_model()
    
    def _build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(4, input_shape=(4,), activation='linear'),  # Input layer
            tf.keras.layers.Dense(8, activation='relu'),                      # Hidden layer
            tf.keras.layers.Dense(2, activation='softmax')                    # Output layer (jump, duck)
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def predict(self, inputs):
        """
        Make a prediction based on game state
        inputs: [distance_to_obstacle, game_speed, obstacle_type, obstacle_height]
        returns: [jump_probability, duck_probability]
        """
        inputs = np.array(inputs).reshape(1, -1)
        return self.model.predict(inputs, verbose=0)[0]
    
    def get_weights(self):
        """Get the neural network weights for genetic algorithm"""
        return [layer.get_weights() for layer in self.model.layers]
    
    def set_weights(self, weights):
        """Set the neural network weights from genetic algorithm"""
        for layer, w in zip(self.model.layers, weights):
            layer.set_weights(w) 