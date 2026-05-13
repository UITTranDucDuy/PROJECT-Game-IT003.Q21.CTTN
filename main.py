import pygame
import sys
import time
import os
from constants import *
from game_board import GameBoard

# Khởi tạo pygame
pygame.init()
pygame.display.set_caption("GAME PIKACHU (Animal Connect) - Python Edition")

# Tạo font dạng cơ bản (System Font) vì chưa tải Unicode Fonts
font_large = pygame.font.SysFont('arial', 48, bold=True)
font_medium = pygame.font.SysFont('arial', 32)
font_small = pygame.font.SysFont('arial', 20)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.best_records = self.load_records()
        
        # Load sounds
        pygame.mixer.init()
        self.sound_click = None
        self.sound_connect = None
        self.sound_wrong = None
        self.sound_win = None
        ASSETS_DIR = "assets"
        
        try:
            self.sound_click = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "click.wav"))
            self.sound_connect = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "connect.wav"))
            self.sound_wrong = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "wrong.wav"))
            self.sound_win = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "win.wav"))
        except:
            pass
            
        # Load background music
        bgm_paths = [os.path.join(ASSETS_DIR, "bgm.mp3"),
                     os.path.join(ASSETS_DIR, "bgm.ogg"),
                     os.path.join(ASSETS_DIR, "bgm.wav")]
        for p in bgm_paths:
            if os.path.exists(p):
                try:
                    pygame.mixer.music.load(p)
                    pygame.mixer.music.set_volume(0.3) # Giảm âm lượng nhạc nền xuống 30% để chill
                    pygame.mixer.music.play(-1) # -1 để loop vô hạn
                    break
                except Exception as e:
                    print("Lỗi tải nhạc nền:", e)
        
        # Load hình ảnh icon
        self.icon_images = []

        os.makedirs(ASSETS_DIR, exist_ok=True)
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
        image_files = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith(valid_extensions)]
        for i in range(NUM_TYPES):
            if i < len(image_files):
                try:
                    path = os.path.join(ASSETS_DIR, image_files[i])
                    # Xử lý convert_alpha an toàn sau khi đã khởi tạo display
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (TILE_SIZE - 4, TILE_SIZE - 4))
                    self.icon_images.append(img)
                except Exception as e:
                    print(f"Lỗi tải hình {path}:", e)
                    self.icon_images.append(None)
            else:
                self.icon_images.append(None)
        
        self.state = "MENU"
        
        # Load background images
        self.menu_bg = None
        self.play_bg = None
        menu_bg_path = os.path.join(ASSETS_DIR, "menu_bg.jpg")
        play_bg_path = os.path.join(ASSETS_DIR, "play_bg.jpg")
        
        if os.path.exists(menu_bg_path):
            try:
                bg = pygame.image.load(menu_bg_path).convert()
                self.menu_bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            except:
                pass
                
        if os.path.exists(play_bg_path):
            try:
                bg = pygame.image.load(play_bg_path).convert()
                self.play_bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            except:
                pass
        
        btn_width, btn_height = 200, 60
        self.easy_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, HEIGHT // 2 - 80, btn_width, btn_height)
        self.hard_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, HEIGHT // 2, btn_width, btn_height)
        self.insane_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, HEIGHT // 2 + 80, btn_width, btn_height)
        
        # State trò chơi (Khởi tạo sau khi nhấn start)
        self.board = None
        self.selected_tile = None  # Ô đầu tiên được click t.c (row, col)
        
        # Biến đếm thời gian
        self.start_time = 0
        self.time_elapsed = 0
        
        # Điểm số
        self.score = 0
        
        # Hiệu ứng nối Line (mất đi sau 0.5s)
        self.connecting_line = [] # Chứa tọa độ line [(r,c), (r,c)...]
        self.line_timer = 0
        
        # Trạng thái WIN / LOSE
        self.game_over = False
        self.win = False
        
        # Hint config
        self.hint_button_rect = pygame.Rect(WIDTH // 2 - 110, 10, 100, 40)
        self.hint_tiles = []
        self.hint_timer = 0
        
        # Pause config
        self.pause_button_rect = pygame.Rect(WIDTH // 2 + 10, 10, 100, 40)
        self.pause_time_start = 0
        
        # Exit config
        self.exit_button_rect = pygame.Rect(WIDTH - 120, 10, 100, 40)

    def load_records(self):
        try:
            with open("records.json", "r") as f:
                import json
                return json.load(f)
        except:
            return {"EASY": float('inf'), "HARD": float('inf'), "INSANE": float('inf')}

    def save_record(self, mode, time_val):
        self.best_records[mode] = time_val
        try:
            with open("records.json", "w") as f:
                import json
                json.dump(self.best_records, f)
        except:
            pass

    def start_game(self, mode="EASY"):
        self.mode = mode
        self.board = GameBoard(ROWS, COLS, NUM_TYPES)
        self.start_time = time.time()
        self.time_elapsed = 0
        self.score = 0
        self.selected_tile = None
        self.game_over = False
        self.win = False
        self.connecting_line = []
        self.line_timer = 0
        self.hint_tiles = []
        self.hint_timer = 0
        self.wrong_tiles = []
        self.wrong_pair_timer = 0
        self.correct_tiles = []
        self.state = "PLAYING"

    def handle_menu_click(self, pos):
        if self.easy_btn.collidepoint(pos):
            if self.sound_click: self.sound_click.play()
            self.start_game(mode="EASY")
        elif self.hard_btn.collidepoint(pos):
            if self.sound_click: self.sound_click.play()
            self.start_game(mode="HARD")
        elif hasattr(self, 'insane_btn') and self.insane_btn.collidepoint(pos):
            if self.sound_click: self.sound_click.play()
            self.start_game(mode="INSANE")

    def draw_menu(self):
        if hasattr(self, 'menu_bg') and self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill(LIGHT_BLUE)
        
        # Hàm vẽ nút có bóng đổ (shadow) và viền
        def draw_styled_button(rect, bg_color, text_str, text_color=WHITE):
            # Bóng đổ
            shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
            pygame.draw.rect(self.screen, (20, 20, 20), shadow_rect, border_radius=12)
            
            # Nút chính
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=12)
            
            # Viền ngoài sáng màu
            pygame.draw.rect(self.screen, WHITE, rect, width=2, border_radius=12)
            
            # Chữ có viền nhẹ (viền đen mờ)
            text_bg = font_medium.render(text_str, True, BLACK)
            text_surf = font_medium.render(text_str, True, text_color)
            tw, th = text_surf.get_size()
            
            # Vẽ bóng của chữ để dễ đọc trên nền sáng
            tx = rect.x + (rect.width - tw) // 2
            ty = rect.y + (rect.height - th) // 2
            self.screen.blit(text_bg, (tx + 2, ty + 2))
            self.screen.blit(text_surf, (tx, ty))

        # Mức Easy
        draw_styled_button(self.easy_btn, GREEN, "EASY")

        # Mức Hard
        draw_styled_button(self.hard_btn, RED, "HARD")

        # Mức Insane
        if hasattr(self, 'insane_btn'):
            draw_styled_button(self.insane_btn, PURPLE, "INSANE")

        pygame.display.flip()

    def get_cell_from_mouse(self, pos):
        """
        Đổi tạo độ màn hình -> chỉ số row, col trên lưới.
        Trả về (row, col) hoặc None nếu click ra ngoài rìa.
        """
        x, y = pos
        col = (x - MARGIN_X) // TILE_SIZE
        row = (y - MARGIN_Y) // TILE_SIZE
        if 0 <= row < ROWS and 0 <= col < COLS:
            return (row, col)
        return None

    def handle_click(self, pos):
        """Xử lý sự kiện khi người dùng click trái chuột."""
        # Kiểm tra nút Exit (có thể ấn bất cứ lúc nào khi đang chơi hoặc game over)
        if hasattr(self, 'exit_button_rect') and self.exit_button_rect.collidepoint(pos):
            if self.sound_click: self.sound_click.play()
            self.state = "MENU"
            return
            
        # Ngừng nhận click nếu game over, đang chạy hiệu ứng nối, hoặc đang chờ ẩn cặp sai
        if self.game_over or self.line_timer > 0 or getattr(self, 'wrong_pair_timer', 0) > 0:
            return
            
        # Kiểm tra nút Pause
        if hasattr(self, 'pause_button_rect') and self.pause_button_rect.collidepoint(pos):
            if self.sound_click: self.sound_click.play()
            self.state = "PAUSED"
            self.pause_time_start = time.time()
            return
            
        # Kiểm tra click vào nút Hint
        if hasattr(self, 'hint_button_rect') and self.hint_button_rect.collidepoint(pos):
            if self.sound_click: self.sound_click.play()
            hint_result = self.board.find_hint()
            if hint_result:
                self.hint_tiles = list(hint_result)
                self.hint_timer = pygame.time.get_ticks()
            return
            
        cell = self.get_cell_from_mouse(pos)
        if not cell:
            self.selected_tile = None
            return
            
        r, c = cell
        
        # Nếu click vào ô trống -> bỏ chọn
        if self.board.grid[r][c] == -1:
            self.selected_tile = None
            return
            
        if self.selected_tile is None:
            # Chọn ô đầu tiên
            if self.sound_click: self.sound_click.play()
            self.selected_tile = cell
        else:
            # Click ô thứ 2, là chính ô đó -> Mất chọn
            if self.selected_tile == cell:
                if self.sound_click: self.sound_click.play()
                self.selected_tile = None
            else:
                # Kiểm tra kết nối 2 ô
                valid_path = self.board.can_connect(self.selected_tile, cell)
                
                if len(valid_path) > 0: # Cặp hợp lệ
                    if self.sound_connect: self.sound_connect.play()
                    self.score += 100
                    
                    # Vẽ hiệu ứng line
                    self.connecting_line = valid_path
                    self.line_timer = pygame.time.get_ticks()
                    self.correct_tiles = [self.selected_tile, cell]
                    
                    self.selected_tile = None
                        
                else: # Chọn sai -> Chọn lại
                    if self.sound_wrong: self.sound_wrong.play()
                    if getattr(self, 'mode', 'EASY') == "INSANE":
                        self.wrong_tiles = [self.selected_tile, cell]
                        self.wrong_pair_timer = pygame.time.get_ticks()
                        self.selected_tile = None
                    else:
                        self.selected_tile = cell
                
    def draw(self):
        """Vẽ toàn bộ khung hình"""
        if hasattr(self, 'play_bg') and self.play_bg:
            self.screen.blit(self.play_bg, (0, 0))
        else:
            self.screen.fill(WHITE)

        # Thanh UI phía trên
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WIDTH, MARGIN_Y))
        
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        time_text = font_medium.render(f"Time: {int(self.time_elapsed)}s", True, WHITE)
        
        self.screen.blit(score_text, (20, 10))
        self.screen.blit(time_text, (WIDTH - 250, 10))

        # Nút HINT
        if hasattr(self, 'hint_button_rect'):
            pygame.draw.rect(self.screen, YELLOW, self.hint_button_rect, border_radius=5)
            hint_text = font_small.render("HINT", True, BLACK)
            hw, hh = hint_text.get_size()
            text_x = self.hint_button_rect.x + (self.hint_button_rect.width - hw) // 2
            text_y = self.hint_button_rect.y + (self.hint_button_rect.height - hh) // 2
            self.screen.blit(hint_text, (text_x, text_y))

        # Nút PAUSE
        if hasattr(self, 'pause_button_rect'):
            pygame.draw.rect(self.screen, ORANGE, self.pause_button_rect, border_radius=5)
            pause_text = font_small.render("PAUSE", True, BLACK)
            pw, ph = pause_text.get_size()
            text_x = self.pause_button_rect.x + (self.pause_button_rect.width - pw) // 2
            text_y = self.pause_button_rect.y + (self.pause_button_rect.height - ph) // 2
            self.screen.blit(pause_text, (text_x, text_y))

        # Nút EXIT
        if hasattr(self, 'exit_button_rect'):
            pygame.draw.rect(self.screen, RED, self.exit_button_rect, border_radius=5)
            exit_text = font_small.render("EXIT", True, WHITE)
            ew, eh = exit_text.get_size()
            text_x = self.exit_button_rect.x + (self.exit_button_rect.width - ew) // 2
            text_y = self.exit_button_rect.y + (self.exit_button_rect.height - eh) // 2
            self.screen.blit(exit_text, (text_x, text_y))

        # Hiển thị từng Tile trên bảng
        for r in range(ROWS):
            for c in range(COLS):
                val = self.board.grid[r][c]
                x = MARGIN_X + c * TILE_SIZE
                y = MARGIN_Y + r * TILE_SIZE
                
                # Ô trống thì chỉ hiện khung hoặc trong suốt (Bỏ hiển thị rìa)
                if val == -1:
                    continue
                
                is_revealed = True
                if getattr(self, 'mode', 'EASY') == "INSANE":
                    if self.selected_tile != (r, c) and \
                       (r, c) not in getattr(self, 'wrong_tiles', []) and \
                       (r, c) not in getattr(self, 'hint_tiles', []) and \
                       (r, c) not in getattr(self, 'correct_tiles', []):
                        is_revealed = False

                if is_revealed:
                    # Vẽ hộp Màu hoặc Hình ảnh ứng với type (Pikachu Icons)
                    if val < len(self.icon_images) and self.icon_images[val] is not None:
                        self.screen.blit(self.icon_images[val], (x + 2, y + 2))
                    else:
                        color = COLORS_MAP[val % len(COLORS_MAP)]
                        rect = (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                        pygame.draw.rect(self.screen, color, rect, border_radius=8)
                        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=8)
                        
                        # Vẽ chữ cái lên khối đại diện cho loại quái (Cho Animal)
                        text_char = chr(65 + val) # Từ A,B,C...
                        text = font_medium.render(text_char, True, WHITE)
                        tw, th = text.get_size()
                        self.screen.blit(text, (x + (TILE_SIZE - tw) // 2, y + (TILE_SIZE - th) // 2))
                else:
                    # Chế độ Insane: Ẩn hình ảnh, chỉ vẽ một khối xám với dấu ?
                    rect = (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                    pygame.draw.rect(self.screen, GRAY, rect, border_radius=8)
                    pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=8)
                    question_text = font_medium.render("?", True, BLACK)
                    qw, qh = question_text.get_size()
                    self.screen.blit(question_text, (x + (TILE_SIZE - qw) // 2, y + (TILE_SIZE - qh) // 2))
                
                # Highlights ô đang được click đầu tiên
                if self.selected_tile == (r, c):
                    pygame.draw.rect(self.screen, RED, (x, y, TILE_SIZE, TILE_SIZE), 3)
                    
                # Vẽ viền Hint
                if getattr(self, 'hint_tiles', None) and (r, c) in self.hint_tiles:
                    pygame.draw.rect(self.screen, RED, (x, y, TILE_SIZE, TILE_SIZE), 5)

        # Vẽ đường kết nối trong khoảng 0.3 giây
        if self.line_timer > 0 and len(self.connecting_line) > 1:
            points = []
            for (r, c) in self.connecting_line:
                # Centers of the cells
                px = MARGIN_X + c * TILE_SIZE + TILE_SIZE // 2
                py = MARGIN_Y + r * TILE_SIZE + TILE_SIZE // 2
                points.append((px, py))
            pygame.draw.lines(self.screen, RED, False, points, 5)

        # Hiển thị kết thúc
        if self.game_over:
            if self.win:
                mode_str = getattr(self, 'mode', 'EASY')
                current_time = int(self.time_elapsed)
                best_time = self.best_records.get(mode_str, float('inf'))
                if current_time <= best_time:
                    msg = f"NEW RECORD: {current_time}s!"
                else:
                    msg = f"YOU WIN! Time: {current_time}s"
            else:
                msg = "GAME OVER!"
                
            color = GREEN if self.win else RED
            over_text = font_large.render(msg, True, color)
            tw, th = over_text.get_size()
            
            # Vẽ hộp bọc để dễ đọc
            bg_rect = pygame.Rect(WIDTH//2 - tw//2 - 20, HEIGHT//2 - th//2 - 20, tw + 40, th + 40)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            self.screen.blit(over_text, (WIDTH//2 - tw//2, HEIGHT//2 - th//2))

        # Hiển thị lúc PAUSE
        if getattr(self, 'state', '') == "PAUSED":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_title = font_large.render("PAUSED", True, WHITE)
            tw, th = pause_title.get_size()
            self.screen.blit(pause_title, (WIDTH // 2 - tw // 2, HEIGHT // 2 - th // 2))
            
            # Vẽ lại nút Resume
            if hasattr(self, 'pause_button_rect'):
                pygame.draw.rect(self.screen, GREEN, self.pause_button_rect, border_radius=5)
                resume_text = font_small.render("RESUME", True, BLACK)
                rw, rh = resume_text.get_size()
                text_x = self.pause_button_rect.x + (self.pause_button_rect.width - rw) // 2
                text_y = self.pause_button_rect.y + (self.pause_button_rect.height - rh) // 2
                self.screen.blit(resume_text, (text_x, text_y))

            # Vẽ lại nút Exit trên overlay
            if hasattr(self, 'exit_button_rect'):
                pygame.draw.rect(self.screen, RED, self.exit_button_rect, border_radius=5)
                exit_text = font_small.render("EXIT", True, WHITE)
                ew, eh = exit_text.get_size()
                text_x = self.exit_button_rect.x + (self.exit_button_rect.width - ew) // 2
                text_y = self.exit_button_rect.y + (self.exit_button_rect.height - eh) // 2
                self.screen.blit(exit_text, (text_x, text_y))

        pygame.display.flip()

    def update(self):
        """Cập nhật logic thời gian"""
        if self.game_over:
            return
            
        self.time_elapsed = time.time() - self.start_time

        # Ẩn đường line kết nối sau 300ms
        if self.line_timer > 0 and pygame.time.get_ticks() - self.line_timer > 300:
            if hasattr(self, 'correct_tiles') and len(self.correct_tiles) == 2:
                # Trì hoãn việc xóa tile để người chơi kịp nhìn thấy cặp đúng
                self.board.remove_tiles(self.correct_tiles[0], self.correct_tiles[1])
                
                # Cập nhật win nếu không còn block
                if self.board.is_game_over():
                    self.win = True
                    self.game_over = True
                    if getattr(self, 'sound_win', None): self.sound_win.play()
                    mode_str = getattr(self, 'mode', 'EASY')
                    if self.time_elapsed < self.best_records.get(mode_str, float('inf')):
                        self.save_record(mode_str, self.time_elapsed)
                else:
                    if getattr(self, 'mode', 'EASY') == "HARD":
                        self.board.shuffle_hard_mode()
                    elif not self.board.find_hint():
                        # Nếu không còn nước đi hợp lệ nào trên bảng, tự động xáo trộn
                        self.board.shuffle_hard_mode()
                self.correct_tiles = []

            self.line_timer = 0
            self.connecting_line = []
            
        # Ẩn viền Hint sau 1 giây
        if getattr(self, 'hint_timer', 0) > 0 and pygame.time.get_ticks() - self.hint_timer > 1000:
            self.hint_timer = 0
            self.hint_tiles = []

        # Ẩn cặp sai sau 0.5 giây trong chế độ Insane
        if getattr(self, 'wrong_pair_timer', 0) > 0 and pygame.time.get_ticks() - self.wrong_pair_timer > 500:
            self.wrong_pair_timer = 0
            self.wrong_tiles = []

    def run(self):
        """Khởi động Game Loop"""
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    
                # Nhấn chuột hoặc Touch màn hình
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "MENU":
                        self.handle_menu_click(event.pos)
                    elif self.state == "PLAYING":
                        self.handle_click(event.pos)
                    elif self.state == "PAUSED":
                        if hasattr(self, 'pause_button_rect') and self.pause_button_rect.collidepoint(event.pos):
                            self.state = "PLAYING"
                            # Bù lại thời gian đã dừng
                            self.start_time += (time.time() - self.pause_time_start)
                        elif hasattr(self, 'exit_button_rect') and self.exit_button_rect.collidepoint(event.pos):
                            self.state = "MENU"
                        
            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "PLAYING" or self.state == "PAUSED":
                if self.state == "PLAYING":
                    self.update() # Chỉ đếm thời gian gạch nối / line khi đang chơi
                self.draw()
            
            # Khóa tốc độ ở 60 khung hình/giây
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
