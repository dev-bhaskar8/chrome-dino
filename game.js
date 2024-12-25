class Game {
    constructor() {
        this.canvas = document.getElementById('game');
        this.ctx = this.canvas.getContext('2d');
        
        // Game constants
        this.GRAVITY = 0.6;
        this.JUMP_SPEED = -10;
        this.GROUND_HEIGHT = this.canvas.height - 100;
        this.INITIAL_GAME_SPEED = 6;
        this.GAME_SPEED = this.INITIAL_GAME_SPEED;
        this.MAX_JUMP_HEIGHT = 100;

        // Sprite positions
        this.SPRITE = {
            DINO: {
                IDLE: { x: 848, y: 0, w: 44, h: 47 },
                RUNNING: [
                    { x: 936, y: 0, w: 44, h: 47 },
                    { x: 980, y: 0, w: 44, h: 47 }
                ],
                DUCKING: [
                    { x: 1112, y: 0, w: 59, h: 47 },
                    { x: 1171, y: 0, w: 59, h: 47 }
                ],
                DEAD: { x: 1024, y: 0, w: 44, h: 47 }
            },
            CACTUS: {
                SMALL: [
                    { x: 228, y: 0, w: 17, h: 35 },
                    { x: 245, y: 0, w: 34, h: 35 },
                    { x: 279, y: 0, w: 51, h: 35 }
                ],
                LARGE: [
                    { x: 332, y: 0, w: 25, h: 50 },
                    { x: 357, y: 0, w: 50, h: 50 },
                    { x: 407, y: 0, w: 75, h: 50 }
                ]
            },
            PTERODACTYL: [
                { x: 134, y: 0, w: 46, h: 40 },
                { x: 180, y: 0, w: 46, h: 40 }
            ],
            CLOUD: { x: 86, y: 2, w: 46, h: 16 },
            GROUND: { x: 2, y: 54, w: 1200, h: 12 },
            GAME_OVER: { x: 655, y: 15, w: 191, h: 11 },
            RESTART: { x: 2, y: 2, w: 36, h: 32 }
        };

        // Sound effects setup
        this.soundEnabled = false;
        this.sounds = {};
        
        // Debug mode
        this.DEBUG = false;
        
        // Add debug controls
        document.addEventListener('keydown', (event) => {
            if (event.code === 'KeyD') {
                this.DEBUG = !this.DEBUG;
                console.log('Debug mode:', this.DEBUG);
            }
        });
        
        // Initialize game
        this.reset();
        
        // Event listeners
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('keyup', this.handleKeyUp.bind(this));
        this.canvas.addEventListener('click', this.handleClick.bind(this));
        
        // Start game loop when sprite is loaded
        this.sprite = new Image();
        this.sprite.src = 'assets/sprite.png';
        this.sprite.onload = () => {
            this.gameLoop();
        };

        // Initialize sounds after first user interaction
        const initSounds = () => {
            if (!this.soundEnabled) {
                this.sounds = {
                    jump: new Audio('assets/jump.wav'),
                    die: new Audio('assets/die.wav'),
                    point: new Audio('assets/point.wav')
                };

                // Set volume for all sounds
                Object.values(this.sounds).forEach(sound => {
                    sound.volume = 0.3; // Lower volume for better experience
                });

                this.soundEnabled = true;
                console.log('Sounds initialized');
            }
            
            // Remove the event listeners after initialization
            document.removeEventListener('click', initSounds);
            document.removeEventListener('keydown', initSounds);
        };

        // Add event listeners for first interaction
        document.addEventListener('click', initSounds);
        document.addEventListener('keydown', initSounds);
    }

    handleClick(event) {
        if (this.gameOver) {
            // Get click coordinates relative to canvas
            const rect = this.canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            // Check if click is within restart button bounds
            const restartX = this.canvas.width / 2 - this.SPRITE.RESTART.w / 2;
            const restartY = this.canvas.height / 2 + 20;
            const restartW = this.SPRITE.RESTART.w;
            const restartH = this.SPRITE.RESTART.h;
            
            if (x >= restartX && x <= restartX + restartW &&
                y >= restartY && y <= restartY + restartH) {
                this.reset();
                requestAnimationFrame(this.gameLoop.bind(this));
            }
        }
    }

    reset() {
        // Game state
        this.score = 0;
        this.highScore = parseInt(localStorage.getItem('highScore')) || 0;
        this.gameOver = false;
        this.isJumping = false;
        this.isDucking = false;
        this.isNight = false;
        this.frameCount = 0;
        this.GAME_SPEED = this.INITIAL_GAME_SPEED;
        
        // Reset game objects
        this.dino = {
            x: 50,
            y: this.GROUND_HEIGHT,
            width: 44,
            height: 47,
            velocityY: 0,
            frame: 0
        };
        
        this.obstacles = [];
        this.clouds = [];

        // Update score display
        document.getElementById('current-score').textContent = '00000';
        document.getElementById('hi-score').textContent = 
            'HI ' + String(Math.floor(this.highScore/100)).padStart(5, '0');
    }
    
    handleKeyDown(event) {
        if (this.gameOver) {
            if (event.code === 'Space' || event.code === 'ArrowUp' || event.code === 'ArrowDown') {
                this.reset();
                requestAnimationFrame(this.gameLoop.bind(this)); // Restart game loop
                return;
            }
        }
        
        if ((event.code === 'Space' || event.code === 'ArrowUp') && !this.isJumping) {
            this.jump();
            this.playSound('jump');
        } else if (event.code === 'ArrowDown') {
            this.isDucking = true;
            if (!this.isJumping) {
                this.dino.height = 30;
            }
        }
    }
    
    handleKeyUp(event) {
        if (event.code === 'ArrowDown') {
            this.isDucking = false;
            this.dino.height = 47; // Reset height
        }
    }
    
    jump() {
        if (this.dino.y === this.GROUND_HEIGHT) {
            this.isJumping = true;
            this.dino.velocityY = this.JUMP_SPEED;
        }
    }
    
    spawnObstacle() {
        const rand = Math.random();
        let obstacle;
        
        if (rand < 0.7) { // 70% chance for cactus
            const isBig = Math.random() > 0.5;
            const variant = Math.floor(Math.random() * 3);
            const spriteData = isBig ? this.SPRITE.CACTUS.LARGE[variant] : this.SPRITE.CACTUS.SMALL[variant];
            
            obstacle = {
                x: this.canvas.width,
                y: this.GROUND_HEIGHT + (isBig ? -15 : 0),
                width: spriteData.w,
                height: spriteData.h,
                sprite: spriteData,
                type: 'cactus'
            };
        } else { // 30% chance for pterodactyl
            const height = this.GROUND_HEIGHT - 40 - Math.random() * 20;
            obstacle = {
                x: this.canvas.width,
                y: height,
                width: this.SPRITE.PTERODACTYL[0].w,
                height: this.SPRITE.PTERODACTYL[0].h,
                sprite: this.SPRITE.PTERODACTYL[0],
                frame: 0,
                type: 'pterodactyl'
            };
        }
        
        this.obstacles.push(obstacle);
    }
    
    spawnCloud() {
        const cloud = {
            x: this.canvas.width,
            y: Math.random() * 30 + 20,
            sprite: this.SPRITE.CLOUD
        };
        this.clouds.push(cloud);
    }
    
    checkCollision(dino, obstacle) {
        return !(
            dino.x + dino.width < obstacle.x + 10 || // Add some padding
            dino.x > obstacle.x + obstacle.width - 10 ||
            dino.y + dino.height < obstacle.y + 10 ||
            dino.y > obstacle.y + obstacle.height - 10
        );
    }
    
    update() {
        this.frameCount++;
        
        // Update dino position and animation
        if (this.isJumping) {
            this.dino.velocityY += this.GRAVITY;
            this.dino.y += this.dino.velocityY;
            
            if (this.dino.y >= this.GROUND_HEIGHT) {
                this.dino.y = this.GROUND_HEIGHT;
                this.dino.velocityY = 0;
                this.isJumping = false;
            }
        }
        
        // Animate dino
        if (this.frameCount % 6 === 0) {
            this.dino.frame = (this.dino.frame + 1) % 2;
        }
        
        // Spawn obstacles
        if (this.frameCount % 50 === 0 && Math.random() < 0.3) {
            this.spawnObstacle();
        }
        
        // Spawn clouds
        if (this.frameCount % 100 === 0 && Math.random() < 0.5) {
            this.spawnCloud();
        }
        
        // Update obstacles
        this.obstacles = this.obstacles.filter(obstacle => {
            obstacle.x -= this.GAME_SPEED;
            
            if (obstacle.type === 'pterodactyl' && this.frameCount % 15 === 0) {
                obstacle.frame = (obstacle.frame + 1) % 2;
                obstacle.sprite = this.SPRITE.PTERODACTYL[obstacle.frame];
            }
            
            if (this.checkCollision(this.dino, obstacle)) {
                this.gameOver = true;
                this.playSound('die');
            }
            
            return obstacle.x > -obstacle.width;
        });
        
        // Update clouds
        this.clouds = this.clouds.filter(cloud => {
            cloud.x -= this.GAME_SPEED * 0.5;
            return cloud.x > -cloud.sprite.w;
        });
        
        // Update score
        if (!this.gameOver) {
            this.score++;
            const newScore = Math.floor(this.score/100);
            const oldScore = Math.floor((this.score-1)/100);
            
            if (newScore > oldScore) {
                this.playSound('point');
            }
            
            document.getElementById('current-score').textContent = 
                String(newScore).padStart(5, '0');
                
            if (this.score > this.highScore) {
                this.highScore = this.score;
                localStorage.setItem('highScore', this.highScore);
                document.getElementById('hi-score').textContent = 
                    'HI ' + String(Math.floor(this.highScore/100)).padStart(5, '0');
            }
        }
        
        // Increase game speed over time
        if (this.score % 100 === 0) {
            this.GAME_SPEED += 0.1;
        }
    }
    
    drawSprite(spriteData, x, y) {
        this.ctx.drawImage(
            this.sprite,
            spriteData.x, spriteData.y,
            spriteData.w, spriteData.h,
            x, y,
            spriteData.w, spriteData.h
        );
    }
    
    draw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw clouds
        this.clouds.forEach(cloud => {
            this.drawSprite(cloud.sprite, cloud.x, cloud.y);
        });
        
        // Draw ground (using the sprite instead of drawing lines)
        const groundPattern = this.SPRITE.GROUND;
        let groundX = -(this.frameCount * this.GAME_SPEED) % groundPattern.w;
        
        // Draw two segments to create seamless scrolling
        this.drawSprite(groundPattern, groundX, this.GROUND_HEIGHT + 20);
        this.drawSprite(groundPattern, groundX + groundPattern.w, this.GROUND_HEIGHT + 20);
        
        // Draw dino
        let dinoSprite;
        if (this.gameOver) {
            dinoSprite = this.SPRITE.DINO.DEAD;
        } else if (this.isDucking) {
            dinoSprite = this.SPRITE.DINO.DUCKING[this.dino.frame];
        } else if (this.isJumping) {
            dinoSprite = this.SPRITE.DINO.IDLE;
        } else {
            dinoSprite = this.SPRITE.DINO.RUNNING[this.dino.frame];
        }
        this.drawSprite(dinoSprite, this.dino.x, this.dino.y);
        
        // Draw obstacles
        this.obstacles.forEach(obstacle => {
            this.drawSprite(obstacle.sprite, obstacle.x, obstacle.y);
            
            // Draw collision boxes in debug mode
            if (this.DEBUG) {
                this.ctx.strokeStyle = 'red';
                this.ctx.strokeRect(
                    obstacle.x + 10,
                    obstacle.y + 10,
                    obstacle.width - 20,
                    obstacle.height - 20
                );
            }
        });

        // Draw game over screen
        if (this.gameOver) {
            // Game Over text
            this.drawSprite(
                this.SPRITE.GAME_OVER,
                this.canvas.width / 2 - this.SPRITE.GAME_OVER.w / 2,
                this.canvas.height / 2 - 20
            );
            
            // Restart button
            this.drawSprite(
                this.SPRITE.RESTART,
                this.canvas.width / 2 - this.SPRITE.RESTART.w / 2,
                this.canvas.height / 2 + 20
            );
        }

        // Draw debug info
        if (this.DEBUG) {
            this.ctx.strokeStyle = 'blue';
            this.ctx.strokeRect(
                this.dino.x + 10,
                this.dino.y + 10,
                this.dino.width - 20,
                this.dino.height - 20
            );

            this.ctx.fillStyle = '#535353';
            this.ctx.font = '12px monospace';
            const debugInfo = [
                `Speed: ${this.GAME_SPEED.toFixed(2)}`,
                `Jump: ${this.isJumping}`,
                `Duck: ${this.isDucking}`,
                `Y: ${Math.floor(this.dino.y)}`,
                `VelY: ${this.dino.velocityY.toFixed(2)}`,
                `Frame: ${this.frameCount}`,
                `Obstacles: ${this.obstacles.length}`
            ];
            debugInfo.forEach((text, i) => {
                this.ctx.fillText(text, 5, 15 + i * 15);
            });
        }
    }
    
    gameLoop() {
        this.update();
        this.draw();
        if (!this.gameOver) {
            requestAnimationFrame(this.gameLoop.bind(this));
        }
    }

    // Add test methods
    testJump() {
        console.log('Testing jump mechanics...');
        this.jump();
        return this.isJumping && this.dino.velocityY < 0;
    }

    testCollision() {
        console.log('Testing collision detection...');
        const testObstacle = {
            x: this.dino.x + 20,
            y: this.dino.y,
            width: 20,
            height: 40
        };
        return this.checkCollision(this.dino, testObstacle);
    }

    testSound() {
        console.log('Testing sound effects...');
        try {
            this.sounds.jump.play().catch(() => {});
            this.sounds.die.play().catch(() => {});
            this.sounds.point.play().catch(() => {});
            return true;
        } catch (error) {
            console.error('Sound test failed:', error);
            return false;
        }
    }

    runTests() {
        console.log('Running game tests...');
        
        const tests = {
            'Jump mechanics': this.testJump.bind(this),
            'Collision detection': this.testCollision.bind(this),
            'Sound effects': this.testSound.bind(this)
        };

        for (const [name, test] of Object.entries(tests)) {
            try {
                const result = test();
                console.log(`${name}: ${result ? 'PASS' : 'FAIL'}`);
            } catch (error) {
                console.error(`${name}: ERROR -`, error);
            }
        }
    }

    playSound(soundName) {
        if (!this.soundEnabled) return;
        
        const sound = this.sounds[soundName];
        if (sound) {
            try {
                // Reset the sound to start
                sound.currentTime = 0;
                
                // Create a promise to handle the play
                const playPromise = sound.play();
                
                if (playPromise !== undefined) {
                    playPromise
                        .then(() => {
                            // Sound played successfully
                        })
                        .catch(error => {
                            // Auto-play was prevented or there was an error
                            console.log(`Sound play failed: ${error}`);
                        });
                }
            } catch (error) {
                console.log(`Error playing sound: ${error}`);
            }
        }
    }
}

// Start the game when the page loads
window.onload = () => {
    const game = new Game();
    
    // Add game instance to window for debugging
    window.game = game;
    console.log('Game loaded. Press D to toggle debug mode.');
    console.log('Access game instance via window.game');
}; 