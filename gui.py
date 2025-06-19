import tkinter as tk
from game_logic import GameBoard, Position
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import random
import time
from game_modes import StandardMode, TimedMode, SniperMode, ChallengeMode


class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SumUp")
        self.root.geometry("500x600")

        self.board = GameBoard()
        self.images = self.load_images()
        self.buttons = []
        self.selected = []

        self.mode = None
        self.start_time = None
        self.running = False
        self.paused = False
        self.timer_id = None
        self.MAX_ERRORS = 5

        self.create_widgets()
        self.update_gui()

    def create_widgets(self):
        # Logo
        logo_img = Image.open("assets/4343.png").resize((250, 80), Image.Resampling.LANCZOS)
        self.logo = ImageTk.PhotoImage(logo_img)
        tk.Label(self.root, image=self.logo).pack(pady=10)

        # Top Buttons
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)

        tk.Button(top_frame, text="Rozpocznij grę", command=self.start_game).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Zatrzymaj grę", command=self.pause_game).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Zakończ grę", command=self.stop_game).pack(side=tk.LEFT, padx=5)

        # Tryby gry (pod przyciskami sterującymi)
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=5)

        self.mode_var = tk.StringVar(value="standard")
        modes = [
            ("Standard", "standard"), 
            ("Minutka", "timed"), 
            ("Sniper", "sniper"),  
            ("Punktowy", "challenge")
        ]


        for text, value in modes:
            tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=value).pack(side=tk.LEFT, padx=2)


        # Game Board Buttons
        board_frame = tk.Frame(self.root)
        board_frame.pack()

        for i in range(GameBoard.SIZE):
            row = []
            for j in range(GameBoard.SIZE):
                btn = tk.Button(board_frame, image=self.images[None],
                                command=lambda r=i, c=j: self.block_clicked(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                row.append(btn)
            self.buttons.append(row)

        # Bottom Buttons
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10)

        row1 = tk.Frame(bottom_frame)
        row1.pack()
        tk.Button(row1, text="Losuj liczby", command=self.randomize_numbers).pack(side=tk.LEFT, padx=5)
        tk.Button(row1, text="Zasady gry", command=self.show_rules).pack(side=tk.LEFT, padx=5)
        tk.Button(row1, text="Zapisz planszę", command=self.save_board).pack(side=tk.LEFT, padx=5)
        tk.Button(row1, text="Wczytaj planszę", command=self.load_board).pack(side=tk.LEFT, padx=5)

        # Status Labels
        row2 = tk.Frame(bottom_frame)
        row2.pack(pady=5)

        self.time_label = tk.Label(row2, text="Czas: 00:00")
        self.time_label.pack(side=tk.LEFT, padx=10)
        self.score_label = tk.Label(row2, text="Punkty: 0")
        self.score_label.pack(side=tk.LEFT, padx=10)
        self.error_label = tk.Label(row2, text="Błędy: 0/5")
        self.error_label.pack(side=tk.LEFT, padx=10)
        self.random_count_label = tk.Label(row2, text="Dolosowania: 0/6")
        self.random_count_label.pack(side=tk.LEFT, padx=10)
        self.move_label = tk.Label(row2, text="Ruchy: 30/30")
        self.move_label.pack_forget()  # domyślnie ukryta

    def start_game(self):
        if self.running:
            messagebox.showinfo("Gra aktywna", "Gra już została rozpoczęta.")
            return

        self.running = True
        self.paused = False

        self.board = GameBoard()
        mode_type = self.mode_var.get()
        mode_map = {
            "standard": StandardMode,
            "timed": TimedMode,
            "sniper": SniperMode,
            "challenge": ChallengeMode
        }
        self.mode = mode_map[mode_type](self)
        self.mode.start()

        self.selected.clear()
        self.start_time = time.time()

        self.init_board_with_random_values()

        self.update_labels()

        self.animate_start(0)

        self.board.mode_name = mode_type

    def init_board_with_random_values(self):
        for i in range(3):
            for j in range(GameBoard.SIZE):
                self.board.board[i][j].value = random.randint(1, 9)

    def animate_start(self, step):
        if step < 6:
            for i in range(3):
                for j in range(GameBoard.SIZE):
                    self.buttons[i][j].config(bg="yellow")
            self.root.after(50, lambda: self.animate_start(step + 1))
        else:
            self.update_gui()
            self.update_timer()

    def pause_game(self):
        if not self.running:
            messagebox.showinfo("Błąd", "Gra nie została rozpoczęta.")
            return

        if not self.paused:
            self.paused = True
            self.board.elapsed_time += time.time() - self.start_time
            self.root.after_cancel(self.timer_id)
            if messagebox.askokcancel("Pauza", "Gra wstrzymana. Kliknij OK aby wznowić."):
                self.paused = False
                self.start_time = time.time()
                self.update_timer()

    def stop_game(self, reason=None):
        if not self.running:
            messagebox.showinfo("Błąd", "Gra nie została rozpoczęta.")
            return

        self.running = False
        self.paused = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        total_time = int(self.board.elapsed_time + (time.time() - self.start_time))
        msg = f"{reason + '\n\n' if reason else ''}Czas: {time.strftime('%H:%M:%S', time.gmtime(total_time))}\nPunkty: {self.board.score}"
        messagebox.showinfo("Koniec gry", msg)

    def block_clicked(self, row, col):
        if not self.running:
            return
        
        pos = Position(row, col)
        if pos in self.selected:
            return

        self.selected.append(pos)
        self.buttons[row][col].config(bg="lightblue")

        if len(self.selected) == 2:
            self.handle_match()
            self.selected.clear()
            self.update_gui()

            if self.board.is_board_empty():
                self.stop_game("Gratulacje! Wyczyściłeś całą planszę!")

    def handle_match(self):
        pos1, pos2 = self.selected
        if self.board.is_match(pos1, pos2):
            val1, val2 = self.board.get_value(pos1.row, pos1.col), self.board.get_value(pos2.row, pos2.col)
            self.board.clear_positions(pos1, pos2)
            self.board.score += 5 if val1 == val2 else 10
            if hasattr(self.mode, 'on_match'):
                self.mode.on_match()
        else:
            self.board.errors += 1
            self.error_label.config(text=f"Błędy: {self.board.errors}/{self.MAX_ERRORS}")
            if self.board.errors >= self.MAX_ERRORS:
                self.stop_game("Przekroczono limit błędów.")
            else:
                messagebox.showwarning("Błąd!",
                    f"Niepoprawne dopasowanie:\n({self.board.get_value(pos1.row, pos1.col)}) i ({self.board.get_value(pos2.row, pos2.col)}) "
                    "nie spełniają warunków. Muszą być równe lub sumować się do 10 i być połączalne.")
                self.mode.on_match_failed()

    def update_gui(self):
        for i in range(GameBoard.SIZE):
            for j in range(GameBoard.SIZE):
                val = self.board.get_value(i, j)
                self.buttons[i][j].config(image=self.images.get(val, self.images[None]), bg="SystemButtonFace")
        self.update_labels()


    def update_labels(self):
        self.score_label.config(text=f"Punkty: {self.board.score}")
        self.error_label.config(text=f"Błędy: {self.board.errors}/{self.MAX_ERRORS}")
        self.random_count_label.config(text=f"Dolosowania: {self.board.random_count}/6")

        if not isinstance(self.mode, TimedMode):
            total_time = int(self.board.elapsed_time + (
                        time.time() - self.start_time)) if self.running and not self.paused else self.board.elapsed_time
            self.time_label.config(text=f"Czas: {time.strftime('%H:%M:%S', time.gmtime(total_time))}")

        if isinstance(self.mode, ChallengeMode):  # jeśli tryb punktowy
            self.move_label.config(text=f"Ruchy: {self.mode.moves_left}/30")
            self.move_label.pack(side=tk.LEFT, padx=10)
        else:
            self.move_label.pack_forget()

        if isinstance(self.mode, SniperMode):
            self.error_label.pack_forget()
        else:
            self.error_label.config(text=f"Błędy: {self.board.errors}/{self.MAX_ERRORS}")
            self.error_label.pack(side=tk.LEFT, padx=10)

    def update_timer(self):
        if self.running and not self.paused:
            self.update_labels()
            self.timer_id = self.root.after(1000, self.update_timer)
            self.mode.on_tick()


    def randomize_numbers(self):
        if not self.running:
            messagebox.showinfo("Błąd", "Gra nie została rozpoczęta.")
            return

        if self.board.random_count >= 6:
            messagebox.showinfo("Limit", "Osiągnięto maksymalną liczbę losowań.")
            return

        empty_rows = [(i, sum(1 for cell in row if cell.is_empty())) for i, row in enumerate(self.board.board)]
        empty_rows.sort(key=lambda x: -x[1])
        selected = [i for i, count in empty_rows[:2] if count > 0]

        if not selected:
            messagebox.showinfo("Brak miejsc", "Brak pustych miejsc do wstawienia liczb.")
            return

        existing_values = [block.value for row in self.board.board for block in row if block.value]
        for i in selected:
            for j in range(GameBoard.SIZE):
                if self.board.board[i][j].is_empty():
                    self.board.board[i][j].value = random.choice(existing_values)
        self.board.random_count += 1
        self.update_gui()

    def show_rules(self):
        if self.running and not self.paused:
            self.pause_game()

        rules = (
            "Zasady gry - tryb standard:\n\n"
            "1. Dopasuj pary liczb: identyczne lub sumujące się do 10.\n"
            "2. Połączenia poziome, pionowe lub po przekątnej.\n"
            "3. Można dodawać nowe liczby maks. 6 razy.\n"
            "4. Wyczyść planszę, aby wygrać.\n"
            "\n\n"
            "Zasady gry - tryb minutka:\n\n"
            "Zasady jak w wersji standardowej, dodatkowo ograniczenie czasowe - minuta na wyczyszczenie całej planszy.\n"
            "\n\n"
            "Zasady gry - tryb sniper:\n\n"
            "Zasady jak w wersji standardowej, ale popełnienie jakiegokolwiek błędu skutkuje zakończeniem gry.\n"
            "\n\n"
            "Zasady gry - tryb punktowy:\n\n"
            "Zasady jak w wersji standardowej, ale występuje dodatkoww ograniczenie co do liczby ruchów - należy wyczyścić planszę w maksymalnie 30 ruchach."
        )
        messagebox.showinfo("Zasady gry", rules)

    def save_board(self):
        if self.running and not self.paused:
            self.board.elapsed_time += time.time() - self.start_time
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if file_path:
            self.board.save_to_file(file_path)
            messagebox.showinfo("Zapisano", f"Plansza zapisana:\n{file_path}")

    def load_board(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not file_path or not file_path.endswith('.csv'):
            messagebox.showerror("Błąd", "Nie wybrano poprawnego pliku CSV.")
            return

        try:
            self.board.load_from_file(file_path)

            mode_map = {
                "standard": StandardMode,
                "timed": TimedMode,
                "sniper": SniperMode,
                "challenge": ChallengeMode
            }
            mode_key = self.board.mode_name
            self.mode_var.set(mode_key)

            if mode_key == "challenge" and hasattr(self.board, "saved_moves_left"):
                self.mode = ChallengeMode(self, moves_left=self.board.saved_moves_left)
            else:
                self.mode = mode_map[mode_key](self)

            self.mode.start()
            self.start_time = time.time()
            self.running = True
            self.paused = False
            self.update_gui()
            self.update_timer()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać planszy:\n{e}")

    def load_images(self):
        images = {}
        for i in range(1, 10):
            img = Image.open(f"assets/img/{i}.png").resize((50, 50))
            images[i] = ImageTk.PhotoImage(img)
        img_empty = Image.open("assets/img/empty.png").resize((50, 50))
        images[None] = ImageTk.PhotoImage(img_empty)
        return images
