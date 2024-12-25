# Chrome Dino Game Clone

A faithful recreation of Chrome's offline dinosaur game using pure JavaScript and HTML5 Canvas.

## Vision

Our vision is to create an exact 1:1 clone of Chrome's offline dinosaur game with:

1. **Visuals**:
   - Using the official Chrome dino sprite sheet
   - Exact same animations and visual effects
   - Day/night cycle

2. **Core Mechanics**:
   - Running T-Rex character
   - Jumping over cacti
   - Ducking under pterodactyls
   - Accurate physics and collision detection

3. **Controls**:
   - SPACE/UP to jump
   - DOWN to duck
   - Click on restart sprite to restart
   - Any dino control to restart after game over

4. **Features**:
   - Score tracking
   - High score storage using localStorage
   - Increasing difficulty over time
   - Original sound effects
   - Debug mode (press 'D')

5. **Technical Requirements**:
   - Pure JavaScript (no frameworks)
   - HTML5 Canvas for rendering
   - WAV format sound effects
   - Local server for development

## Features

- Exact 1:1 clone of the Chrome dinosaur game
- Pure JavaScript implementation (no frameworks)
- Original game mechanics:
  - Running T-Rex that jumps over cacti
  - Ducking under pterodactyls
  - Score tracking with high score persistence
  - Increasing difficulty over time
  - Day/night cycle
  - Original sound effects
  - Original sprite sheet

## How to Play

1. Press SPACE or UP ARROW to jump
2. Press DOWN ARROW to duck
3. Avoid cacti and pterodactyls
4. Score points by surviving longer
5. After game over:
   - Click the restart button
   - OR press any dino control key (SPACE/UP/DOWN)

## Development

The game uses:
- HTML5 Canvas for rendering
- Local Storage for high score persistence
- Original Chrome dino sprite sheet
- WAV format sound effects

## Running Locally

Due to browser security restrictions when loading audio files, you need to serve the game through a web server. You can use Python's built-in server:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000` in your browser.

## Files

- `index.html` - Game HTML structure
- `style.css` - Game styling
- `game.js` - Game logic and mechanics
- `assets/` - Game assets (sprite sheet and sounds)

## Debug Mode

Press 'D' to toggle debug mode, which shows:
- Collision boxes
- Game speed
- Jump/duck state
- Position and velocity
- Frame count
- Number of obstacles 