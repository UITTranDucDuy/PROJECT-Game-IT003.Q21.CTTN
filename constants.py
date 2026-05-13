# constants.py
# Định nghĩa các hằng số dùng chung trong toàn bộ game
import pygame

# Kích thước khung hình
WIDTH = 800
HEIGHT = 600
FPS = 60

# Cấu hình Lưới chơi (Grid)
# Số hàng ngang và dọc
ROWS = 10
COLS = 16

# Tính toán kích thước ô dựa vào màn hình
TILE_SIZE = min(WIDTH // COLS, HEIGHT // ROWS)

# Chỉnh bảng chơi vào giữa để đẹp hơn
MARGIN_X = (WIDTH - (COLS * TILE_SIZE)) // 2
MARGIN_Y = (HEIGHT - (ROWS * TILE_SIZE)) // 2

# Màu sắc RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)

# Bảng màu tương ứng cho 26 loại icon chữ cái/số
COLORS_MAP = [
    RED, GREEN, YELLOW, ORANGE, PURPLE, 
    CYAN, MAGENTA, PINK, BROWN, BLUE,
    (50, 205, 50), (255, 105, 180), (123, 104, 238), (30, 144, 255), (218, 165, 32)
]

# Loại các loại icon
NUM_TYPES = 20

# Thời gian chơi (giây)
GAME_TIME = 300
