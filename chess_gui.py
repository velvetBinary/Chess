# FANCY CHESS GUI - Full version with Undo, Move History, AI, Dark Mode, Pawn Promotion

import tkinter as tk
from tkinter import messagebox
import random

TILE_SIZE = 60
BOARD_SIZE = 8

pieces_unicode = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
}

directions = {
    "P": [(-1, 0), (-1, -1), (-1, 1)],
    "p": [(1, 0), (1, -1), (1, 1)],
    "R": [(1, 0), (-1, 0), (0, 1), (0, -1)],
    "B": [(1, 1), (-1, -1), (1, -1), (-1, 1)],
    "Q": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],
    "N": [(-2, -1), (-2, 1), (-1, 2), (-1, -2), (1, 2), (1, -2), (2, -1), (2, 1)],
    "K": [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
}

initial_board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p"] * 8,
    [" "] * 8,
    [" "] * 8,
    [" "] * 8,
    [" "] * 8,
    ["P"] * 8,
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]

def coords_to_notation(row, col):
    return f"{chr(col + ord('a'))}{8 - row}"

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fancy Chess")
        self.theme = "light"
        self.create_widgets()
        self.restart_game()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE*TILE_SIZE, height=BOARD_SIZE*TILE_SIZE)
        self.canvas.grid(row=0, column=0, rowspan=8)
        self.canvas.bind("<Button-1>", self.handle_click)

        self.history_box = tk.Listbox(self.root, height=20, width=20)
        self.history_box.grid(row=0, column=1, padx=10)

        tk.Button(self.root, text="Undo Move", command=self.undo_move).grid(row=1, column=1, pady=5)
        tk.Button(self.root, text="Restart Game", command=self.restart_game).grid(row=2, column=1, pady=5)
        tk.Button(self.root, text="Toggle Theme", command=self.toggle_theme).grid(row=3, column=1, pady=5)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.draw_board()
        self.draw_pieces()

    def restart_game(self):
        self.board = [row[:] for row in initial_board]
        self.turn = "white"
        self.selected = None
        self.legal_moves = []
        self.move_stack = []
        self.move_history = []
        self.history_box.delete(0, tk.END)
        self.draw_board()
        self.draw_pieces()

    def undo_move(self):
        if self.move_stack:
            self.board = self.move_stack.pop()
            if self.move_history:
                self.move_history.pop()
                self.history_box.delete(tk.END)
            self.turn = "black" if self.turn == "white" else "white"
            self.selected = None
            self.legal_moves = []
            self.draw_board()
            self.draw_pieces()

    def draw_board(self):
        self.canvas.delete("all")
        light, dark = ("#EEE", "#444") if self.theme == "light" else ("#222", "#888")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1, y1 = col * TILE_SIZE, row * TILE_SIZE
                x2, y2 = x1 + TILE_SIZE, y1 + TILE_SIZE
                color = light if (row + col) % 2 == 0 else dark
                if self.selected == (row, col):
                    color = "#88F"
                elif (row, col) in self.legal_moves:
                    color = "#6F6"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def draw_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece != " ":
                    x = col * TILE_SIZE + TILE_SIZE // 2
                    y = row * TILE_SIZE + TILE_SIZE // 2
                    color = "white" if piece.isupper() else "black"
                    self.canvas.create_text(x, y, text=pieces_unicode[piece], font=("Arial", 36), fill=color)

    def handle_click(self, event):
        row, col = event.y // TILE_SIZE, event.x // TILE_SIZE
        if self.selected:
            if (row, col) in self.legal_moves:
                self.move_stack.append([r[:] for r in self.board])
                self.make_move(self.selected, (row, col))
                self.selected = None
                self.legal_moves = []
                self.check_winner()
                if self.turn == "black":
                    self.root.after(500, self.make_ai_move)
            else:
                self.selected = None
                self.legal_moves = []
        else:
            piece = self.board[row][col]
            if piece != " " and (
                (self.turn == "white" and piece.isupper()) or
                (self.turn == "black" and piece.islower())
            ):
                self.selected = (row, col)
                self.legal_moves = self.get_legal_moves(row, col)
        self.draw_board()
        self.draw_pieces()

    def make_move(self, from_pos, to_pos):
        r1, c1 = from_pos
        r2, c2 = to_pos
        piece = self.board[r1][c1]
        self.board[r2][c2] = piece
        self.board[r1][c1] = " "

        # Pawn promotion
        if piece == "P" and r2 == 0:
            self.board[r2][c2] = "Q"
        elif piece == "p" and r2 == 7:
            self.board[r2][c2] = "q"

        notation = f"{coords_to_notation(r1, c1)} → {coords_to_notation(r2, c2)}"
        self.move_history.append(notation)
        self.history_box.insert(tk.END, notation)
        self.turn = "black" if self.turn == "white" else "white"

    def make_ai_move(self):
        all_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != " " and piece.islower():
                    for move in self.get_legal_moves(r, c):
                        all_moves.append(((r, c), move))
        if all_moves:
            move = random.choice(all_moves)
            self.move_stack.append([r[:] for r in self.board])
            self.make_move(*move)
            self.draw_board()
            self.draw_pieces()
            self.check_winner()

    def get_legal_moves(self, r1, c1):
        piece = self.board[r1][c1]
        legal = []
        for r2 in range(BOARD_SIZE):
            for c2 in range(BOARD_SIZE):
                if self.is_valid_move(piece, r1, c1, r2, c2):
                    legal.append((r2, c2))
        return legal

    def is_valid_move(self, piece, r1, c1, r2, c2):
        if not (0 <= r2 < 8 and 0 <= c2 < 8): return False
        if r1 == r2 and c1 == c2: return False
        target = self.board[r2][c2]
        if target != " " and target.isupper() == piece.isupper(): return False

        if piece.lower() == "p":
            direction = -1 if piece.isupper() else 1
            start_row = 6 if piece.isupper() else 1
            if c1 == c2:
                if r2 == r1 + direction and target == " ": return True
                if r1 == start_row and r2 == r1 + 2 * direction and self.board[r1 + direction][c1] == " " and target == " ": return True
            elif abs(c2 - c1) == 1 and r2 == r1 + direction and target != " " and target.isupper() != piece.isupper(): return True
            return False

        moves = directions.get(piece.upper(), [])
        dr, dc = r2 - r1, c2 - c1
        if piece.upper() == "N":
            return (dr, dc) in moves
        if piece.upper() == "K":
            return (abs(dr), abs(dc)) in [(1, 0), (0, 1), (1, 1), (1, -1), (-1, 1), (-1, 0), (0, -1), (-1, -1)]

        for drow, dcol in moves:
            for i in range(1, 8):
                nr, nc = r1 + drow * i, c1 + dcol * i
                if not (0 <= nr < 8 and 0 <= nc < 8): break
                if nr == r2 and nc == c2:
                    return self.is_path_clear(r1, c1, r2, c2)
                if self.board[nr][nc] != " ": break
        return False

    def is_path_clear(self, r1, c1, r2, c2):
        dr, dc = r2 - r1, c2 - c1
        step_r = (dr > 0) - (dr < 0)
        step_c = (dc > 0) - (dc < 0)
        r, c = r1 + step_r, c1 + step_c
        while (r, c) != (r2, c2):
            if self.board[r][c] != " ": return False
            r += step_r
            c += step_c
        return True

    def check_winner(self):
        flat = sum(self.board, [])
        if "k" not in flat:
            messagebox.showinfo("Game Over", "White wins! ♔")
        elif "K" not in flat:
            messagebox.showinfo("Game Over", "Black wins! ♚")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
