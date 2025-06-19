# game_modes.py
import tkinter as tk
import time
class GameMode:
    def __init__(self, game_gui):
        self.gui = game_gui

    def start(self):
        pass

    def on_match_failed(self):
        pass

    def on_tick(self):
        pass

    def is_game_over(self):
        return False



class StandardMode(GameMode):
    pass  # dziedziczy całe zachowanie z GUI




class TimedMode(GameMode):
    def __init__(self, gui):
        super().__init__(gui)
        self.time_limit = 60  # 60 sekund

    def start(self):
        self.start_time = time.time()

    def on_tick(self):
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - int(elapsed))
        self.gui.time_label.config(text=f"Czas: 00:{remaining:02}")
        if remaining <= 0:
            self.gui.stop_game("Czas minął!")




class SniperMode(GameMode):
    def start(self):
        self.gui.error_label.pack_forget()

    def on_match_failed(self):
        self.gui.stop_game("Popełniono błąd. Koniec gry!")
        





class ChallengeMode(GameMode):
    def __init__(self, gui):
        super().__init__(gui)
        self.moves_left = gui.board.moves_left if hasattr(gui.board, "moves_left") else 30
        gui.board.moves_left = self.moves_left

    def start(self):
        self.gui.move_label.config(text=f"Ruchy: {self.moves_left}/30")
        self.gui.move_label.pack(side=tk.LEFT, padx=10)

    def on_match_failed(self):
        self._decrement_moves()

    def on_match(self):
        self._decrement_moves()

    def _decrement_moves(self):
        self.moves_left -= 1
        self.gui.board.moves_left = self.moves_left  # aktualizacja planszy
        self.gui.move_label.config(text=f"Ruchy: {self.moves_left}/30")
        if self.moves_left <= 0:
            self.gui.stop_game("Wykorzystano wszystkie ruchy.")
