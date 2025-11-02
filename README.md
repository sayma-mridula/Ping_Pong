# 🤖 AI Battle Arena - Intelligent Pong Game

An advanced Pong game featuring AI vs AI battles using **Minimax** and **Hybrid (Fuzzy + Minimax)** algorithms. Watch intelligent bots compete in real-time with stunning visual effects!

## ✨ Features

### 🧠 AI Algorithms
- **Minimax AI**: Uses alpha-beta pruning with depth-4 search tree for optimal decision making
- **Hybrid AI**: Dynamically switches between Fuzzy Logic and Minimax based on game state
- **Fuzzy Logic**: Fast, reactive decisions for close-range ball interactions
- **Auto-balancing**: Dynamic difficulty adjustment based on score differential

### 🎮 Game Features
- **60-second timed matches** with automatic winner detection
- **Real-time statistics tracking** - persistent win/loss records saved to JSON
- **Animated splash screen** and countdown before matches
- **Pause functionality** - Press `P` to pause/resume
- **Particle effects** - Dynamic trail effects and glow animations
- **Custom emoji-style bots** - Procedurally drawn robot faces

### 🎨 Visual Effects
- Neon color scheme with purple and cyan themes
- Animated grid background with moving particles
- Glowing paddles with movement trails
- Ball fire effects with color transitions
- Pulsing UI elements and smooth animations
- Progress bar showing match time remaining

## 📋 Requirements

```
Python 3.7+
pygame
```

## 🚀 Installation

1. **Clone or download the game files**

2. **Install dependencies**:
```bash
pip install pygame
```

3. **Optional audio files** (place in same directory as game):
   - `hit.wav` - Paddle hit sound
   - `score.mp3` - Score sound effect
   - `pause.wav` - Pause sound
   
   *(Game runs fine without audio files)*

## 🎮 How to Play

### Running the Game
```bash
python pong_game.py
```

### Controls
- **ENTER** - Start match / Restart after match ends
- **P** - Pause/Resume game
- **R** - Reset statistics (on start screen)
- **Q** - Quit game
- **ESC** - Skip splash screen

### Game Flow
1. **Splash Screen** - 2-second animated intro
2. **Start Screen** - Shows Bot 1 vs Bot 2 with robot avatars
3. **Countdown** - 3-2-1-GO! animation
4. **Match** - 60-second AI battle
5. **Results** - Winner announcement and statistics

## 🤖 How It Works

### Minimax Algorithm
- **Alpha-Beta Pruning**: Efficient game tree search
- **Depth-4 evaluation**: Looks 4 moves ahead
- **State evaluation**: Considers ball distance, opponent position, and center ball proximity
- **Strategic positioning**: Anticipates future ball positions

### Hybrid AI Strategy
The Hybrid AI intelligently switches strategies based on:
- **Ball proximity**: Uses Fuzzy Logic when ball is close (<250px)
- **Score pressure**: Switches to Minimax when losing
- **Time urgency**: Quick Fuzzy decisions when ball approaches fast
- **Center control**: Minimax for mid-field positioning

### Fairness Mechanisms
- **Randomized starting positions**: Bots randomly swap sides each match
- **Auto-balancing**: Losing bot gets faster reaction time (0.05s → 0.08s)
- **Equal starting conditions**: Both bots start with identical parameters

## 📊 Statistics Tracking

Match statistics are automatically saved to `ai_battle_stats.json`:
- Total matches played
- Bot 1 wins
- Bot 2 wins
- Draw count
- Win percentages

Press `R` on the start screen to reset statistics.

## 🎯 Game Mechanics

### Scoring
- Ball reaches opponent's side: +1 point
- Ball hits center obstacle: Point awarded based on last paddle hit
- Match ends after 60 seconds
- Highest score wins (or draw if tied)

### Center Obstacle
- Moving vertical ball in center of screen
- Adds strategic complexity
- Rewards precise paddle control

## 🎨 Customization

### Color Schemes
```python
NEON_PURPLE = (147, 51, 234)  # Bot 1 color
NEON_CYAN = (6, 182, 212)     # Bot 2 color
GOLD = (255, 215, 0)          # Highlights
```

### Match Duration
```python
MATCH_DURATION = 60  # Change match length in seconds
```

### AI Reaction Time
```python
left_ai_reaction = 0.05   # Lower = faster (0.05-0.08 range)
right_ai_reaction = 0.05
```

## 🏗️ Project Structure

```
pong_game.py
├── Classes
│   ├── MatchStatistics - Persistent stats tracking
│   ├── Particle - Visual effect particles
│   ├── Paddle - AI paddle with glow effects
│   └── Ball - Game ball with trails
├── AI Functions
│   ├── minimax_alpha_beta() - Minimax decision tree
│   ├── fuzzy_logic() - Fuzzy inference system
│   ├── ai_move_hybrid() - Hybrid strategy selector
│   └── enhanced_hybrid_decision() - Strategy weight calculation
├── Rendering
│   ├── draw_background() - Animated grid and particles
│   ├── draw_emoji_bot() - Robot face drawing
│   ├── draw_game_header() - HUD with timer and scores
│   └── Screen functions (splash, start, countdown, results)
└── Game Loop
    └── Main game logic with collision detection
```

## 🐛 Troubleshooting

**Game won't start?**
- Ensure Python 3.7+ is installed
- Install pygame: `pip install pygame`

**No sound?**
- Sound files are optional - game works without them
- Check audio file formats (WAV/MP3)

**Low performance?**
- Reduce particle count in `background_particles` loop
- Lower `clock.tick(60)` to 30 FPS

**Statistics not saving?**
- Check write permissions in game directory
- Delete `ai_battle_stats.json` if corrupted

## 🎓 Educational Value

This project demonstrates:
- **Game AI**: Minimax, Fuzzy Logic, Hybrid approaches
- **Algorithm optimization**: Alpha-beta pruning
- **Game development**: Pygame framework, particle systems
- **Software engineering**: Clean code structure, OOP design
- **Data persistence**: JSON statistics tracking

## 📝 License

Free to use for educational purposes. Modify and extend as desired!

## 🙏 Credits

Created as an AI algorithm comparison demonstration project.

## 🔮 Future Enhancements

Potential additions:
- [ ] Neural network AI player
- [ ] Multiplayer mode (human vs AI)
- [ ] Different difficulty levels
- [ ] Power-ups and special effects
- [ ] Tournament mode with multiple rounds
- [ ] Replay system
- [ ] Online leaderboards

---

**Enjoy watching the bots battle! 🤖⚡🤖**
