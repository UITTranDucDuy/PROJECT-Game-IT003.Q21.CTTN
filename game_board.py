import random
from pathfinder import find_path

class GameBoard:
    """
    Lớp xử lý cấu trúc và logic lưu trữ bảng điểm (Board).
    """
    def __init__(self, rows, cols, num_types):
        """
        Khởi tạo bảng chơi với viền ngoài được bọc ô đệm (padding) 
        để đường đi có thể đi vòng qua bên ngoài.
        
        Args:
            rows (int): Dòng (tính tổng thể). Phải là số chẵn logic để ghép cặp.
            cols (int): Cột (tính tổng thể).
            num_types (int): Số loại biểu tượng/khối màu trong game.
        """
        self.rows = rows
        self.cols = cols
        self.num_types = num_types
        # Mảng 2 chiều chứa game data. Mặc định là -1 (hiển thị ô trống / ô đi được)
        self.grid = [[-1 for _ in range(cols)] for _ in range(rows)]
        self.generate_board()

    def generate_board(self):
        """
        Sinh ngẫu nhiên các loại khối. Lưu ý chừa hàng 0, cột 0,
        và hàng cuối, cột cuối là rìa -1 (không gian rỗng cho đường nối vòng).
        """
        # Số lượng ô thực chơi bên trong
        play_rows = self.rows - 2
        play_cols = self.cols - 2
        
        total_playable_tiles = play_rows * play_cols
        
        # Tạo danh sách các loại mảnh theo cặp
        # Mỗi loại sẽ có 2, 4, hoặc tùy chỉnh cặp mảnh
        # Đảm bảo mỗi loại icon đều xuất hiện ít nhất một cặp và phân phối đồng đều
        tiles = []
        for i in range(total_playable_tiles // 2):
            val = i % self.num_types
            tiles.extend([val, val])

        # Đảo lộn ngẫu nhiên (Shuffle)
        random.shuffle(tiles)

        # Xếp vào trong ma trận con
        idx = 0
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                self.grid[r][c] = tiles[idx]
                idx += 1

    def get_value(self, r, c):
        """Lấy giá trị tại ô. -1 là trống."""
        return self.grid[r][c]

    def remove_tiles(self, p1, p2):
        """
        Xóa 2 ô khỏi bảng (Cập nhật thành -1).
        
        Args:
            p1 (tuple): Tọa độ (r, c) ô đầu
            p2 (tuple): Tọa độ (r, c) ô thứ hai
        """
        self.grid[p1[0]][p1[1]] = -1
        self.grid[p2[0]][p2[1]] = -1

    def can_connect(self, p1, p2):
        """
        Kiểm tra hai tọa độ có thể nối với nhau hay không.
        
        Returns:
            list: Trả về path (mảng các tọa độ nối nhau) nếu có, nếu không trả về mảng rỗng [].
        """
        r1, c1 = p1
        r2, c2 = p2
        
        # Hai ô không được trùng nhau và không được là ô rỗng
        if p1 == p2:
            return []
            
        val1 = self.grid[r1][c1]
        val2 = self.grid[r2][c2]
        
        if val1 == -1 or val2 == -1:
            return []
            
        # Phải cùng loại
        if val1 != val2:
            return []
            
        # Gọi thuật toán BFS
        return find_path(self.grid, p1, p2)

    def is_game_over(self):
        """
        Kiểm tra xem không còn ô ghép nào trên màn hình.
        Returns:
            bool: True nếu thắng (tất cả là -1), ngược lại False.
        """
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.grid[r][c] != -1:
                    return False
        return True

    def check_has_move(self):
        """
        Thuật toán duyệt tìm kiếm xem trên bàn còn ít nhất 1 cặp có thể nối được hay không.
        Đây là tính năng năng cao giúp tự động Shuffle bài nếu không còn nước đi, 
        tạm thời giữ ở MVP trả về True (để dành nâng cấp).
        """
        # (Chức năng nâng cao - sẽ phát triển sau nếu cần)
        return True

    def find_hint(self):
        """
        Tìm kiếm 1 cặp ô hợp lệ trên bàn cờ.
        Returns:
            tuple: (p1, p2) nếu tìm thấy cặp hợp lệ, ngược lại return None.
        """
        from collections import defaultdict
        positions_by_val = defaultdict(list)
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                val = self.grid[r][c]
                if val != -1:
                    positions_by_val[val].append((r, c))
                    
        for val, positions in positions_by_val.items():
            n = len(positions)
            for i in range(n):
                for j in range(i + 1, n):
                    p1 = positions[i]
                    p2 = positions[j]
                    path = self.can_connect(p1, p2)
                    if len(path) > 0:
                        return (p1, p2)
        return None

    def shuffle_hard_mode(self):
        """
        Trộn bảng cho Hard Mode:
        1. Tìm 1 cặp đang có thể nối được (nếu có).
        2. Cố định vị trí cặp đó.
        3. Trộn ngẫu nhiên (chỉ giá trị) của tất cả các ô trên bàn còn lại.
        4. Nếu lúc bắt đầu không tìm được cặp nào, thì trộn toàn bộ đến khi có cặp.
        """
        # 1. Tìm 1 cặp thỏa mãn
        valid_pair = self.find_hint()
        
        fixed_positions = []
        if valid_pair:
            fixed_positions = [valid_pair[0], valid_pair[1]]
        
        # 2. Lấy tất cả các ô không phải -1 và không nằm trong fixed_positions
        tiles_to_shuffle_positions = []
        tiles_values = []
        
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.grid[r][c] != -1 and (r, c) not in fixed_positions:
                    tiles_to_shuffle_positions.append((r, c))
                    tiles_values.append(self.grid[r][c])
                    
        # 3. Trộn values
        import random
        random.shuffle(tiles_values)
        
        # 4. Gán lại vào board
        for i, (r, c) in enumerate(tiles_to_shuffle_positions):
            self.grid[r][c] = tiles_values[i]
            
        # Nếu ban đầu không có valid_pair, ta phải lặp trộn đến khi tìm ra 1 cặp
        if not valid_pair:
            while not self.find_hint():
                random.shuffle(tiles_values)
                for i, (r, c) in enumerate(tiles_to_shuffle_positions):
                    self.grid[r][c] = tiles_values[i]
