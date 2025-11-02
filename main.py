import pygame
import random
import time
import json
import os
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
HEADER_HEIGHT = 120
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('AI Battle Arena')

# Professional Color Palette
DARK_BG = (10, 10, 20)
ACCENT_BG = (15, 15, 30)
WHITE = (255, 255, 255)
NEON_PURPLE = (147, 51, 234)  # Minimax color
NEON_CYAN = (6, 182, 212)      # Hybrid color
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)
FIRE_COLORS = [(255, 100, 50), (255, 180, 80)]
GRID_COLOR = (30, 30, 50)
PARTICLE_COLORS = [(255, 100, 100), (100, 200, 255), (255, 200, 100)]

# Fonts
font = pygame.font.Font(None, 96)
score_font = pygame.font.Font(None, 120)
menu_font = pygame.font.Font(None, 64)
small_score_font = pygame.font.Font(None, 48)  # For bot scores in header

# Load bot image from bot.jpg file (optional - we use emoji bots now)
def load_bot_image():
    """Load bot image from bot.jpg file - SKIPPED, using emoji bots instead"""
    # Since we're using emoji bots now, we don't need to load bot.jpg
    # But keeping the function for potential future use
    return None

bot_image = None  # Not needed - using emoji bots

# Ball trail storage
ball_trail = []
game_logs = []

# Performance metrics
minimax_decisions = 0
fuzzy_decisions = 0
hybrid_switches = {"fuzzy": 0, "minimax": 0}

# AI role tracking
left_ai_type = "minimax"
right_ai_type = "hybrid"
left_ai_color = NEON_PURPLE
right_ai_color = NEON_CYAN
left_ai_reaction = 0.05
right_ai_reaction = 0.05

# Bot display names
bot1_color = NEON_PURPLE
bot2_color = NEON_CYAN

# ============================================
# MATCH STATISTICS TRACKING
# ============================================

class MatchStatistics:
    def __init__(self):
        self.stats_file = "ai_battle_stats.json"
        self.load_stats()
    
    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    # Support both old and new stats format
                    self.bot1_wins = data.get('bot1_wins', data.get('minimax_wins', 0))
                    self.bot2_wins = data.get('bot2_wins', data.get('hybrid_wins', 0))
                    self.draws = data.get('draws', 0)
                    self.total_matches = data.get('total_matches', 0)
            except:
                self.reset_stats()
        else:
            self.reset_stats()
    
    def reset_stats(self):
        self.bot1_wins = 0
        self.bot2_wins = 0
        self.draws = 0
        self.total_matches = 0
    
    def save_stats(self):
        data = {
            'bot1_wins': self.bot1_wins,
            'bot2_wins': self.bot2_wins,
            'draws': self.draws,
            'total_matches': self.total_matches
        }
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def record_match(self, winner):
        self.total_matches += 1
        
        if winner == "bot1":
            self.bot1_wins += 1
        elif winner == "bot2":
            self.bot2_wins += 1
        else:
            self.draws += 1
        
        self.save_stats()
    
    def get_win_rate(self, bot):
        if self.total_matches == 0:
            return 0.0
        
        if bot == "bot1":
            return (self.bot1_wins / self.total_matches) * 100
        elif bot == "bot2":
            return (self.bot2_wins / self.total_matches) * 100
        else:
            return (self.draws / self.total_matches) * 100
    
    def get_summary(self):
        if self.total_matches == 0:
            return "No matches played yet"
        
        bot1_rate = self.get_win_rate("bot1")
        bot2_rate = self.get_win_rate("bot2")
        draw_rate = self.get_win_rate("draw")
        
        return f"Total: {self.total_matches} | Bot1: {bot1_rate:.1f}% | Bot2: {bot2_rate:.1f}% | Draw: {draw_rate:.1f}%"

match_stats = MatchStatistics()

# Load sound effects
try:
    hit_sound = pygame.mixer.Sound('hit.wav')
    score_sound = pygame.mixer.Sound('score.mp3')
    pause_sound = pygame.mixer.Sound('pause.wav')
except:
    hit_sound = None
    score_sound = None
    pause_sound = None

