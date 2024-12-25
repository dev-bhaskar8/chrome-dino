import argparse
from ai import DinoTrainer

def main():
    parser = argparse.ArgumentParser(description='Train AI to play Chrome Dinosaur Game')
    parser.add_argument('--population', type=int, default=100,
                      help='Population size for genetic algorithm')
    parser.add_argument('--generations', type=int, default=100,
                      help='Number of generations to train')
    parser.add_argument('--output', type=str, default='best_dino.h5',
                      help='Output file for best model')
    
    args = parser.parse_args()
    
    # Create and train the AI
    trainer = DinoTrainer(
        population_size=args.population,
        generations=args.generations
    )
    
    print("Starting training...")
    trainer.train()
    
    # Save the best performing model
    trainer.save_best_model(args.output)
    print(f"Training complete! Best model saved to {args.output}")

if __name__ == "__main__":
    main() 