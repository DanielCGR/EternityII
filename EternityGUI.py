import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from io import StringIO
import Eternity  # Import your existing Eternity code
import math

COLORS = {
    'G': '#70ad47',
    'B': '#4bacc6',
    'R': '#FF0000',
    'V': '#8064a2',
    'Y': '#ffd966',
    'O': '#f57e20',
    'A': '#1c90f3',
    '-': 'black'
}

class EternityGUI(tk.Tk):

    def __init__(self):
        super().__init__()

        # Define ttk style
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg='#1E5162')
        self.style.configure('Custom.TButton', background='#ADD8E6', foreground='#000000', font=('Helvetica', 12, 'bold'))
        self.style.configure('Custom.TLabel', background='#ADD8E6', foreground='#000000', font=('Helvetica', 16, 'bold'))

        # Initialize GUI components
        self.title("Eternity II Solver")
        self.geometry("600x700")

        self.title_label = ttk.Label(self, text="Eternity II - UPC", style='Custom.TLabel')
        self.title_label.pack(pady=10)

        self.canvas = tk.Canvas(self, width=550, height=550, bg='#222')
        self.canvas.pack(pady=10)

        self.input_button = ttk.Button(self, text="Load Puzzle Input", command=self.load_puzzle_input, style='Custom.TButton')
        self.input_button.place(relx=0.28, rely=0.9, anchor="center")

        self.solve_puzzle_button = ttk.Button(self, text="Solve Puzzle", command=self.run_solver, state="disabled", style='Custom.TButton')
        self.solve_puzzle_button.place(relx=0.51, rely=0.9, anchor="center")

        self.reset_button = ttk.Button(self, text="Reset", command=self.reset, state="disabled", style='Custom.TButton')
        self.reset_button.place(relx=0.71, rely=0.9, anchor="center")

    def display_puzzle_pieces(self):
        self.canvas.delete("all")
        size = len(self.puzzle)
        grid_size = int(math.sqrt(size))
        square_size = int(self.canvas["width"]) // (grid_size)

        for row in range(grid_size):
            for col in range(grid_size):
                piece_index = row * grid_size + col
                piece = self.puzzle[piece_index]
                x, y = col * square_size, row * square_size
                self.draw_piece(self.canvas, piece, x, y, square_size)

    def draw_piece(self, canvas, piece, x, y, square_size, rotation=0):
        half = square_size // 2

        coords = [
            (x, y + half),
            (x + half, y),
            (x + square_size, y + half),
            (x + half, y + square_size)
        ]

        def rotate_polygon(coords, center, angle):
            angle = math.radians(angle)
            rotated_coords = []
            for coord in coords:
                x, y = coord
                x_diff = x - center[0]
                y_diff = y - center[1]
                new_x = center[0] + x_diff * math.cos(angle) - y_diff * math.sin(angle)
                new_y = center[1] + x_diff * math.sin(angle) + y_diff * math.cos(angle)
                rotated_coords.append((new_x, new_y))
            return rotated_coords

        square_center = (x + half, y + half)
        rotated_coords = rotate_polygon(coords, square_center, 45)

        for i, color in enumerate(piece):
            index = (i - rotation) % 4
            if index < 0:
                index += len(piece)
            triangle_coords = [rotated_coords[index], rotated_coords[(index + 1) % 4], square_center]

            # Adjust the triangle vertices slightly to remove the gap between pieces
            adjust_factor = 1.4
            adjusted_triangle_coords = []
            for coord in triangle_coords:
                adjusted_x = square_center[0] + adjust_factor * (coord[0] - square_center[0])
                adjusted_y = square_center[1] + adjust_factor * (coord[1] - square_center[1])
                adjusted_triangle_coords.append((adjusted_x, adjusted_y))

            canvas.create_polygon(adjusted_triangle_coords, fill=COLORS[color], outline='')
            label_x, label_y = (adjusted_triangle_coords[0][0] + 2 * adjusted_triangle_coords[1][0] + adjusted_triangle_coords[2][0]) // 4, (adjusted_triangle_coords[0][1] + 2 * adjusted_triangle_coords[1][1] + adjusted_triangle_coords[2][1]) // 4
            canvas.create_text(label_x, label_y, text=color, fill='white', font=('Arial', 10, 'bold'))


    def display_solution(self):
        self.canvas.delete("all")
        if not self.solution:
            messagebox.showerror("No Solution", "No solution found. Try another input.")
            return

        size = int(len(self.solution))
        square_size = int(self.canvas["width"]) // size

        for row in range(size):
            for col in range(size):
                piece_idx = self.solution[row][col] - 1
                rotation = (4 - self.rotations[row][col]) % 4  # Fix the rotation issue here
                piece = self.puzzle[piece_idx]
                rotated_piece = piece[rotation:] + piece[:rotation]
                x = col * square_size
                y = row * square_size
                self.draw_piece(self.canvas, rotated_piece, x, y, square_size)


    def load_puzzle_input(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                input_str = file.read()
                self.puzzle = Eternity.read_puzzle(StringIO(input_str))
                self.display_puzzle_pieces()
                self.solve_puzzle_button["state"] = "normal"
                self.reset_button["state"] = "normal"

    def run_solver(self):
        self.solution, self.rotations = Eternity.solve_eternity(self.puzzle)
        if self.solution is not None:
            for idx, (row, rot) in enumerate(zip(self.solution, self.rotations)):
                print(f"Row {idx + 1}:")
                print(f"Piece Index : {row} || Rotation : {rot}")
            self.display_solution()
        else:
            messagebox.showerror("No Solution", "No solution found. Try another input.")
            self.reset()


    def reset(self):
        # Reset the application to the initial state
        self.canvas.delete("all")
        self.solve_puzzle_button["state"] = "disabled"
        self.reset_button["state"] = "disabled"


if __name__ == "__main__":
    app = EternityGUI()
    app.mainloop()