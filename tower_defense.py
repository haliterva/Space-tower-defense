import pygame
import math
import random

# Pygame'i başlat
pygame.init()

# Sabitler
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Uzay Teması Renk Paleti
BG_COLOR = (5, 5, 20)
STAR_COLOR = (200, 200, 255)
NEBULA_COLORS = [(80, 20, 120), (20, 80, 150), (120, 20, 80)]

# Enerji Yolu Renkleri
PATH_COLOR = (0, 150, 255)
PATH_GLOW = (100, 200, 255)
PATH_CORE = (200, 230, 255)

# UI Renkleri
PANEL_BG = (10, 10, 40)
PANEL_ACCENT = (30, 30, 80)
TEXT_PRIMARY = (200, 220, 255)
TEXT_SECONDARY = (140, 160, 200)

# Uzay Gemisi (Düşman) Renkleri
ENEMY_COLOR = (220, 50, 50)
ENEMY_GLOW = (255, 100, 100)
ENEMY_ENGINE = (255, 150, 0)
HEALTH_GREEN = (50, 255, 150)
HEALTH_RED = (255, 50, 80)

# Uzay İstasyonu (Kule) Renkleri
BASIC_COLOR = (50, 150, 255)
BASIC_LIGHT = (150, 200, 255)
BASIC_LASER = (100, 180, 255)
FAST_COLOR = (255, 180, 50)
FAST_LIGHT = (255, 220, 150)
FAST_LASER = (255, 200, 100)
HEAVY_COLOR = (180, 50, 255)
HEAVY_LIGHT = (220, 150, 255)
HEAVY_LASER = (200, 100, 255)

# Efekt Renkleri
GLOW_COLOR = (100, 200, 255)
PARTICLE_COLORS = [(100, 200, 255), (255, 150, 80), (150, 255, 200), (255, 100, 200)]
EXPLOSION_COLORS = [(255, 200, 100), (255, 100, 50), (255, 50, 150)]

# Oyun penceresi
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Uzay Tower Defense")
clock = pygame.time.Clock()
is_fullscreen = False

# Font
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 26)
title_font = pygame.font.Font(None, 48)
large_font = pygame.font.Font(None, 64)

# Yol koordinatları
path = [
    (0, 200),
    (300, 200),
    (300, 400),
    (600, 400),
    (600, 100),
    (900, 100),
    (900, 500),
    (SCREEN_WIDTH, 500)
]

