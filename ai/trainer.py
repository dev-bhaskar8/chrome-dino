import numpy as np
from typing import List, Tuple
import matplotlib.pyplot as plt
from .neural_network import DinoNeuralNetwork
from .genetic_algorithm import GeneticAlgorithm
from .game_interface import GameInterface

class DinoTrainer:
    def __init__(self, population_size: int = 100, generations: int = 100):
        self.game_interface = GameInterface()
        self.genetic_algorithm = GeneticAlgorithm(population_size=population_size)
        self.generations = generations
        self.best_scores: List[float] = []
        self.avg_scores: List[float] = []
    
    def train_generation(self) -> Tuple[List[float], List[float]]:
        """Train one generation of dinosaurs"""
        scores = []
        survival_times = []
        
        # Train each member of the population
        for dino in self.genetic_algorithm.population:
            score, time = self.train_dino(dino)
            scores.append(score)
            survival_times.append(time)
        
        return scores, survival_times
    
    def train_dino(self, dino: DinoNeuralNetwork) -> Tuple[float, float]:
        """Train a single dinosaur"""
        self.game_interface.reset_game()
        
        while not self.game_interface.is_game_over():
            # Get current game state
            state = self.game_interface.get_game_state()
            
            # Get action from neural network
            action = dino.predict(state)
            
            # Perform action in game
            self.game_interface.perform_action(action)
        
        # Return final score and survival time
        return self.game_interface.get_score()
    
    def train(self):
        """Train the population for specified number of generations"""
        for generation in range(self.generations):
            print(f"Generation {generation + 1}/{self.generations}")
            
            # Train current generation
            scores, survival_times = self.train_generation()
            
            # Calculate fitness scores
            fitness_scores = self.genetic_algorithm.calculate_fitness(scores, survival_times)
            
            # Record statistics
            self.best_scores.append(max(scores))
            self.avg_scores.append(np.mean(scores))
            
            print(f"Best Score: {max(scores):.2f}")
            print(f"Average Score: {np.mean(scores):.2f}")
            
            # Evolve population
            self.genetic_algorithm.evolve(fitness_scores)
            
            # Plot progress every 10 generations
            if (generation + 1) % 10 == 0:
                self.plot_progress()
    
    def plot_progress(self):
        """Plot training progress"""
        plt.figure(figsize=(10, 6))
        plt.plot(self.best_scores, label='Best Score')
        plt.plot(self.avg_scores, label='Average Score')
        plt.xlabel('Generation')
        plt.ylabel('Score')
        plt.title('Training Progress')
        plt.legend()
        plt.grid(True)
        plt.savefig('training_progress.png')
        plt.close()
    
    def save_best_model(self, filename: str):
        """Save the best performing model"""
        best_idx = np.argmax(self.best_scores)
        best_dino = self.genetic_algorithm.population[best_idx]
        best_dino.model.save(filename)
    
    def load_model(self, filename: str) -> DinoNeuralNetwork:
        """Load a trained model"""
        dino = DinoNeuralNetwork()
        dino.model = tf.keras.models.load_model(filename)
        return dino 