"""
=====================================================
2048 Game Engine - TwentyRL Arena Project
=====================================================
Lead Developer: Game logic implementation
Software Project Management & Technical Monitoring
=====================================================
"""

import numpy as np
import random


class Game2048:
    """
    2048 Oyun Engine
    - 4x4 grid
    - Tile'lar yukarı/aşağı/sol/sağ kaydırılır
    - Aynı sayılı tile'lar birleşir
    - Hedef: 2048 tile'a ulaşmak
    """

    def __init__(self, size=4):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.score = 0
        self.game_over = False
        self.won = False
        self.moves_count = 0
        self._add_new_tile()
        self._add_new_tile()

    def _add_new_tile(self):
        """Boş hücreye yeni tile ekler (%90 ihtimalle 2, %10 ihtimalle 4)"""
        empty_cells = [(i, j) for i in range(self.size)
                       for j in range(self.size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def _compress(self, row):
        """Row'daki sıfırları sağa iter, dolu olanları sola toplar"""
        new_row = [num for num in row if num != 0]
        new_row += [0] * (self.size - len(new_row))
        return new_row

    def _merge(self, row):
        """Bitişik aynı tile'ları birleştirir"""
        for i in range(self.size - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                self.score += row[i]
                row[i + 1] = 0
                if row[i] == 2048:
                    self.won = True
        return row

    def move_left(self):
        """Sol kaydırma"""
        changed = False
        for i in range(self.size):
            original = self.board[i].copy()
            compressed = self._compress(self.board[i].tolist())
            merged = self._merge(compressed)
            final = self._compress(merged)
            self.board[i] = final
            if not np.array_equal(original, self.board[i]):
                changed = True
        return changed

    def move_right(self):
        """Sağ kaydırma - board'ı flip edip left yapıyoruz"""
        self.board = np.fliplr(self.board)
        changed = self.move_left()
        self.board = np.fliplr(self.board)
        return changed

    def move_up(self):
        """Yukarı kaydırma - transpose edip left yapıyoruz"""
        self.board = self.board.T
        changed = self.move_left()
        self.board = self.board.T
        return changed

    def move_down(self):
        """Aşağı kaydırma - transpose + flip edip left yapıyoruz"""
        self.board = self.board.T
        self.board = np.fliplr(self.board)
        changed = self.move_left()
        self.board = np.fliplr(self.board)
        self.board = self.board.T
        return changed

    def make_move(self, action):
        """
        action: 0=up, 1=down, 2=left, 3=right
        Returns: (changed, score_gained, game_over)
        """
        score_before = self.score
        moves = {0: self.move_up, 1: self.move_down,
                 2: self.move_left, 3: self.move_right}

        changed = moves[action]()
        score_gained = self.score - score_before

        if changed:
            self._add_new_tile()
            self.moves_count += 1

        if self._is_game_over():
            self.game_over = True

        return changed, score_gained, self.game_over

    def _is_game_over(self):
        """Oyun bitti mi kontrol eder"""
        if np.any(self.board == 0):
            return False

        # Hala birleştirilebilecek tile var mı?
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.board[i][j] == self.board[i][j + 1]:
                    return False
                if self.board[j][i] == self.board[j + 1][i]:
                    return False
        return True

    def get_state(self):
        """Board state'ini RL agent için döndürür"""
        return self.board.copy()

    def get_max_tile(self):
        """En yüksek tile değerini döndürür"""
        return int(np.max(self.board))

    def reset(self):
        """Oyunu sıfırlar"""
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.score = 0
        self.game_over = False
        self.won = False
        self.moves_count = 0
        self._add_new_tile()
        self._add_new_tile()
        return self.get_state()

    def display(self):
        """Board'u terminalde gösterir"""
        print("-" * 25)
        for row in self.board:
            print("|", end="")
            for val in row:
                if val == 0:
                    print("     |", end="")
                else:
                    print(f" {val:4d}|", end="")
            print()
            print("-" * 25)
        print(f"Score: {self.score} | Moves: {self.moves_count} | Max Tile: {self.get_max_tile()}")


if __name__ == "__main__":
    # Quick test
    game = Game2048()
    game.display()
    print("\nMoving left...")
    game.make_move(2)
    game.display()
