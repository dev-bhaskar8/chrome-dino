import numpy as np
from typing import Dict, List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
import platform
import os
import time

class GameInterface:
    def __init__(self, url: str = "http://localhost:8000"):
        self.url = url
        self.setup_browser()
    
    def setup_browser(self):
        """Initialize the browser and load the game"""
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Commented out for debugging
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Handle different platforms
        system = platform.system()
        arch = platform.machine()
        
        if system == "Darwin" and arch == "arm64":
            # For Mac with Apple Silicon
            options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            chromedriver_path = "/opt/homebrew/bin/chromedriver"  # Updated path for M1/M2 Macs
            if not os.path.exists(chromedriver_path):
                raise Exception(f"ChromeDriver not found at {chromedriver_path}. Please install it using 'brew install --cask chromedriver'")
            service = Service(chromedriver_path)
        else:
            # For other platforms
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
        
        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_window_size(800, 600)
            self.driver.get(self.url)
            
            # Wait for canvas element
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "game"))
            )
            
            # Wait for game to initialize
            time.sleep(2)  # Give time for JavaScript to initialize
            
            # Start the game by pressing space
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)
            
        except Exception as e:
            raise Exception(f"Failed to initialize game: {str(e)}")
    
    def get_game_state(self) -> List[float]:
        """
        Extract game state from browser using JavaScript
        Returns: [distance_to_obstacle, game_speed, obstacle_type, obstacle_height]
        """
        try:
            game_state = self.driver.execute_script("""
                const canvas = document.getElementById('game');
                const game = canvas.gameInstance;
                if (!game) return null;
                
                const tRex = game.tRex;
                const obstacles = game.obstacles || [];
                
                // Get nearest obstacle
                let nearestObstacle = null;
                let minDistance = Infinity;
                
                for (const obstacle of obstacles) {
                    const distance = obstacle.x - tRex.x;
                    if (distance > 0 && distance < minDistance) {
                        minDistance = distance;
                        nearestObstacle = obstacle;
                    }
                }
                
                return {
                    distance: nearestObstacle ? nearestObstacle.x - tRex.x : 1000,
                    speed: game.speed || 0,
                    type: nearestObstacle ? (nearestObstacle.type === 'PTERODACTYL' ? 1 : 0) : 0,
                    height: nearestObstacle ? nearestObstacle.y : 0
                };
            """)
            
            if not game_state:
                return [1000, 0, 0, 0]
            
            return [
                game_state['distance'],
                game_state['speed'],
                game_state['type'],
                game_state['height']
            ]
        except Exception as e:
            print(f"Error getting game state: {e}")
            return [1000, 0, 0, 0]
    
    def perform_action(self, action: List[float]):
        """
        Perform action in browser using JavaScript
        action: [jump_probability, duck_probability]
        """
        jump_prob, duck_prob = action
        
        try:
            if jump_prob > 0.5:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)
            elif duck_prob > 0.5:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
            else:
                # Release duck if we were ducking
                self.driver.execute_script("""
                    const canvas = document.getElementById('game');
                    const game = canvas.gameInstance;
                    if (game && game.tRex) {
                        game.tRex.isDucking = false;
                    }
                """)
        except Exception as e:
            print(f"Error performing action: {e}")
    
    def get_score(self) -> Tuple[float, float]:
        """Get the current score and survival time from browser"""
        try:
            game_data = self.driver.execute_script("""
                const canvas = document.getElementById('game');
                const game = canvas.gameInstance;
                if (!game) return null;
                
                return {
                    score: game.score || 0,
                    time: game.time || 0
                };
            """)
            
            if not game_data:
                return 0, 0
                
            return (
                float(game_data['score']),
                float(game_data['time']) / 1000  # Convert to seconds
            )
        except Exception as e:
            print(f"Error getting score: {e}")
            return 0, 0
    
    def is_game_over(self) -> bool:
        """Check if the game is over in browser"""
        try:
            return bool(self.driver.execute_script("""
                const canvas = document.getElementById('game');
                const game = canvas.gameInstance;
                return game ? game.gameOver : true;
            """))
        except Exception as e:
            print(f"Error checking game over: {e}")
            return True
    
    def reset_game(self):
        """Reset the game in browser"""
        try:
            # Press space to restart
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)
            time.sleep(0.1)  # Give the game time to reset
        except Exception as e:
            print(f"Error resetting game: {e}")
    
    def __del__(self):
        """Clean up browser when done"""
        if hasattr(self, 'driver'):
            self.driver.quit() 