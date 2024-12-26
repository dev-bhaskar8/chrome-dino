import argparse
import time
from ai import DinoNeuralNetwork, GameInterface

def play_game(model_path: str = 'best_dino.h5'):
    """Load a trained model and let it play the game"""
    print("Loading trained model...")
    dino = DinoNeuralNetwork()
    dino.model.load_weights(model_path)
    
    print("Starting game...")
    game = GameInterface()  # Browser will be visible
    
    try:
        total_games = 0
        high_score = 0
        
        while True:
            total_games += 1
            print(f"\nGame #{total_games}")
            
            # Reset game state
            game.reset_game()
            time.sleep(0.5)  # Give the game time to reset
            
            # Play until game over
            while not game.is_game_over():
                # Get current game state
                state = game.get_game_state()
                
                # Get AI's decision
                action = dino.predict(state)
                
                # Perform the action
                game.perform_action(action)
            
            # Get final score
            score, duration = game.get_score()
            high_score = max(high_score, score)
            
            print(f"Score: {score:.0f}")
            print(f"Duration: {duration:.1f} seconds")
            print(f"High Score: {high_score:.0f}")
            
            # Wait a bit before starting next game
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping game...")
    finally:
        print(f"\nFinal Statistics:")
        print(f"Total Games Played: {total_games}")
        print(f"High Score: {high_score:.0f}")

def main():
    parser = argparse.ArgumentParser(description='Watch trained AI play Chrome Dino Game')
    parser.add_argument('--model', type=str, default='best_dino.h5',
                      help='Path to the trained model file')
    
    args = parser.parse_args()
    
    play_game(model_path=args.model)

if __name__ == "__main__":
    main() 