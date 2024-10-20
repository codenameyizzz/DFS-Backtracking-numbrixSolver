# gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from board import Board
from solver import solve, read_input_from_file
import copy

class NumbrixApp:
    def __init__(self, master):
        self.master = master
        master.title("Numbrix Solver")

        # Grid untuk menampilkan tombol
        self.buttons = [[None for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                btn = tk.Button(master, text='-', width=4, height=2, font=("Helvetica", 16),
                                command=lambda row=i, col=j: self.button_click(row, col))
                btn.grid(row=i, column=j, padx=1, pady=1, sticky='news')
                self.buttons[i][j] = btn

        # Tombol untuk memuat game dari file
        self.load_button = tk.Button(master, text="Load Game", command=self.load_game)
        self.load_button.grid(row=9, column=0, columnspan=4, pady=10, sticky='news')

        # Tombol untuk memulai penyelesaian game
        self.solve_button = tk.Button(master, text="Solve", command=self.start_solving)
        self.solve_button.grid(row=9, column=5, columnspan=4, pady=10, sticky='news')

        # Inisialisasi papan
        self.board = Board()

        # Menyimpan langkah-langkah penyelesaian
        self.steps = []
        self.current_step = 0

    def button_click(self, row, col):
        """
        Input manual untuk memasukkan angka ke papan.
        """
        val = self.board.get(row, col).get()
        if self.board.get(row, col).is_set():
            messagebox.showwarning("Warning", "Cannot change fixed cells.")
            return
        new_val = simpledialog.askinteger("Input", f"Enter value for ({row + 1},{col + 1}):", initialvalue=val)
        if new_val is not None:
            if not (1 <= new_val <= 81):
                messagebox.showerror("Error", "Value must be between 1 and 81.")
                return
            self.board.set(row, col, new_val, is_fixed=False)
            self.update_board()

    def load_game(self):
        """
        Fungsi untuk memuat game dari file.
        """
        filename = filedialog.askopenfilename(title="Select Numbrix Puzzle File",
                                              filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        if filename:
            try:
                self.board = Board()
                read_input_from_file(filename, self.board)
                self.update_board()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def update_board(self):
        """
        Memperbarui tampilan papan UI berdasarkan nilai papan saat ini.
        """
        for i in range(9):
            for j in range(9):
                val = self.board.get(i, j)
                display_val = str(val.get()) if val.is_set() else "-"
                self.buttons[i][j]['text'] = display_val
                if val.is_set():
                    self.buttons[i][j]['bg'] = 'light blue'  # Warna untuk sel tetap
                else:
                    self.buttons[i][j]['bg'] = 'light gray'  # Warna untuk sel kosong

    def start_solving(self):
        """
        Memulai proses penyelesaian dengan animasi langkah demi langkah.
        """
        if not self.validate_board():
            return

        self.steps = []
        self.current_step = 0

        def step_callback(board_snapshot):
            """
            Callback yang dipanggil setiap kali ada perubahan pada papan selama proses penyelesaian.
            """
            snapshot = [[board_snapshot.get(i, j).get() if board_snapshot.get(i, j).is_set() else 0 for j in range(9)] for i in range(9)]
            self.steps.append(snapshot)

        # Jalankan solver dengan step_callback
        solve(self.board, "trace", step_callback=step_callback)

        if not self.steps:
            messagebox.showinfo("Info", "No steps were generated during solving.")
            return

        # Mulai animasi langkah demi langkah
        self.animate_steps()

    def animate_steps(self):
        """
        Menampilkan langkah-langkah penyelesaian secara animasi.
        """
        if self.current_step >= len(self.steps):
            # Setelah animasi selesai
            if self.board.is_complete():
                messagebox.showinfo("Success", "Solution found!")
            else:
                messagebox.showwarning("Failed", "Failed to find a solution.")
            return

        snapshot = self.steps[self.current_step]

        for i in range(9):
            for j in range(9):
                new_val = snapshot[i][j]
                btn = self.buttons[i][j]
                current_val = btn['text']
                if new_val != 0 and current_val != str(new_val):
                    btn['text'] = str(new_val)
                    if not self.board.get(i, j).is_set():
                        btn['bg'] = 'yellow'  # Menandai perubahan

        self.current_step += 1
        # Update papan dengan snapshot saat ini
        self.board = Board()
        for i in range(9):
            for j in range(9):
                val = snapshot[i][j]
                if val != 0:
                    self.board.set(i, j, val, is_fixed=False)

        # Delay untuk animasi langkah berikutnya (misalnya, 100 ms)
        self.master.after(100, self.animate_steps)

    def validate_board(self):
        """
        Memeriksa apakah papan awal valid sebelum memulai penyelesaian.
        """
        numbers = set()
        for i in range(9):
            for j in range(9):
                val = self.board.get(i, j).get()
                if val is not None and val != 0:
                    if val in numbers:
                        messagebox.showerror("Error", f"Duplicate number {val} found at ({i + 1},{j + 1}).")
                        return False
                    numbers.add(val)
        return True