paused = False

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = random.randint(15, 30)
        self.max_lifetime = self.lifetime
        self.size = random.uniform(2, 6)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2.5)
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.rotation = random.uniform(0, 360)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_x *= 0.98  # Friction
        self.velocity_y *= 0.98
        self.lifetime -= 1
        self.rotation += 5

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = max(0, int(255 * (self.lifetime / self.max_lifetime)))
            glow_size = int(self.size * 2)
            particle_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha // 2)
            pygame.draw.circle(particle_surface, color_with_alpha, (glow_size, glow_size), glow_size)
            surface.blit(particle_surface, (self.x - glow_size, self.y - glow_size))
            
            main_color = (*self.color, alpha)
            main_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(main_surface, main_color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(main_surface, (self.x - self.size, self.y - self.size))

class Paddle:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 24, 120)
        self.speed = 10
        self.target_y = y
        self.color = color
        self.glow_intensity = 0
        self.movement_trail = []

    def move(self, direction):
        if direction == "up" and self.rect.top > HEADER_HEIGHT:
            self.target_y -= self.speed
            self.glow_intensity = min(255, self.glow_intensity + 20)
        elif direction == "down" and self.rect.bottom < SCREEN_HEIGHT:
            self.target_y += self.speed
            self.glow_intensity = min(255, self.glow_intensity + 20)

    def update(self):
        if self.rect.centery < self.target_y:
            self.rect.y += min(self.speed, self.target_y - self.rect.centery)
        elif self.rect.centery > self.target_y:
            self.rect.y -= min(self.speed, self.rect.centery - self.target_y)
        
        # Add trail effect
        self.movement_trail.append((self.rect.centery, self.glow_intensity))
        if len(self.movement_trail) > 5:
            self.movement_trail.pop(0)
        
        # Fade glow
        self.glow_intensity = max(0, self.glow_intensity - 3)

    def draw(self):
        # Draw glow trail
        for i, (y_pos, intensity) in enumerate(self.movement_trail):
            if intensity > 0:
                glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height), pygame.SRCALPHA)
                glow_color = (*self.color, int(intensity * 0.3 * (i / len(self.movement_trail))))
                pygame.draw.rect(glow_surface, glow_color, (10, 0, self.rect.width, self.rect.height), border_radius=12)
                screen.blit(glow_surface, (self.rect.x - 10, y_pos - self.rect.height // 2))
        
        # Draw main paddle with glow
        glow_surface = pygame.Surface((self.rect.width + 16, self.rect.height + 16), pygame.SRCALPHA)
        glow_alpha = int(self.glow_intensity * 0.6)
        if glow_alpha > 0:
            glow_color = (*self.color, glow_alpha)
            pygame.draw.rect(glow_surface, glow_color, (8, 8, self.rect.width, self.rect.height), border_radius=12)
            screen.blit(glow_surface, (self.rect.x - 8, self.rect.y - 8))
        
        # Main paddle body
        pygame.draw.rect(screen, self.color, self.rect, border_radius=12)
        # Inner highlight
        highlight = tuple(min(255, c + 40) for c in self.color)
        pygame.draw.rect(screen, highlight, (self.rect.x + 4, self.rect.y + 4, self.rect.width - 8, self.rect.height - 8), border_radius=8)
    
    def clone(self):
        new_paddle = Paddle(self.rect.x, self.rect.y, self.color)
        new_paddle.target_y = self.target_y
        new_paddle.speed = self.speed
        return new_paddle

class Ball:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.speed_x = 7 * random.choice((1, -1))
        self.speed_y = 7 * random.choice((1, -1))
        self.fire_color = FIRE_COLORS[0]
        self.particles = []
        self.rotation = 0

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.rotation += math.sqrt(self.speed_x**2 + self.speed_y**2) * 2
        ball_trail.append((self.rect.copy(), self.fire_color))
        if len(ball_trail) > 15:
            ball_trail.pop(0)
        for _ in range(4):
            self.particles.append(Particle(self.rect.centerx, self.rect.centery, self.fire_color))

    def draw(self):
        # Draw trail with fade
        for i, (trail_rect, trail_color) in enumerate(ball_trail):
            alpha = int(255 * (i / len(ball_trail)) * 0.6)
            if alpha > 0:
                trail_surface = pygame.Surface((trail_rect.width + 10, trail_rect.height + 10), pygame.SRCALPHA)
                trail_color_alpha = (*trail_color, alpha // 3)
                pygame.draw.circle(trail_surface, trail_color_alpha, 
                                 (trail_rect.width // 2 + 5, trail_rect.height // 2 + 5), 
                                 (trail_rect.width // 2) + 5)
                screen.blit(trail_surface, (trail_rect.x - 5, trail_rect.y - 5))
        
        # Draw particles
        for particle in self.particles:
            particle.update()
            particle.draw(screen)
        self.particles = [p for p in self.particles if p.lifetime > 0]
        
        # Draw outer glow
        glow_surface = pygame.Surface((self.rect.width + 16, self.rect.height + 16), pygame.SRCALPHA)
        glow_color = (*self.fire_color, 100)
        pygame.draw.circle(glow_surface, glow_color, (self.rect.width // 2 + 8, self.rect.height // 2 + 8), 
                         self.rect.width // 2 + 8)
        screen.blit(glow_surface, (self.rect.x - 8, self.rect.y - 8))
        
        # Draw main ball
        pygame.draw.circle(screen, self.fire_color, self.rect.center, self.rect.width // 2)
        # Inner highlight
        highlight = tuple(min(255, int(c * 1.3)) for c in self.fire_color)
        pygame.draw.circle(screen, highlight, self.rect.center, self.rect.width // 3)
        # Core
        pygame.draw.circle(screen, WHITE, self.rect.center, self.rect.width // 6)
        
    def reset(self):
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = HEADER_HEIGHT + 20 + (SCREEN_HEIGHT - HEADER_HEIGHT) // 2
        self.speed_x = 7 * random.choice((1, -1))
        self.speed_y = 7 * random.choice((1, -1))
        ball_trail.clear()
        self.particles.clear()
        self.rotation = 0

    def toggle_fire_color(self):
        self.fire_color = FIRE_COLORS[1] if self.fire_color == FIRE_COLORS[0] else FIRE_COLORS[0]

    def move_vertical_center(self):
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y += abs(self.speed_y)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0
    
    def clone(self):
        new_ball = Ball(self.rect.x, self.rect.y)
        new_ball.speed_x = self.speed_x
        new_ball.speed_y = self.speed_y
        new_ball.fire_color = self.fire_color
        return new_ball

# Fairness functions
def randomize_ai_roles():
    if random.choice([True, False]):
        return "minimax", "hybrid", NEON_PURPLE, NEON_CYAN
    else:
        return "hybrid", "minimax", NEON_CYAN, NEON_PURPLE

def auto_balance_difficulty(left_score, right_score):
    score_diff = abs(left_score - right_score)
    if score_diff > 3:
        if left_score > right_score:
            return 0.08, 0.05
        else:
            return 0.05, 0.08
    return 0.05, 0.05

# Fuzzy logic
def fuzzy_ball_position(ball, ai_paddle):
    if ball.rect.centery < ai_paddle.rect.centery - 100:
        return "far"
    elif ball.rect.centery < ai_paddle.rect.centery - 50:
        return "mid"
    else:
        return "near"

def fuzzy_logic(ball, ai_paddle):
    global fuzzy_decisions
    fuzzy_decisions += 1
    
    ball_pos_fuzzy = fuzzy_ball_position(ball, ai_paddle)
    move_direction = "stay"

    if ball_pos_fuzzy == "near":
        move_direction = "down" if ball.rect.centery > ai_paddle.rect.centery else "up"
    elif ball_pos_fuzzy in ["mid", "far"]:
        if abs(ball.speed_y) > 5:
            move_direction = "down" if ball.rect.centery > ai_paddle.rect.centery else "up"

    return move_direction

# Minimax
def simulate_ball_movement(ball_sim, steps=1):
    for _ in range(steps):
        ball_sim.rect.x += ball_sim.speed_x
        ball_sim.rect.y += ball_sim.speed_y
        if ball_sim.rect.top <= 0 or ball_sim.rect.bottom >= SCREEN_HEIGHT:
            ball_sim.speed_y *= -1

def evaluate_state(ball, my_paddle, opponent_paddle, center_ball, is_left_paddle):
    score = 0
    my_distance = abs(ball.rect.centery - my_paddle.rect.centery)
    opponent_distance = abs(ball.rect.centery - opponent_paddle.rect.centery)
    
    score -= my_distance * 0.5
    score += opponent_distance * 0.3
    
    if center_ball:
        center_distance = abs(ball.rect.centerx - center_ball.rect.centerx)
        if center_distance < 50:
            score -= 30
    
    if is_left_paddle:
        if ball.speed_x < 0 and my_distance < 30:
            score += 20
    else:
        if ball.speed_x > 0 and my_distance < 30:
            score += 20
    
    if my_paddle.rect.top <= 10 or my_paddle.rect.bottom >= SCREEN_HEIGHT - 10:
        score -= 10
    
    return score

def minimax_alpha_beta(ball, my_paddle, opponent_paddle, center_ball, depth, alpha, beta, maximizing, is_left_paddle):
    global minimax_decisions
    
    if depth == 0:
        return evaluate_state(ball, my_paddle, opponent_paddle, center_ball, is_left_paddle), "stay"
    
    moves = ["up", "stay", "down"]
    
    if maximizing:
        max_eval = float('-inf')
        best_move = "stay"
        
        for move in moves:
            ball_sim = ball.clone()
            my_paddle_sim = my_paddle.clone()
            opponent_paddle_sim = opponent_paddle.clone()
            
            if move == "up":
                my_paddle_sim.rect.y = max(0, my_paddle_sim.rect.y - my_paddle_sim.speed)
            elif move == "down":
                my_paddle_sim.rect.y = min(SCREEN_HEIGHT - my_paddle_sim.rect.height, 
                                           my_paddle_sim.rect.y + my_paddle_sim.speed)
            
            simulate_ball_movement(ball_sim, steps=2)
            
            eval_score, _ = minimax_alpha_beta(ball_sim, my_paddle_sim, opponent_paddle_sim, 
                                               center_ball, depth - 1, alpha, beta, False, is_left_paddle)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        
        if depth == 4:
            minimax_decisions += 1
        
        return max_eval, best_move
    
    else:
        min_eval = float('inf')
        best_move = "stay"
        
        for move in moves:
            ball_sim = ball.clone()
            my_paddle_sim = my_paddle.clone()
            opponent_paddle_sim = opponent_paddle.clone()
            
            if ball_sim.rect.centery > opponent_paddle_sim.rect.centery:
                opponent_paddle_sim.rect.y = min(SCREEN_HEIGHT - opponent_paddle_sim.rect.height,
                                                 opponent_paddle_sim.rect.y + opponent_paddle_sim.speed)
            else:
                opponent_paddle_sim.rect.y = max(0, opponent_paddle_sim.rect.y - opponent_paddle_sim.speed)
            
            simulate_ball_movement(ball_sim, steps=2)
            
            eval_score, _ = minimax_alpha_beta(ball_sim, my_paddle_sim, opponent_paddle_sim,
                                               center_ball, depth - 1, alpha, beta, True, is_left_paddle)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        
        return min_eval, best_move

def ai_move_minimax(ai_paddle, ball, opponent_paddle, center_ball, is_left_paddle, reaction_time=0.05):
    if random.random() < reaction_time:
        return
    
    _, best_move = minimax_alpha_beta(
        ball, ai_paddle, opponent_paddle, center_ball,
        depth=4,
        alpha=float('-inf'),
        beta=float('inf'),
        maximizing=True,
        is_left_paddle=is_left_paddle
    )
    
    if best_move == "up":
        ai_paddle.move("up")
    elif best_move == "down":
        ai_paddle.move("down")

# Hybrid AI
def calculate_score_pressure(left_score, right_score, is_left_paddle):
    if is_left_paddle:
        return left_score - right_score
    else:
        return right_score - left_score

def enhanced_hybrid_decision(ball, ai_paddle, is_left_paddle, left_score, right_score):
    ball_approaching = (is_left_paddle and ball.speed_x < 0) or (not is_left_paddle and ball.speed_x > 0)
    distance_to_ball = abs(ball.rect.centerx - ai_paddle.rect.centerx)
    
    score_pressure = calculate_score_pressure(left_score, right_score, is_left_paddle)
    time_urgency = 1.0 - (min(distance_to_ball, 400) / 400)
    
    fuzzy_weight = 0
    minimax_weight = 0
    
    if distance_to_ball < 250 and ball_approaching:
        fuzzy_weight += 0.6
    if time_urgency > 0.7:
        fuzzy_weight += 0.3
    if score_pressure < -2:
        fuzzy_weight += 0.2
    
    if distance_to_ball > 300:
        minimax_weight += 0.5
    if score_pressure > 1:
        minimax_weight += 0.4
    if abs(ball.rect.centerx - SCREEN_WIDTH//2) < 100:
        minimax_weight += 0.3
    
    return "fuzzy" if fuzzy_weight > minimax_weight else "minimax"

def ai_move_hybrid(ai_paddle, ball, opponent_paddle, center_ball, is_left_paddle, left_score, right_score, reaction_time=0.05):
    global hybrid_switches
    
    if random.random() < reaction_time:
        return
    
    strategy = enhanced_hybrid_decision(ball, ai_paddle, is_left_paddle, left_score, right_score)
    
    if strategy == "fuzzy":
        hybrid_switches["fuzzy"] += 1
        move_direction = fuzzy_logic(ball, ai_paddle)
        
        if move_direction == "up":
            ai_paddle.move("up")
        elif move_direction == "down":
            ai_paddle.move("down")
    else:
        hybrid_switches["minimax"] += 1
        _, best_move = minimax_alpha_beta(
            ball, ai_paddle, opponent_paddle, center_ball,
            depth=4,
            alpha=float('-inf'),
            beta=float('inf'),
            maximizing=True,
            is_left_paddle=is_left_paddle
        )
        
        if best_move == "up":
            ai_paddle.move("up")
        elif best_move == "down":
            ai_paddle.move("down")

# Animated background elements
background_particles = []
for _ in range(30):
    background_particles.append({
        'x': random.randint(0, SCREEN_WIDTH),
        'y': random.randint(0, SCREEN_HEIGHT),
        'speed': random.uniform(0.2, 0.8),
        'size': random.randint(1, 3),
        'alpha': random.randint(50, 150)
    })

# Rendering
def draw_background():
    screen.fill(DARK_BG)
    
    # Animated grid pattern
    grid_offset = int(time.time() * 20) % 50
    for x in range(0, SCREEN_WIDTH + 100, 50):
        pygame.draw.line(screen, GRID_COLOR, (x - grid_offset, 0), (x - grid_offset, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT + 100, 50):
        pygame.draw.line(screen, GRID_COLOR, (0, y - grid_offset), (SCREEN_WIDTH, y - grid_offset), 1)
    
    # Center divider line with glow
    center_x = SCREEN_WIDTH // 2
    for i in range(5):
        alpha = 50 - i * 10
        divider_surface = pygame.Surface((1, SCREEN_HEIGHT), pygame.SRCALPHA)
        divider_color = (*GRID_COLOR, alpha)
        pygame.draw.line(divider_surface, divider_color, (0, 0), (0, SCREEN_HEIGHT), 1)
        screen.blit(divider_surface, (center_x - i, 0))
        screen.blit(divider_surface, (center_x + i, 0))
    
    # Animated background particles
    for particle in background_particles:
        particle['y'] += particle['speed']
        if particle['y'] > SCREEN_HEIGHT:
            particle['y'] = 0
            particle['x'] = random.randint(0, SCREEN_WIDTH)
        base_color = NEON_PURPLE if random.random() > 0.5 else NEON_CYAN
        particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
        particle_color = (*base_color, particle['alpha'])
        pygame.draw.circle(particle_surface, particle_color, (particle['size'], particle['size']), particle['size'])
        screen.blit(particle_surface, (particle['x'], particle['y']))

def draw_scores(left_score, right_score):
    # Left score with glow
    left_str = str(left_score)
    left_text = score_font.render(left_str, True, left_ai_color)
    left_width = left_text.get_width()
    for i in range(3):
        glow_intensity = 100 - i * 30
        glow_color = tuple(min(255, c + glow_intensity) for c in left_ai_color)
        left_glow = score_font.render(left_str, True, glow_color)
        screen.blit(left_glow, (SCREEN_WIDTH // 4 - left_width // 2 + i, 30 + i))
    screen.blit(left_text, (SCREEN_WIDTH // 4 - left_width // 2, 30))
    
    # Right score with glow
    right_str = str(right_score)
    right_text = score_font.render(right_str, True, right_ai_color)
    right_width = right_text.get_width()
    for i in range(3):
        glow_intensity = 100 - i * 30
        glow_color = tuple(min(255, c + glow_intensity) for c in right_ai_color)
        right_glow = score_font.render(right_str, True, glow_color)
        screen.blit(right_glow, (3 * SCREEN_WIDTH // 4 - right_width // 2 + i, 30 + i))
    screen.blit(right_text, (3 * SCREEN_WIDTH // 4 - right_width // 2, 30))

def log_event(event):
    game_logs.append(event)
    print(event)

def draw_game_header(left_score, right_score, elapsed_time, total_time):
    """Draw fixed header with robots and progress bar"""
    header_height = 120
    
    # Semi-transparent header background
    header_surface = pygame.Surface((SCREEN_WIDTH, header_height), pygame.SRCALPHA)
    header_surface.fill((*DARK_BG, 200))
    screen.blit(header_surface, (0, 0))
    
    # Bot icon size
    bot_size = 80
    
    # Draw scores at the top
    left_score_text = small_score_font.render(str(left_score), True, bot1_color)
    right_score_text = small_score_font.render(str(right_score), True, bot2_color)
    
    # Position scores at the very top (centered above bot icons)
    left_bot_center_x = 20 + bot_size // 2
    right_bot_center_x = SCREEN_WIDTH - 100 + bot_size // 2
    score_y = 5
    
    screen.blit(left_score_text, (left_bot_center_x - left_score_text.get_width() // 2, score_y))
    screen.blit(right_score_text, (right_bot_center_x - right_score_text.get_width() // 2, score_y))
    
    # Time remaining (centered at top)
    time_left = max(0, int(total_time - elapsed_time))
    time_text = font.render(f"{time_left}s", True, WHITE)
    time_y = 10
    screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, time_y))
    
    # Progress bar - smaller and centered, positioned below timer
    progress = elapsed_time / total_time
    bar_width = 300  # Smaller width
    bar_height = 8
    bar_x = (SCREEN_WIDTH - bar_width) // 2  # Centered
    bar_y = time_y + time_text.get_height() + 15  # Below the timer
    
    # Background bar
    pygame.draw.rect(screen, (50, 50, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
    
    # Progress fill with gradient effect
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        for i in range(fill_width):
            # Gradient from purple to cyan
            ratio = i / bar_width
            r = int(bot1_color[0] * (1 - ratio) + bot2_color[0] * ratio)
            g = int(bot1_color[1] * (1 - ratio) + bot2_color[1] * ratio)
            b = int(bot1_color[2] * (1 - ratio) + bot2_color[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height))
        
        # Glow on progress
        pygame.draw.rect(screen, (*WHITE, 50), (bar_x, bar_y, fill_width, bar_height), border_radius=4)
    
    # Bot images positioned below the scores
    bot_y = score_y + small_score_font.get_height() + 10  # Below the score
    draw_bot_image(20, bot_y, bot_size, bot1_color, "bot1")
    draw_bot_image(SCREEN_WIDTH - 100, bot_y, bot_size, bot2_color, "bot2")

def draw_bot_image(x, y, size, color, bot_type="bot1"):
    """Draw emoji-style bot face"""
    draw_emoji_bot(x, y, size, color, bot_type)

def draw_emoji_bot(x, y, size, color, bot_type="bot1"):
    """Draw a simple emoji-style bot face"""
    center_x = x + size // 2
    center_y = y + size // 2
    radius = size // 2 - 2
    
    # Subtle glow behind bot
    glow_surface = pygame.Surface((size + 10, size + 10), pygame.SRCALPHA)
    glow_color = (*color, 20)
    pygame.draw.circle(glow_surface, glow_color, (size // 2 + 5, size // 2 + 5), radius + 3)
    screen.blit(glow_surface, (x - 5, y - 5))
    
    # Main bot head circle (colored)
    pygame.draw.circle(screen, color, (center_x, center_y), radius)
    
    # Inner highlight circle
    highlight_radius = radius - 4
    highlight_color = tuple(min(255, c + 50) for c in color)
    pygame.draw.circle(screen, highlight_color, (center_x, center_y), highlight_radius)
    
    # Eyes - two circles
    eye_size = max(6, size // 8)
    eye_spacing = size // 3
    left_eye_x = center_x - eye_spacing // 2
    right_eye_x = center_x + eye_spacing // 2
    eye_y = center_y - size // 8
    
    # Eye whites
    pygame.draw.circle(screen, WHITE, (left_eye_x, eye_y), eye_size)
    pygame.draw.circle(screen, WHITE, (right_eye_x, eye_y), eye_size)
    
    # Eye pupils
    pupil_size = eye_size - 2
    pygame.draw.circle(screen, (0, 0, 0), (left_eye_x, eye_y), pupil_size)
    pygame.draw.circle(screen, (0, 0, 0), (right_eye_x, eye_y), pupil_size)
    
    # Mouth - happy smile (curved upward)
    mouth_y = center_y + size // 6
    mouth_width = size // 3
    mouth_height = size // 5
    # Draw a smile arc that curves upward
    # Position rect so the arc follows the top edge (creating upward curve)
    mouth_rect = pygame.Rect(center_x - mouth_width // 2, mouth_y - mouth_height // 2, mouth_width, mouth_height)
    # Arc from right (0) to left (π) along the top half of the ellipse = upward smile
    pygame.draw.arc(screen, (0, 0, 0), mouth_rect, 0, 3.14159, 3)
    
    # Optional: small antenna/top decoration
    if bot_type == "bot1":
        pygame.draw.circle(screen, color, (center_x, y + size // 8), 4)

def splash_screen():
    """Show aesthetic robot splash screen"""
    showing = True
    start_time = time.time()
    fade_duration = 2.0  # seconds
    
    while showing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                showing = False
        
        elapsed = time.time() - start_time
        
        # Background with particles
        draw_background()
        
        # Fade in animation
        alpha = min(255, int(255 * (elapsed / fade_duration)))
        
        # Draw robot
        center_x = SCREEN_WIDTH // 2 - 60
        center_y = SCREEN_HEIGHT // 2 - 50
        draw_bot_image(center_x, center_y, 120, NEON_CYAN, "bot2")
        
        # Title with fade
        title_text = menu_font.render("AI ARENA", True, WHITE)
        title_surface = pygame.Surface((title_text.get_width(), title_text.get_height()), pygame.SRCALPHA)
        title_surface.blit(title_text, (0, 0))
        title_surface.set_alpha(alpha)
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Auto-advance after fade
        if elapsed >= fade_duration:
            showing = False
        
        pygame.display.flip()
        clock.tick(60)

def start_screen():
    showing = True
    pulse_time = 0
    
    while showing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    showing = False
                elif event.key == pygame.K_r:
                    match_stats.reset_stats()
                    match_stats.save_stats()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

        draw_background()
        pulse_time += 0.1
        pulse = abs(math.sin(pulse_time))
        
        # Title with glow
        title_text = menu_font.render("BOT BATTLE", True, WHITE)
        for i in range(5):
            glow_intensity = int(100 * (1 - i/5) * pulse)
            glow_color = tuple(min(255, c + glow_intensity) for c in NEON_CYAN)
            title_glow = menu_font.render("BOT BATTLE", True, glow_color)
            screen.blit(title_glow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + i, 120 + i))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 120))
        
        # Bot names with animated colors - better spacing to avoid overlap
        bot1_text = font.render("BOT 1", True, bot1_color)
        bot2_text = font.render("BOT 2", True, bot2_color)
        vs_text = font.render("VS", True, GOLD)
        
        # Calculate positions with proper spacing
        bot1_width = bot1_text.get_width()
        vs_width = vs_text.get_width()
        bot2_width = bot2_text.get_width()
        
        center_x = SCREEN_WIDTH // 2
        spacing = 140  # Space between elements
        
        screen.blit(bot1_text, (center_x - (bot1_width + spacing + vs_width // 2), 260))
        screen.blit(vs_text, (center_x - vs_width // 2, 270))
        screen.blit(bot2_text, (center_x + (vs_width // 2 + spacing), 260))
        
        # Draw emoji bots above each bot name
        bot1_robot_x = center_x - (bot1_width + spacing + vs_width // 2) + bot1_width // 2 - 40
        bot2_robot_x = center_x + (vs_width // 2 + spacing) + bot2_width // 2 - 40
        draw_bot_image(bot1_robot_x, 180, 80, bot1_color, "bot1")
        draw_bot_image(bot2_robot_x, 180, 80, bot2_color, "bot2")
        
        # Start instruction with pulse
        start_intensity = int(150 + 105 * pulse)
        start_color = tuple(min(255, start_intensity) for _ in range(3))
        start_text = font.render("PRESS ENTER", True, start_color)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 450))

        pygame.display.flip()
        clock.tick(60)

def countdown_screen():
    """Show countdown before match starts"""
    showing = True
    start_time = time.time()
    countdown = [3, 2, 1]
    countdown_index = 0
    
    while showing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        elapsed = time.time() - start_time
        current_count = countdown[countdown_index]
        display_count = countdown[countdown_index]
        
        # Background
        draw_background()
        
        # Pulse animation
        pulse = abs(math.sin(elapsed * 6))
        
        # Countdown number with massive glow
        count_text = score_font.render(str(display_count), True, WHITE)
        
        # Draw massive glow
        for i in range(20):
            glow_intensity = int(200 * (1 - i/20) * pulse)
            glow_color = tuple(min(255, c + glow_intensity) for c in NEON_CYAN)
            glow_size = 200 + (i * 15)
            glow_text = score_font.render(str(display_count), True, glow_color)
            text_rect = glow_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            # Simulate glow by drawing multiple times offset
            for offset in [(i, 0), (-i, 0), (0, i), (0, -i), (i//2, i//2), (-i//2, -i//2)]:
                screen.blit(glow_text, (text_rect.x + offset[0], text_rect.y + offset[1]))
        
        # Main countdown
        count_text = score_font.render(str(display_count), True, WHITE)
        text_rect = count_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(count_text, text_rect)
        
        # Progress to next number
        if elapsed >= 1.0:
            countdown_index += 1
            start_time = time.time()
            if countdown_index >= len(countdown):
                showing = False
        
        pygame.display.flip()
        clock.tick(60)
    
    # Final "GO!" flash
    go_time = time.time()
    while time.time() - go_time < 0.5:
        draw_background()
        go_text = menu_font.render("GO!", True, GOLD)
        text_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(go_text, text_rect)
        pygame.display.flip()
        clock.tick(60)

def pause_game():
    global paused
    paused = True
    if pause_sound:
        pause_sound.play()
    
    pulse_time = 0
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
                    if pause_sound:
                        pause_sound.play()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        
        draw_background()
        pulse_time += 0.15
        pulse = abs(math.sin(pulse_time))
        
        # Pause text with glow
        pause_text = menu_font.render("PAUSED", True, WHITE)
        for i in range(5):
            glow_intensity = int(120 * (1 - i/5) * pulse)
            glow_color = tuple(min(255, c + glow_intensity) for c in ORANGE)
            pause_glow = menu_font.render("PAUSED", True, glow_color)
            screen.blit(pause_glow, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2 + i, 
                                     SCREEN_HEIGHT // 2 - 100 + i))
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        resume_intensity = int(150 + 105 * pulse)
        resume_color = tuple(min(255, resume_intensity) for _ in range(3))
        resume_text = font.render("P - RESUME", True, resume_color)
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
        clock.tick(60)

def reset_game_state():
    global left_ai_paddle, right_ai_paddle, ball, left_score, right_score
    global game_logs, ball_trail, last_hitter
    global minimax_decisions, fuzzy_decisions, hybrid_switches
    global left_ai_type, right_ai_type, left_ai_color, right_ai_color
    global left_ai_reaction, right_ai_reaction
    
    left_ai_type, right_ai_type, left_ai_color, right_ai_color = randomize_ai_roles()
    
    # Debug: Print which AI is on which side
    print(f"\n=== NEW MATCH ===")
    print(f"BOT 1 (Left): {left_ai_type.upper()}")
    print(f"BOT 2 (Right): {right_ai_type.upper()}")
    print("=" * 20)
    
    left_ai_paddle = Paddle(40, HEADER_HEIGHT + 20 + (SCREEN_HEIGHT - HEADER_HEIGHT) // 2 - 60, left_ai_color)
    right_ai_paddle = Paddle(SCREEN_WIDTH - 64, HEADER_HEIGHT + 20 + (SCREEN_HEIGHT - HEADER_HEIGHT) // 2 - 60, right_ai_color)
    ball = Ball(SCREEN_WIDTH // 2, HEADER_HEIGHT + 20 + (SCREEN_HEIGHT - HEADER_HEIGHT) // 2)
    
    left_score = 0
    right_score = 0
    game_logs = []
    ball_trail = []
    last_hitter = None
    minimax_decisions = 0
    fuzzy_decisions = 0
    hybrid_switches = {"fuzzy": 0, "minimax": 0}
    left_ai_reaction = 0.05
    right_ai_reaction = 0.05

def show_result_screen(left_score, right_score):
    showing = True
    
    # Determine winner
    if left_score > right_score:
        winner = "BOT 1"
        winner_color = bot1_color
        winner_algorithm = "bot1"
    elif right_score > left_score:
        winner = "BOT 2"
        winner_color = bot2_color
        winner_algorithm = "bot2"
    else:
        winner = 'DRAW'
        winner_color = GOLD
        winner_algorithm = "draw"
    
    # Record match
    match_stats.record_match(winner_algorithm)

    pulse_time = 0
    while showing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'restart'
                elif event.key == pygame.K_q:
                    return 'quit'

        draw_background()
        pulse_time += 0.12
        pulse = abs(math.sin(pulse_time))
        
        # Title
        title = menu_font.render('MATCH COMPLETE', True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Final scores with glow
        left_str = str(left_score)
        right_str = str(right_score)
        left_score_text = score_font.render(left_str, True, bot1_color)
        right_score_text = score_font.render(right_str, True, bot2_color)
        screen.blit(left_score_text, (SCREEN_WIDTH // 4 - left_score_text.get_width() // 2, 250))
        screen.blit(right_score_text, (3 * SCREEN_WIDTH // 4 - right_score_text.get_width() // 2, 250))
        
        # Robot avatars above scores
        draw_bot_image(SCREEN_WIDTH // 4 - 50, 180, 60, bot1_color, "bot1")
        draw_bot_image(3 * SCREEN_WIDTH // 4 - 50, 180, 60, bot2_color, "bot2")
        
        # Winner with pulsing glow (or draw message)
        if winner == 'DRAW':
            display_text = "IT'S A DRAW!"
        else:
            display_text = f"{winner} WINS!"
        
        winner_text = menu_font.render(display_text, True, winner_color)
        for i in range(8):
            glow_intensity = int(150 * (1 - i/8) * pulse)
            glow_color = tuple(min(255, c + glow_intensity) for c in winner_color)
            winner_glow = menu_font.render(display_text, True, glow_color)
            screen.blit(winner_glow, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2 + i, 
                                     SCREEN_HEIGHT // 2 + i))
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # Continue instruction
        cont_intensity = int(150 + 105 * pulse)
        cont_color = tuple(min(255, cont_intensity) for _ in range(3))
        cont_text = font.render("ENTER - RESTART", True, cont_color)
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, SCREEN_HEIGHT - 150))

        pygame.display.flip()
        clock.tick(60)

# Initialize clock early
clock = pygame.time.Clock()

# Main game - adjusted for header
left_ai_paddle = Paddle(40, HEADER_HEIGHT + 20 + (SCREEN_HEIGHT - HEADER_HEIGHT) // 2 - 60, left_ai_color)
right_ai_paddle = Paddle(SCREEN_WIDTH - 64, HEADER_HEIGHT + 20 + (SCREEN_HEIGHT - HEADER_HEIGHT) // 2 - 60, right_ai_color)
ball = Ball(SCREEN_WIDTH // 2, HEADER_HEIGHT + 20 + (SCREEN_HEIGHT - HEADER_HEIGHT) // 2)

left_score = 0
right_score = 0
last_hitter = None

running = True

MATCH_DURATION = 60

# Show splash screen
splash_screen()

# Show start screen
start_screen()

# Show countdown
reset_game_state()
countdown_screen()

start_time = time.time()

center_ball = Ball(SCREEN_WIDTH // 2, HEADER_HEIGHT + 20 + (SCREEN_HEIGHT - HEADER_HEIGHT) // 2)
center_ball.speed_x = 0
center_ball.speed_y = 5

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause_game()
    
    ball.move()
    if ball.rect.top <= HEADER_HEIGHT or ball.rect.bottom >= SCREEN_HEIGHT:
        ball.speed_y *= -1

    if ball.rect.colliderect(left_ai_paddle.rect):
        ball.speed_x *= -1
        ball.toggle_fire_color()
        if hit_sound:
            hit_sound.play()
        last_hitter = 'left'

    if ball.rect.colliderect(right_ai_paddle.rect):
        ball.speed_x *= -1
        ball.toggle_fire_color()
        if hit_sound:
            hit_sound.play()
        last_hitter = 'right'

    if ball.rect.colliderect(center_ball.rect):
        if last_hitter == 'left':
            right_score += 1
            if score_sound:
                score_sound.play()
            ball.reset()
        elif last_hitter == 'right':
            left_score += 1
            if score_sound:
                score_sound.play()
            ball.reset()
        else:
            ball.speed_x *= -1
            ball.speed_y *= -1
        last_hitter = None

    if ball.rect.left <= 0:
        right_score += 1
        if score_sound:
            score_sound.play()
        ball.reset()
    elif ball.rect.right >= SCREEN_WIDTH:
        left_score += 1
        if score_sound:
            score_sound.play()
        ball.reset()
    
    left_ai_reaction, right_ai_reaction = auto_balance_difficulty(left_score, right_score)
    
    if left_ai_type == "minimax":
        ai_move_minimax(left_ai_paddle, ball, right_ai_paddle, center_ball, 
                       is_left_paddle=True, reaction_time=left_ai_reaction)
    else:
        ai_move_hybrid(left_ai_paddle, ball, right_ai_paddle, center_ball, 
                      is_left_paddle=True, left_score=left_score, right_score=right_score,
                      reaction_time=left_ai_reaction)
    
    if right_ai_type == "minimax":
        ai_move_minimax(right_ai_paddle, ball, left_ai_paddle, center_ball, 
                       is_left_paddle=False, reaction_time=right_ai_reaction)
    else:
        ai_move_hybrid(right_ai_paddle, ball, left_ai_paddle, center_ball, 
                      is_left_paddle=False, left_score=left_score, right_score=right_score,
                      reaction_time=right_ai_reaction)
    
    left_ai_paddle.update()
    right_ai_paddle.update()
    
    draw_background()
    
    # Draw center ball with glow
    center_ball.move_vertical_center()
    glow_size = 20
    glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
    glow_color = (*center_ball.fire_color, 80)
    pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
    screen.blit(glow_surface, (center_ball.rect.centerx - glow_size, center_ball.rect.centery - glow_size))
    pygame.draw.circle(screen, center_ball.fire_color, center_ball.rect.center, center_ball.rect.width // 2)
    pygame.draw.circle(screen, WHITE, center_ball.rect.center, center_ball.rect.width // 4)
    
    # Draw paddles and ball
    left_ai_paddle.draw()
    right_ai_paddle.draw()
    ball.draw()
    
    # Draw header with robots and progress bar  
    elapsed = time.time() - start_time
    draw_game_header(left_score, right_score, elapsed, MATCH_DURATION)
    
    pygame.display.flip()

    clock.tick(60)

    if elapsed >= MATCH_DURATION:
        choice = show_result_screen(left_score, right_score)
        if choice == 'restart':
            start_screen()
            reset_game_state()
            countdown_screen()
            start_time = time.time()
            continue
        else:
            running = False

pygame.quit()

try:
    _ = show_result_screen(left_score, right_score)
except Exception:
    pass