def draw_rounded_rect(surface, color, rect, radius=10):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_glow_circle(surface, color, pos, radius, glow_radius=5):
    for i in range(glow_radius):
        alpha = int(50 * (1 - i / glow_radius))
        glow_color = (*color[:3], alpha)
        glow_surface = pygame.Surface((radius * 2 + i * 2, radius * 2 + i * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (radius + i, radius + i), radius + i)
        surface.blit(glow_surface, (pos[0] - radius - i, pos[1] - radius - i))
    pygame.draw.circle(surface, color, pos, radius)

class Particle:
    def __init__(self, x, y, color, particle_type="normal"):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.color = color
        self.life = 30
        self.max_life = 30
        self.size = random.randint(2, 5)
        self.particle_type = particle_type
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.particle_type == "explosion":
            self.vx *= 0.95
            self.vy *= 0.95
        else:
            self.vy += 0.05
    
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        size = int(self.size * (self.life / self.max_life))
        if size > 0:
            particle_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            glow_alpha = alpha // 3
            pygame.draw.circle(particle_surface, (*self.color[:3], glow_alpha), (size * 2, size * 2), size * 2)
            color_with_alpha = (*self.color[:3], alpha)
            pygame.draw.circle(particle_surface, color_with_alpha, (size * 2, size * 2), size)
            surface.blit(particle_surface, (int(self.x - size * 2), int(self.y - size * 2)))

class Enemy:
    def __init__(self, health, speed, reward):
        self.health = health
        self.max_health = health
        self.speed = speed
        self.reward = reward
        self.path_index = 0
        self.x = path[0][0]
        self.y = path[0][1]
        self.radius = 15
        self.angle = 0
        
    def move(self):
        if self.path_index < len(path) - 1:
            target_x, target_y = path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.speed:
                self.path_index += 1
                if self.path_index >= len(path) - 1:
                    return True
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        return False
    
    def draw(self):
        self.angle += 5
        pos = (int(self.x), int(self.y))
        
        # Motor ateşi
        engine_x = pos[0] - 12
        engine_y = pos[1]
        for i in range(3):
            flame_size = 8 - i * 2
            flame_alpha = 150 - i * 50
            flame_surf = pygame.Surface((flame_size * 2, flame_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flame_surf, (*ENEMY_ENGINE[:3], flame_alpha), (flame_size, flame_size), flame_size)
            screen.blit(flame_surf, (engine_x - flame_size - i * 3, engine_y - flame_size))
        
        # Gemi parlama efekti
        glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        for i in range(3):
            alpha = int(40 * (1 - i / 3))
            glow_col = (*ENEMY_GLOW[:3], alpha)
            pygame.draw.circle(glow_surface, glow_col, (self.radius * 2, self.radius * 2), self.radius + i * 4)
        screen.blit(glow_surface, (pos[0] - self.radius * 2, pos[1] - self.radius * 2))
        
        # Gemi gövdesi
        ship_points = [
            (pos[0] + 15, pos[1]),
            (pos[0] - 10, pos[1] - 10),
            (pos[0] - 10, pos[1] + 10)
        ]
        pygame.draw.polygon(screen, ENEMY_COLOR, ship_points)
        pygame.draw.polygon(screen, ENEMY_GLOW, ship_points, 2)
        
        pygame.draw.circle(screen, ENEMY_GLOW, pos, 5)
        pygame.draw.circle(screen, (255, 200, 200), pos, 3)
        
        # Can çubuğu
        bar_width = 40
        bar_height = 5
        health_ratio = max(0, self.health / self.max_health)
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 25
        
        bg_rect = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_rect, (0, 0, 0, 120), (0, 0, bar_width, bar_height), border_radius=2)
        screen.blit(bg_rect, (bar_x, bar_y))
        
        if health_ratio > 0:
            health_color = HEALTH_GREEN if health_ratio > 0.5 else HEALTH_RED
            health_width = int((bar_width - 2) * health_ratio)
            draw_rounded_rect(screen, health_color, (bar_x + 1, bar_y + 1, health_width, bar_height - 2), 2)

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        self.level = 1
        
        if tower_type == "basic":
            self.damage = 15
            self.range = 120
            self.fire_rate = 40
            self.color = BASIC_COLOR
            self.light_color = BASIC_LIGHT
            self.cost = 50
        elif tower_type == "fast":
            self.damage = 9
            self.range = 95
            self.fire_rate = 20
            self.color = FAST_COLOR
            self.light_color = FAST_LIGHT
            self.cost = 100
        elif tower_type == "heavy":
            self.damage = 50
            self.range = 150
            self.fire_rate = 60
            self.color = HEAVY_COLOR
            self.light_color = HEAVY_LIGHT
            self.cost = 200
        
        self.cooldown = 0
        self.target = None
        self.shoot_animation = 0
        
    def find_target(self, enemies):
        for enemy in enemies:
            distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if distance <= self.range:
                return enemy
        return None
    
    def shoot(self, enemies):
        if self.cooldown <= 0:
            target = self.find_target(enemies)
            if target:
                self.target = target
                target.health -= self.damage
                self.cooldown = self.fire_rate
                self.shoot_animation = 10
                return True
        else:
            self.cooldown -= 1
        
        if self.shoot_animation > 0:
            self.shoot_animation -= 1
        
        return False
    
    def draw(self):
        tower_size = 32
        
        # Taban platformu
        base_points = []
        for i in range(6):
            angle = math.pi / 3 * i
            bx = self.x + math.cos(angle) * (tower_size // 2 + 4)
            by = self.y + math.sin(angle) * (tower_size // 2 + 4)
            base_points.append((bx, by))
        
        pygame.draw.polygon(screen, self.color, base_points)
        pygame.draw.polygon(screen, self.light_color, base_points, 3)
        
        # Enerji çekirdeği
        core_radius = tower_size // 3
        for i in range(3):
            glow_radius = core_radius + i * 4
            alpha = int(80 * (1 - i / 3))
            glow_surf = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.light_color[:3], alpha), (glow_radius * 2, glow_radius * 2), glow_radius)
            screen.blit(glow_surf, (self.x - glow_radius * 2, self.y - glow_radius * 2))
        
        pygame.draw.circle(screen, self.color, (self.x, self.y), core_radius)
        pygame.draw.circle(screen, self.light_color, (self.x, self.y), core_radius - 3)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), core_radius - 6)
        
        # Dönen enerji halkası
        ring_radius = core_radius + 6
        for i in range(4):
            angle = (pygame.time.get_ticks() / 500 + i * math.pi / 2) % (2 * math.pi)
            rx = self.x + math.cos(angle) * ring_radius
            ry = self.y + math.sin(angle) * ring_radius
            pygame.draw.circle(screen, self.light_color, (int(rx), int(ry)), 3)
        
        # Lazer ışını
        if self.target and self.shoot_animation > 5:
            laser_color = BASIC_LASER if self.type == "basic" else (FAST_LASER if self.type == "fast" else HEAVY_LASER)
            
            for thickness in range(4, 0, -1):
                alpha = int(255 * (self.shoot_animation / 10) * (thickness / 4))
                line_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                glow_color = (*laser_color[:3], alpha)
                pygame.draw.line(line_surface, glow_color, (self.x, self.y), 
                               (int(self.target.x), int(self.target.y)), thickness * 3)
                screen.blit(line_surface, (0, 0))
            
            pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), 
                           (int(self.target.x), int(self.target.y)), 2)

