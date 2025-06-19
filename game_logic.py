import csv
import random
# === Block Class ===
class Block:
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return str(self.value) if self.value is not None else ""

    def is_empty(self):
        return self.value is None

# === Position Class ===
class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

# === GameBoard Class ===
class GameBoard:
    SIZE = 6

    def __init__(self):
        self.board = [[Block(None) for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.score = 0
        self.random_count = 0
        self.errors = 0
        self.elapsed_time = 0
        self.mode_name = "standard"

    def get_value(self, row, col):
        return self.board[row][col].value

    def clear_positions(self, pos1, pos2):
        self.board[pos1.row][pos1.col].value = None
        self.board[pos2.row][pos2.col].value = None

    def refill_empty(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.board[i][j].is_empty():
                    self.board[i][j].value = random.randint(1, 9)

    def is_match(self, pos1, pos2):
        val1 = self.get_value(pos1.row, pos1.col)
        val2 = self.get_value(pos2.row, pos2.col)

        if val1 is None or val2 is None:
            return False

        if not self.are_positions_connectable(pos1, pos2):
            return False

        return val1 == val2 or val1 + val2 == 10

    def are_positions_connectable(self, pos1, pos2):
        row_diff = pos2.row - pos1.row
        col_diff = pos2.col - pos1.col

        if row_diff == 0:
            step = 1 if col_diff > 0 else -1
            for c in range(pos1.col + step, pos2.col, step):
                if self.board[pos1.row][c].value is not None:
                    return False
            return True

        if col_diff == 0:
            step = 1 if row_diff > 0 else -1
            for r in range(pos1.row + step, pos2.row, step):
                if self.board[r][pos1.col].value is not None:
                    return False
            return True

        if abs(row_diff) == abs(col_diff):
            step_r = 1 if row_diff > 0 else -1
            step_c = 1 if col_diff > 0 else -1
            r, c = pos1.row + step_r, pos1.col + step_c
            while r != pos2.row and c != pos2.col:
                if self.board[r][c].value is not None:
                    return False
                r += step_r
                c += step_c
            return True

        return False

    def save_to_file(self, filename="board.csv"):
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                # Zapis planszy
                for row in self.board:
                    writer.writerow([block.value if block.value is not None else "" for block in row])
                writer.writerow([])

                # Zapis stanu gry
                writer.writerow(["mode", self.mode_name])
                writer.writerow(["score", self.score])
                writer.writerow(["random_count", self.random_count])
                writer.writerow(["errors", self.errors])
                writer.writerow(["elapsed_time", self.elapsed_time])

                # Zapis moves_left tylko dla trybu challenge
                if self.mode_name == "challenge":
                    writer.writerow(["moves_left", self.moves_left])
        except Exception as e:
            print("Error saving file:", e)

    def load_from_file(self, filename="board.csv"):
        try:
            with open(filename, "r") as f:
                reader = csv.reader(f)
                rows = list(reader)

            for i in range(self.SIZE):
                for j in range(self.SIZE):
                    val = rows[i][j]
                    self.board[i][j].value = int(val) if val else None

            for row in rows[self.SIZE + 1:]:
                if row and row[0] == "mode":
                    self.mode_name = row[1]
                elif row and row[0] == "score":
                    self.score = int(row[1])
                elif row and row[0] == "random_count":
                    self.random_count = int(row[1])
                elif row and row[0] == "errors":
                    self.errors = int(row[1])
                elif row and row[0] == "elapsed_time":
                    try:
                        self.elapsed_time = float(row[1])
                    except ValueError:
                        self.elapsed_time = 0
                elif row and row[0] == "moves_left":
                    self.moves_left = int(row[1])
        except Exception as e:
            print("Error loading file:", e)

    def is_board_empty(self):
        return all(block.value is None for row in self.board for block in row)