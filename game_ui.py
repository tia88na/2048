"""
=====================================================
Game UI - Interactive 2048 Game with RL Agent
=====================================================
UX/UI Designer + Lead Developer: Game Interface
Software Project Management & Technical Monitoring
=====================================================

Bu UI'da:
- Manual play (oyuncu kendi oynar)
- RL agent play (agent otomatik oynar)
- Hibrit mode (agent öneri verir)

Çalıştırmak için: pip install pygame
"""

import pygame
import sys
import time
from game_2048 import Game2048
from rl_agent import QLearningAgent

# Renk paleti (2048 resmi renkleri)
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50),
}

TEXT_COLORS = {
    2: (119, 110, 101),
    4: (119, 110, 101),
}

BG_COLOR = (187, 173, 160)
SCREEN_BG = (250, 248, 239)

# UI ayarları
CELL_SIZE = 100
CELL_PADDING = 10
GRID_SIZE = 4
BOARD_WIDTH = CELL_SIZE * GRID_SIZE + CELL_PADDING * (GRID_SIZE + 1)
WINDOW_WIDTH = BOARD_WIDTH + 40
WINDOW_HEIGHT = BOARD_WIDTH + 200


class Game2048UI:
    def __init__(self, agent_path=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("TwentyRL Arena - 2048 with RL")
        self.clock = pygame.time.Clock()

        self.game = Game2048()
        self.agent = QLearningAgent()
        if agent_path:
            try:
                self.agent.load_model(agent_path)
                print(f"Agent loaded from {agent_path}")
            except Exception as e:
                print(f"Could not load agent: {e}")

        self.agent.epsilon = 0  # Pure exploitation

        # Modes
        self.mode = "MANUAL"  # MANUAL, AUTO, HYBRID
        self.auto_delay = 0.2  # seconds between auto moves
        self.last_auto_move = 0

        # Fonts
        self.font_large = pygame.font.SysFont('Arial', 40, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 16)

    def draw_tile(self, value, x, y):
        """Tek tile çizer"""
        color = TILE_COLORS.get(value, (60, 58, 50))
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect, border_radius=6)

        if value != 0:
            text_color = TEXT_COLORS.get(value, (249, 246, 242))
            font_size = 40 if value < 100 else (32 if value < 1000 else 24)
            font = pygame.font.SysFont('Arial', font_size, bold=True)
            text = font.render(str(value), True, text_color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def draw_board(self):
        """Oyun tahtasını çizer"""
        board_x = 20
        board_y = 100

        # Board background
        board_rect = pygame.Rect(board_x, board_y, BOARD_WIDTH, BOARD_WIDTH)
        pygame.draw.rect(self.screen, BG_COLOR, board_rect, border_radius=8)

        # Tiles
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = board_x + CELL_PADDING + j * (CELL_SIZE + CELL_PADDING)
                y = board_y + CELL_PADDING + i * (CELL_SIZE + CELL_PADDING)
                self.draw_tile(self.game.board[i][j], x, y)

    def draw_header(self):
        """Score ve mod gösterir"""
        # Title
        title = self.font_large.render("2048", True, (119, 110, 101))
        self.screen.blit(title, (20, 20))

        # Score box
        score_text = self.font_medium.render(f"Score: {self.game.score}",
                                             True, (255, 255, 255))
        score_bg = pygame.Rect(WINDOW_WIDTH - 220, 20, 200, 50)
        pygame.draw.rect(self.screen, BG_COLOR, score_bg, border_radius=4)
        self.screen.blit(score_text,
                         (WINDOW_WIDTH - 200, 32))

        # Mode indicator
        mode_color = {"MANUAL": (100, 150, 100),
                      "AUTO": (150, 100, 100),
                      "HYBRID": (100, 100, 150)}
        mode_text = self.font_small.render(f"Mode: {self.mode}",
                                           True, mode_color[self.mode])
        self.screen.blit(mode_text, (20, 65))

        # Max tile
        max_tile_text = self.font_small.render(
            f"Max Tile: {self.game.get_max_tile()}",
            True, (119, 110, 101))
        self.screen.blit(max_tile_text, (150, 65))

    def draw_footer(self):
        """Alt kısımda controls gösterir"""
        y = WINDOW_HEIGHT - 80

        instructions = [
            "Controls:",
            "Arrows = Move | M = Manual | A = Auto (RL Agent) | R = Reset | Q = Quit"
        ]

        for i, text in enumerate(instructions):
            rendered = self.font_small.render(text, True, (119, 110, 101))
            self.screen.blit(rendered, (20, y + i * 20))

        # Game over banner
        if self.game.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT),
                                     pygame.SRCALPHA)
            overlay.fill((238, 228, 218, 180))
            self.screen.blit(overlay, (0, 0))

            end_text = self.font_large.render("GAME OVER!", True, (119, 110, 101))
            text_rect = end_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
            self.screen.blit(end_text, text_rect)

            restart_text = self.font_medium.render("Press R to restart",
                                                   True, (119, 110, 101))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2,
                                                        WINDOW_HEIGHT // 2 + 30))
            self.screen.blit(restart_text, restart_rect)

    def handle_input(self, event):
        """Klavye girdilerini işler"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                return False
            elif event.key == pygame.K_r:
                self.game.reset()
            elif event.key == pygame.K_m:
                self.mode = "MANUAL"
            elif event.key == pygame.K_a:
                self.mode = "AUTO"
            elif event.key == pygame.K_h:
                self.mode = "HYBRID"
            elif self.mode == "MANUAL" and not self.game.game_over:
                action_map = {
                    pygame.K_UP: 0,
                    pygame.K_DOWN: 1,
                    pygame.K_LEFT: 2,
                    pygame.K_RIGHT: 3
                }
                if event.key in action_map:
                    self.game.make_move(action_map[event.key])
        return True

    def auto_play_step(self):
        """RL agent otomatik hamle yapıyor - invalid move handling ile"""
        current_time = time.time()
        if (current_time - self.last_auto_move) > self.auto_delay:
            if not self.game.game_over:
                state = self.game.get_state()
                action = self.agent.choose_action(state)
                changed, _, _ = self.game.make_move(action)

                # Invalid move handling: agent geçersiz hamle seçtiyse alternatif dene
                if not changed:
                    for alt_action in [0, 1, 2, 3]:
                        if alt_action != action:
                            changed, _, _ = self.game.make_move(alt_action)
                            if changed:
                                break
                    # Hiçbir hareket yapılamadıysa game over
                    if not changed:
                        self.game.game_over = True

                self.last_auto_move = current_time

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    running = self.handle_input(event)

            # Auto mode check
            if self.mode == "AUTO":
                self.auto_play_step()

            # Draw everything
            self.screen.fill(SCREEN_BG)
            self.draw_header()
            self.draw_board()
            self.draw_footer()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    ui = Game2048UI(agent_path='agent_final.pkl')
    ui.run()