class Game:
    def __init__(self):
        self.money = 250
        self.lives = 15
        self.wave = 0
        self.enemies = []
        self.towers = []
        self.particles = []
        self.selected_tower_type = None
        self.game_over = False
        self.enemy_spawn_timer = 0
        self.enemies_to_spawn = 0
        self.wave_in_progress = False
        self.game_speed = 1
        self.background_stars = [(random.randint(0, SCREEN_WIDTH), 
                                  random.randint(0, SCREEN_HEIGHT), 
                                  random.randint(1, 3),
                                  random.choice([STAR_COLOR, (150, 150, 255), (255, 200, 200)]),
                                  random.randint(180, 255)) for _ in range(200)]
        self.nebula_particles = [(random.randint(0, SCREEN_WIDTH),
                                  random.randint(0, SCREEN_HEIGHT),
                                  random.randint(30, 80),
                                  random.choice(NEBULA_COLORS)) for _ in range(15)]
        
    def start_wave(self):
        if not self.wave_in_progress:
            self.wave += 1
            self.enemies_to_spawn = 6 + self.wave * 4
            self.wave_in_progress = True

    def spawn_enemy(self):
        if self.enemies_to_spawn > 0 and self.enemy_spawn_timer <= 0:
            # ÜSTEL güçlenme 
            health = 50 + (self.wave ** 1.6) * 18        
            speed = 1.0 + min(self.wave * 0.10, 1.8)     
            reward = 8 + self.wave * 2                   
            
            self.enemies.append(Enemy(health, speed, reward))
            self.enemies_to_spawn -= 1
            self.enemy_spawn_timer = 50
        else:
            self.enemy_spawn_timer -= 1
    
    def update(self):
        if self.game_over:
            return
        
        for _ in range(self.game_speed):
            if self.wave_in_progress:
                self.spawn_enemy()
            
            for enemy in self.enemies[:]:
                reached_end = enemy.move()
                if reached_end:
                    self.lives -= 1
                    self.enemies.remove(enemy)
                    if self.lives <= 0:
                        self.game_over = True
                elif enemy.health <= 0:
                    self.money = min(300, self.money + enemy.reward)
                    self.enemies.remove(enemy)
            
            if self.wave_in_progress and self.enemies_to_spawn == 0 and len(self.enemies) == 0:
                self.wave_in_progress = False
            
            # Kuleler hız çarpanına göre ateş etsin
            for tower in self.towers:
                if tower.shoot(self.enemies):
                    for _ in range(8):
                        color = random.choice(PARTICLE_COLORS)
                        self.particles.append(Particle(tower.x, tower.y, color))
                    if tower.target:
                        for _ in range(10):
                            exp_color = random.choice(EXPLOSION_COLORS)
                            self.particles.append(Particle(tower.target.x, tower.target.y, exp_color, "explosion"))
        
        # Partikül limiti - maksimum 150 partikül
        if len(self.particles) > 150:
            self.particles = self.particles[-150:]
        
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw(self):
        screen.fill(BG_COLOR)
        
        # Yıldızlar
        for star_x, star_y, star_size, star_color, alpha in self.background_stars:
            star_surface = pygame.Surface((star_size * 4, star_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, (*star_color[:3], alpha // 3), 
                             (star_size * 2, star_size * 2), star_size * 2)
            pygame.draw.circle(star_surface, (*star_color[:3], alpha), 
                             (star_size * 2, star_size * 2), star_size)
            screen.blit(star_surface, (star_x - star_size * 2, star_y - star_size * 2))
        
        # Enerji yolu 
        time_offset = pygame.time.get_ticks() / 200
        for i in range(len(path) - 1):
            # Glow efekti 
            pygame.draw.line(screen, (*PATH_GLOW[:3],), path[i], path[i+1], 22)
            pygame.draw.line(screen, PATH_COLOR, path[i], path[i+1], 14)
            pygame.draw.line(screen, PATH_CORE, path[i], path[i+1], 7)
            
            path_length = math.sqrt((path[i+1][0] - path[i][0])**2 + (path[i+1][1] - path[i][1])**2)
            num_particles = int(path_length / 100)  # 80 yerine 100
            for j in range(num_particles):
                t = ((j + time_offset) % num_particles) / num_particles
                px = path[i][0] + (path[i+1][0] - path[i][0]) * t
                py = path[i][1] + (path[i+1][1] - path[i][1]) * t
                # Basit circle çiz, surface oluşturma
                pygame.draw.circle(screen, PATH_CORE, (int(px), int(py)), 3)
                pygame.draw.circle(screen, (255, 255, 255), (int(px), int(py)), 2)
        
        for tower in self.towers:
            tower.draw()
        
        for enemy in self.enemies:
            enemy.draw()
        
        for particle in self.particles:
            particle.draw(screen)
        
        self.draw_ui()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_ui(self):
        # Üst panel
        panel_surface = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*PANEL_BG, 230), (0, 0, SCREEN_WIDTH, 60))
        screen.blit(panel_surface, (0, 0))
        
        card_width = 140
        card_height = 40
        card_y = 10
        
        # Para
        money_rect = (15, card_y, card_width, card_height)
        draw_rounded_rect(screen, PANEL_ACCENT, money_rect, 8)
        pygame.draw.circle(screen, FAST_LIGHT, (35, card_y + 20), 8)
        pygame.draw.circle(screen, FAST_COLOR, (35, card_y + 20), 5)
        money_text = small_font.render(f"${self.money}", True, FAST_LIGHT)
        screen.blit(money_text, (50, card_y + 10))
        
        # Can
        lives_rect = (170, card_y, card_width, card_height)
        draw_rounded_rect(screen, PANEL_ACCENT, lives_rect, 8)
        shield_points = [(190, card_y + 12), (195, card_y + 8), (200, card_y + 12), (200, card_y + 28), (195, card_y + 32), (190, card_y + 28)]
        pygame.draw.polygon(screen, ENEMY_COLOR, shield_points)
        lives_text = small_font.render(f"{self.lives}", True, ENEMY_COLOR)
        screen.blit(lives_text, (210, card_y + 10))
        
        # Dalga
        wave_rect = (325, card_y, card_width, card_height)
        draw_rounded_rect(screen, PANEL_ACCENT, wave_rect, 8)
        for wave_line in range(3):
            pygame.draw.line(screen, TEXT_PRIMARY, (340, card_y + 14 + wave_line * 6), (355, card_y + 14 + wave_line * 6), 2)
        wave_text = small_font.render(f"Dalga {self.wave}", True, TEXT_PRIMARY)
        screen.blit(wave_text, (360, card_y + 10))
        
        # Hız butonları
        speed_button_y = 10
        speed_button_width = 70
        speed_button_height = 40
        speed_button_gap = 10
        
        # 2x
        speed_2x_x = SCREEN_WIDTH - 360
        speed_2x_color = FAST_LIGHT if self.game_speed == 2 else PANEL_ACCENT
        draw_rounded_rect(screen, speed_2x_color, (speed_2x_x, speed_button_y, speed_button_width, speed_button_height), 10)
        if self.game_speed == 2:
            glow_surf = pygame.Surface((speed_button_width + 6, speed_button_height + 6), pygame.SRCALPHA)
            draw_rounded_rect(glow_surf, (*FAST_LIGHT[:3], 80), (3, 3, speed_button_width, speed_button_height), 10)
            screen.blit(glow_surf, (speed_2x_x - 3, speed_button_y - 3))
        speed_2x_text = small_font.render("2x", True, TEXT_PRIMARY)
        text_rect = speed_2x_text.get_rect(center=(speed_2x_x + speed_button_width//2, speed_button_y + speed_button_height//2))
        screen.blit(speed_2x_text, text_rect)
        
        # 3x
        speed_3x_x = speed_2x_x + speed_button_width + speed_button_gap
        speed_3x_color = HEAVY_LIGHT if self.game_speed == 3 else PANEL_ACCENT
        draw_rounded_rect(screen, speed_3x_color, (speed_3x_x, speed_button_y, speed_button_width, speed_button_height), 10)
        if self.game_speed == 3:
            glow_surf = pygame.Surface((speed_button_width + 6, speed_button_height + 6), pygame.SRCALPHA)
            draw_rounded_rect(glow_surf, (*HEAVY_LIGHT[:3], 80), (3, 3, speed_button_width, speed_button_height), 10)
            screen.blit(glow_surf, (speed_3x_x - 3, speed_button_y - 3))
        speed_3x_text = small_font.render("3x", True, TEXT_PRIMARY)
        text_rect = speed_3x_text.get_rect(center=(speed_3x_x + speed_button_width//2, speed_button_y + speed_button_height//2))
        screen.blit(speed_3x_text, text_rect)
        
        # Dalga başlat butonu
        button_x = SCREEN_WIDTH - 200
        button_y = 10
        button_width = 195
        button_height = 40
        
        if not self.wave_in_progress:
            draw_rounded_rect(screen, HEALTH_GREEN, (button_x, button_y, button_width, button_height), 10)
            glow_surf = pygame.Surface((button_width + 10, button_height + 10), pygame.SRCALPHA)
            draw_rounded_rect(glow_surf, (50, 255, 150, 60), (5, 5, button_width, button_height), 10)
            screen.blit(glow_surf, (button_x - 5, button_y - 5))
            play_points = [(button_x + 20, button_y + 12), (button_x + 20, button_y + 28), (button_x + 32, button_y + 20)]
            pygame.draw.polygon(screen, (10, 10, 30), play_points)
            button_text = small_font.render("Sonraki Dalga", True, (10, 10, 30))
            screen.blit(button_text, (button_x + 40, button_y + 10))
        else:
            draw_rounded_rect(screen, PANEL_ACCENT, (button_x, button_y, button_width, button_height), 10)
            angle = (pygame.time.get_ticks() / 5) % 360
            for i in range(3):
                a = math.radians(angle + i * 120)
                cx = button_x + 25 + math.cos(a) * 8
                cy = button_y + 20 + math.sin(a) * 8
                pygame.draw.circle(screen, TEXT_SECONDARY, (int(cx), int(cy)), 3)
            button_text = small_font.render("Devam ediyor...", True, TEXT_SECONDARY)
            screen.blit(button_text, (button_x + 40, button_y + 10))
        
        # Alt panel
        panel_surface = pygame.Surface((SCREEN_WIDTH, 110), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*PANEL_BG, 240), (0, 0, SCREEN_WIDTH, 110))
        screen.blit(panel_surface, (0, SCREEN_HEIGHT - 110))
        
        title_text = small_font.render("KULE SECIMI", True, TEXT_PRIMARY)
        screen.blit(title_text, (20, SCREEN_HEIGHT - 100))
        
        towers_info = [
            ("basic", "Savunma ", "$50", BASIC_COLOR, BASIC_LIGHT, 240),
            ("fast", "Hızlı Ateş ", "$100", FAST_COLOR, FAST_LIGHT, 460),
            ("heavy", "Ağır ", "$200", HEAVY_COLOR, HEAVY_LIGHT, 680)
        ]
        
        for tower_type, name, cost, color, light_color, x_pos in towers_info:
            card_y = SCREEN_HEIGHT - 90
            card_width = 200  # 170'ten 200'e artırıldı (uzun isimler için)
            card_height = 75
            
            if self.selected_tower_type == tower_type:
                glow_rect = (x_pos - 5, card_y - 5, card_width + 10, card_height + 10)
                draw_rounded_rect(screen, light_color, glow_rect, 12)
            
            card_rect = (x_pos, card_y, card_width, card_height)
            draw_rounded_rect(screen, PANEL_ACCENT, card_rect, 10)
            
            icon_size = 40
            icon_x = x_pos + 15
            icon_y = card_y + 17
            draw_rounded_rect(screen, color, (icon_x, icon_y, icon_size, icon_size), 8)
            draw_rounded_rect(screen, light_color, (icon_x, icon_y, icon_size, icon_size // 2), 8)
            
            name_text = small_font.render(name, True, TEXT_PRIMARY)
            cost_text = small_font.render(cost, True, FAST_LIGHT)
            screen.blit(name_text, (icon_x + icon_size + 10, card_y + 15))
            screen.blit(cost_text, (icon_x + icon_size + 10, card_y + 40))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (10, 15, 25, 200), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(overlay, (0, 0))
        
        card_width = 500
        card_height = 300
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = (SCREEN_HEIGHT - card_height) // 2
        
        shadow = pygame.Surface((card_width + 20, card_height + 20), pygame.SRCALPHA)
        draw_rounded_rect(shadow, (0, 0, 0, 100), (10, 10, card_width, card_height), 20)
        screen.blit(shadow, (card_x - 10, card_y - 10))
        
        draw_rounded_rect(screen, PANEL_BG, (card_x, card_y, card_width, card_height), 20)
        
        game_over_text = large_font.render("OYUN BITTI!", True, ENEMY_COLOR)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, card_y + 70))
        screen.blit(game_over_text, text_rect)
        
        wave_label = title_font.render("Son Dalga:", True, TEXT_SECONDARY)
        text_rect = wave_label.get_rect(center=(SCREEN_WIDTH // 2, card_y + 130))
        screen.blit(wave_label, text_rect)
        
        wave_num = large_font.render(f"{self.wave}", True, FAST_LIGHT)
        text_rect = wave_num.get_rect(center=(SCREEN_WIDTH // 2, card_y + 170))
        screen.blit(wave_num, text_rect)
        
        button_width = 320
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = card_y + 220
        
        draw_rounded_rect(screen, HEALTH_GREEN, (button_x, button_y, button_width, button_height), 12)
        center_x = button_x + 30
        center_y = button_y + 25
        pygame.draw.circle(screen, (10, 10, 30), (center_x, center_y), 10, 3)
        arrow_points = [(center_x + 8, center_y - 8), (center_x + 12, center_y - 4), (center_x + 8, center_y)]
        pygame.draw.polygon(screen, (10, 10, 30), arrow_points)
        restart_text = font.render("Yeniden Basla (R)", True, (10, 10, 30))
        screen.blit(restart_text, (button_x + 55, button_y + 12))
    
    def place_tower(self, x, y):
        if self.selected_tower_type and not self.wave_in_progress:
            tower = Tower(x, y, self.selected_tower_type)
            if self.money >= tower.cost:
                on_path = False
                for i in range(len(path) - 1):
                    if self.point_to_line_distance(x, y, path[i], path[i+1]) < 30:
                        on_path = True
                        break
                
                too_close = False
                for existing_tower in self.towers:
                    if math.sqrt((existing_tower.x - x)**2 + (existing_tower.y - y)**2) < 40:
                        too_close = True
                        break
                
                if not on_path and not too_close and y > 50 and y < SCREEN_HEIGHT - 110:
                    self.money -= tower.cost
                    self.towers.append(tower)
    
    def point_to_line_distance(self, px, py, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        line_mag = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_mag < 0.00000001:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_mag ** 2)
        u = max(0, min(1, u))
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        return math.sqrt((px - ix)**2 + (py - iy)**2)

def main():
    global screen, is_fullscreen
    game = Game()
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # 2x Hız butonu
                if (SCREEN_WIDTH - 360 < mouse_x < SCREEN_WIDTH - 290 and 
                    10 < mouse_y < 50):
                    game.game_speed = 2 if game.game_speed != 2 else 1
                
                # 3x Hız butonu
                elif (SCREEN_WIDTH - 280 < mouse_x < SCREEN_WIDTH - 210 and 
                    10 < mouse_y < 50):
                    game.game_speed = 3 if game.game_speed != 3 else 1
                
                # Dalga başlat
                elif (SCREEN_WIDTH - 200 < mouse_x < SCREEN_WIDTH - 10 and 
                    10 < mouse_y < 45 and not game.wave_in_progress):
                    game.start_wave()
                
                # Kule seçimi
                elif SCREEN_HEIGHT - 110 < mouse_y < SCREEN_HEIGHT:
                    if 280 < mouse_x < 450:
                        game.selected_tower_type = "basic"
                    elif 480 < mouse_x < 650:
                        game.selected_tower_type = "fast"
                    elif 680 < mouse_x < 850:
                        game.selected_tower_type = "heavy"
                
                # Kule yerleştir
                else:
                    game.place_tower(mouse_x, mouse_y)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game = Game()
                elif event.key == pygame.K_F11:
                    # Tam ekran toggle
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                elif event.key == pygame.K_ESCAPE and is_fullscreen:
                    # ESC ile tam ekrandan çık
                    is_fullscreen = False
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        game.update()
        game.draw()
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()