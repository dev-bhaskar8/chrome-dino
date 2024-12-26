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
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--mute-audio')  # Mute audio for training
        
        # Handle different platforms
        system = platform.system()
        arch = platform.machine()
        
        if system == "Darwin" and arch == "arm64":
            # For Mac with Apple Silicon
            options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            chromedriver_path = "/opt/homebrew/bin/chromedriver"
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
            time.sleep(1)
            
            # Start the game
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)
            
        except Exception as e:
            raise Exception(f"Failed to initialize game: {str(e)}")
    
    def get_game_state(self) -> List[float]:
        """
        Extract game state from browser
        Returns: [distance_to_obstacle, game_speed, obstacle_type, obstacle_height]
        """
        try:
            game_state = self.driver.execute_script("""
                const game = window.gameInstance;
                if (!game) return null;
                
                const dino = game.dino;
                const obstacles = game.obstacles || [];
                
                let nearestObstacle = null;
                let minDistance = Infinity;
                
                for (const obstacle of obstacles) {
                    const distance = obstacle.x - dino.x;
                    if (distance > 0 && distance < minDistance) {
                        minDistance = distance;
                        nearestObstacle = obstacle;
                    }
                }
                
                return {
                    distance: nearestObstacle ? nearestObstacle.x - dino.x : 1000,
                    speed: game.GAME_SPEED || 0,
                    type: nearestObstacle ? (nearestObstacle.type === 'pterodactyl' ? 1 : 0) : 0,
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
        except Exception:
            return [1000, 0, 0, 0]
    
    def perform_action(self, action: List[float]):
        """
        Perform action in browser
        action: [jump_probability, duck_probability]
        """
        try:
            jump_prob, duck_prob = action
            
            if jump_prob > 0.5:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)
            elif duck_prob > 0.5:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
            else:
                # Release duck if we were ducking
                self.driver.execute_script("""
                    const game = window.gameInstance;
                    if (game) {
                        game.isDucking = false;
                    }
                """)
        except Exception:
            pass
    
    def get_score(self) -> Tuple[float, float]:
        """Get the current score and survival time"""
        try:
            game_data = self.driver.execute_script("""
                const game = window.gameInstance;
                return game ? {
                    score: game.score || 0,
                    time: game.frameCount || 0
                } : null;
            """)
            
            if not game_data:
                return 0, 0
                
            return (
                float(game_data['score']),
                float(game_data['time']) / 60  # Convert frames to seconds
            )
        except Exception:
            return 0, 0
    
    def is_game_over(self) -> bool:
        """Check if the game is over"""
        try:
            return bool(self.driver.execute_script("""
                const game = window.gameInstance;
                return game ? game.gameOver : true;
            """))
        except Exception:
            return True
    
    def reset_game(self):
        """Reset the game"""
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)
            time.sleep(0.1)  # Give the game time to reset
        except Exception:
            pass
    
    def __del__(self):
        """Clean up browser when done"""
        if hasattr(self, 'driver'):
            self.driver.quit() 