import collections

def find_path(board, p1, p2):
    """
    Sử dụng thuật toán BFS (Tìm kiếm theo chiều rộng) để tìm đường đi ngắn nhất
    giữa hai điểm p1 và p2 trên lưới board.
    Đường đi hợp lệ không được xoay quá 2 lần (tối đa 3 đoạn thẳng).
    
    Args:
        board (list of list of int): Mảng 2 chiều biểu diễn trạng thái game. 
                                     Giá trị -1 nghĩa là ô trống.
        p1 (tuple): Tọa độ (row, col) của điểm bắt đầu.
        p2 (tuple): Tọa độ (row, col) của điểm kết thúc.

    Returns:
        list of tuple: Danh sách các tọa độ (row, col) tạo thành đường đi từ p1 tới p2.
                       Nếu không có đường đi hợp lệ, trả về mảng rỗng [].
    """
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0
    
    # Lịch sử đã duyệt. Do trạng thái bao gồm cả tọa độ và hướng đi đến tọa độ đó,
    # chúng ta lưu visited như sau: visited[(r, c, direction)] = số lần xoay tối thiểu
    visited = {}
    
    # Hàng đợi cho BFS: [ ((row, col), direction, turns, path) ]
    # direction: 0: Lên, 1: Nằm ngang phải, 2: Xuống, 3: Trái. Ban đầu -1 chưa có hướng.
    queue = collections.deque()
    queue.append((p1, -1, 0, [p1]))
    visited[(p1[0], p1[1], -1)] = 0
    
    # 4 hướng đi: (dr, dc)
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    
    while queue:
        (r, c), cur_dir, turns, path = queue.popleft()
        
        # Nếu đã tới đích và thỏa mãn số lần xoay
        if (r, c) == p2:
            return path
            
        # Thử đi theo 4 hướng
        for i, (dr, dc) in enumerate(directions):
            nr, nc = r + dr, c + dc
            
            # Kiểm tra xem có đi ra ngoài biên không.
            # Lưu ý trong trò chơi này, ta có một lớp "viền nilon" (row 0, col 0, row max-1, col max-1)
            # luôn rỗng nên đường nối có thể đi vòng qua.
            if 0 <= nr < rows and 0 <= nc < cols:
                # Tính số lần xoay (turns) mới
                new_turns = turns
                if cur_dir != -1 and cur_dir != i:
                    new_turns += 1
                
                # Cắt tỉa nhánh: nếu xoay quá 2 lần thì đường đi này bị loại
                if new_turns > 2:
                    continue
                
                # Chỉ được đi vào ô trống HOẶC là ô mục tiêu (p2)
                if board[nr][nc] == -1 or (nr, nc) == p2:
                    # Ràng buộc visited để không đi vào vòng lặp
                    # Nếu có đường nào đến ô (nr, nc) theo hướng `i` mà có số lần turn ít hơn hoặc bằng
                    # so với việc đã từng đến thì ta duyệt tiếp. Dấu <= rất quan trọng.
                    if (nr, nc, i) not in visited or visited[(nr, nc, i)] > new_turns:
                        visited[(nr, nc, i)] = new_turns
                        new_path = list(path)
                        new_path.append((nr, nc))
                        queue.append(((nr, nc), i, new_turns, new_path))
                        
    # Trả về rỗng nếu không tìm thấy đường đi hợp lệ
    return []
