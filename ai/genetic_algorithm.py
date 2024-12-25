import numpy as np
from typing import List, Tuple
from .neural_network import DinoNeuralNetwork

class GeneticAlgorithm:
    def __init__(self, population_size: int = 100, elite_size: int = 10, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.population: List[DinoNeuralNetwork] = []
        self.initialize_population()
    
    def initialize_population(self):
        """Create initial population of neural networks"""
        self.population = [DinoNeuralNetwork() for _ in range(self.population_size)]
    
    def calculate_fitness(self, scores: List[float], survival_times: List[float]) -> List[float]:
        """Calculate fitness scores for each member of the population"""
        return [(score * 1.5 + time * 0.5) for score, time in zip(scores, survival_times)]
    
    def select_parents(self, fitness_scores: List[float]) -> List[Tuple[DinoNeuralNetwork, DinoNeuralNetwork]]:
        """Select parents for next generation using tournament selection"""
        parents = []
        for _ in range(self.population_size - self.elite_size):
            # Tournament selection
            tournament_size = 5
            tournament_indices = np.random.choice(len(self.population), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            parent1_idx = tournament_indices[np.argmax(tournament_fitness)]
            
            # Select second parent
            tournament_indices = np.random.choice(len(self.population), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            parent2_idx = tournament_indices[np.argmax(tournament_fitness)]
            
            parents.append((self.population[parent1_idx], self.population[parent2_idx]))
        return parents
    
    def crossover(self, parent1: DinoNeuralNetwork, parent2: DinoNeuralNetwork) -> DinoNeuralNetwork:
        """Create child neural network from two parents"""
        child = DinoNeuralNetwork()
        child_weights = []
        
        for p1_layer_weights, p2_layer_weights in zip(parent1.get_weights(), parent2.get_weights()):
            # Randomly choose weights from either parent
            child_layer_weights = []
            for p1_w, p2_w in zip(p1_layer_weights, p2_layer_weights):
                mask = np.random.rand(*p1_w.shape) < 0.5
                child_w = np.where(mask, p1_w, p2_w)
                child_layer_weights.append(child_w)
            child_weights.append(child_layer_weights)
        
        child.set_weights(child_weights)
        return child
    
    def mutate(self, network: DinoNeuralNetwork):
        """Apply random mutations to neural network weights"""
        weights = network.get_weights()
        mutated_weights = []
        
        for layer_weights in weights:
            mutated_layer = []
            for w in layer_weights:
                mutation_mask = np.random.rand(*w.shape) < self.mutation_rate
                mutations = np.random.normal(0, 0.1, size=w.shape)
                w = np.where(mutation_mask, w + mutations, w)
                mutated_layer.append(w)
            mutated_weights.append(mutated_layer)
        
        network.set_weights(mutated_weights)
    
    def evolve(self, fitness_scores: List[float]) -> List[DinoNeuralNetwork]:
        """Create next generation of neural networks"""
        # Sort population by fitness
        sorted_indices = np.argsort(fitness_scores)[::-1]
        
        # Keep elite members
        new_population = [self.population[i] for i in sorted_indices[:self.elite_size]]
        
        # Select parents and create offspring
        parents = self.select_parents(fitness_scores)
        for parent1, parent2 in parents:
            child = self.crossover(parent1, parent2)
            self.mutate(child)
            new_population.append(child)
        
        self.population = new_population
        return new_population 