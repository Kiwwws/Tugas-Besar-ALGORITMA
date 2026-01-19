import tkinter as tk
from tkinter import messagebox
import time

class SudokuUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver - Backtracking Visualization (Kelompok 10)")
        self.root.geometry("600x780") # Sedikit diperbesar agar muat
        
        # Variabel Logika
        self.grid_cells = [[None for _ in range(9)] for _ in range(9)]
        self.board = []
        self.backtracks = 0
        self.start_time = 0
        self.is_solving = False
        
        # --- UI COMPONENTS ---
        
        # 1. Header & Stats
        self.frame_header = tk.Frame(root, pady=10)
        self.frame_header.pack()
        
        self.lbl_title = tk.Label(self.frame_header, text="Sudoku Backtracking Solver", font=("Helvetica", 16, "bold"))
        self.lbl_title.pack()
        
        self.lbl_stats = tk.Label(self.frame_header, text="Backtracks: 0 | Time: 0.00s", font=("Courier", 12), fg="blue")
        self.lbl_stats.pack()

        # 2. Sudoku Grid (Container Utama)
        self.frame_grid = tk.Frame(root, padx=10, pady=10, bg="#333333") # Background gelap untuk kontras
        self.frame_grid.pack()
        
        # Panggil fungsi grid baru
        self.create_grid_blocks()

        # 3. Control Buttons
        self.frame_controls = tk.Frame(root, pady=20)
        self.frame_controls.pack()
        
        btn_opts = {'width': 12, 'font': ('Arial', 10)}
        tk.Button(self.frame_controls, text="Load Easy", command=lambda: self.load_board("easy"), **btn_opts).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_controls, text="Load Medium", command=lambda: self.load_board("medium"), **btn_opts).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_controls, text="Load Hard", command=lambda: self.load_board("hard"), **btn_opts).grid(row=0, column=2, padx=5)
        
        tk.Button(self.frame_controls, text="SOLVE NOW", command=self.start_solving, bg="green", fg="white", font=("Arial", 12, "bold"), width=15).grid(row=1, column=0, columnspan=3, pady=15)
        
        tk.Button(self.frame_controls, text="Clear / Reset", command=self.clear_grid, bg="red", fg="white", width=15).grid(row=2, column=0, columnspan=3)

        # Default load
        self.load_board("easy")

    def create_grid_blocks(self):
        """
        Membuat grid dengan pendekatan BLOK 3x3 agar garis batas terlihat jelas.
        Struktur: 3x3 Frame Blok -> Di dalam masing-masing ada 3x3 Entry.
        """
        for i in range(3): # Loop Baris Blok (0-2)
            for j in range(3): # Loop Kolom Blok (0-2)
                
                # Frame untuk setiap BLOK 3x3 (Ini yang membuat garis tebal)
                block_frame = tk.Frame(
                    self.frame_grid, 
                    bd=2,               # Ketebalan border blok
                    relief="solid",     # Jenis garis solid
                    bg="black"          # Warna garis pemisah
                )
                # Grid placement untuk blok (kasih padding dikit biar rapi)
                block_frame.grid(row=i, column=j, padx=2, pady=2)
                
                # Isi blok dengan 9 kotak angka
                for si in range(3): # Sub-row (0-2)
                    for sj in range(3): # Sub-col (0-2)
                        
                        # Hitung koordinat asli (0-8) untuk logika
                        real_row = i * 3 + si
                        real_col = j * 3 + sj
                        
                        entry = tk.Entry(
                            block_frame, 
                            width=2,            # Lebar kotak
                            font=("Helvetica", 20, "bold"), 
                            justify="center", 
                            bd=1, 
                            relief="solid"      # Border tipis untuk sel
                        )
                        # Grid di dalam block_frame
                        entry.grid(row=si, column=sj, padx=1, pady=1, ipadx=5, ipady=5)
                        
                        # Simpan referensi ke array utama agar logika solve tetap jalan
                        self.grid_cells[real_row][real_col] = entry

    def reset_visuals(self):
        """Mengembalikan warna background ke putih"""
        for i in range(9):
            for j in range(9):
                self.grid_cells[i][j].config(bg="white")

    def load_board(self, level):
        """Memuat dataset soal ke UI"""
        self.reset_visuals() 
        
        # Dataset Soal
        boards = {
            "easy": [
                [7,8,0,4,0,0,1,2,0], [6,0,0,0,7,5,0,0,9], [0,0,0,6,0,1,0,7,8],
                [0,0,7,0,4,0,2,6,0], [0,0,1,0,5,0,9,3,0], [9,0,4,0,6,0,0,0,5],
                [0,7,0,3,0,0,0,1,2], [1,2,0,0,0,7,4,0,0], [0,4,9,2,0,6,0,0,7]
            ],
            "medium": [
                [0,0,0,2,6,0,7,0,1], [6,8,0,0,7,0,0,9,0], [1,9,0,0,0,4,5,0,0],
                [8,2,0,1,0,0,0,4,0], [0,0,4,6,0,2,9,0,0], [0,5,0,0,0,3,0,2,8],
                [0,0,9,3,0,0,0,7,4], [0,4,0,0,5,0,0,3,6], [7,0,3,0,1,8,0,0,0]
            ],
            "hard": [
                [0,2,0,0,0,0,0,0,0], [0,0,0,6,0,0,0,0,3], [0,7,4,0,8,0,0,0,0],
                [0,0,0,0,0,3,0,0,2], [0,8,0,0,4,0,0,1,0], [6,0,0,5,0,0,0,0,0],
                [0,0,0,0,1,0,7,8,0], [5,0,0,0,0,9,0,0,0], [0,0,0,0,0,0,0,4,0]
            ]
        }
        
        self.board = [row[:] for row in boards[level]] # Deep copy
        self.update_ui_from_board(lock_inputs=True)
        self.backtracks = 0
        self.lbl_stats.config(text="Backtracks: 0 | Time: 0.00s")

    def update_ui_from_board(self, lock_inputs=False):
        """Menyalin data dari self.board ke UI Grid"""
        for i in range(9):
            for j in range(9):
                val = self.board[i][j]
                entry = self.grid_cells[i][j]
                
                # BUG FIX: Pastikan widget enable dulu sebelum didelete/insert
                entry.config(state="normal") 
                entry.delete(0, tk.END) 
                
                if val != 0:
                    entry.insert(0, str(val))
                    if lock_inputs:
                        # Angka Soal: Hitam Tebal
                        entry.config(fg="black", state="disabled") 
                else:
                    # Angka Jawaban: Biru
                    entry.config(fg="blue", state="normal") 

    def clear_grid(self):
        """Membersihkan grid dan mereset warna"""
        self.reset_visuals() 
        for i in range(9):
            for j in range(9):
                self.grid_cells[i][j].config(state="normal")
                self.grid_cells[i][j].delete(0, tk.END)
        self.backtracks = 0
        self.lbl_stats.config(text="Backtracks: 0 | Time: 0.00s")

    # --- ALGORITMA BACKTRACKING (CORE) ---

    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i, j)
        return None

    def is_valid(self, num, pos):
        # Cek Baris & Kolom
        for i in range(9):
            if self.board[pos[0]][i] == num and pos[1] != i: return False
            if self.board[i][pos[1]] == num and pos[0] != i: return False
        
        # Cek Box
        box_x, box_y = pos[1] // 3, pos[0] // 3
        for i in range(box_y*3, box_y*3 + 3):
            for j in range(box_x*3, box_x*3 + 3):
                if self.board[i][j] == num and (i,j) != pos: return False
        return True

    def solve_visual(self):
        """Versi Solve dengan update GUI"""
        find = self.find_empty()
        if not find:
            return True
        row, col = find

        for i in range(1, 10):
            if self.is_valid(i, (row, col)):
                self.board[row][col] = i
                
                # --- VISUALISASI START ---
                entry = self.grid_cells[row][col]
                entry.delete(0, tk.END)
                entry.insert(0, str(i))
                entry.config(bg="#ccffcc") # Hijau saat mencoba
                
                self.root.update() 
                # --- VISUALISASI END ---

                if self.solve_visual():
                    return True

                # BACKTRACK
                self.board[row][col] = 0
                entry.delete(0, tk.END)
                entry.config(bg="#ffcccc") # Merah saat mundur
                self.backtracks += 1
                
                if self.backtracks % 10 == 0: 
                    self.lbl_stats.config(text=f"Backtracks: {self.backtracks} | Solving...")
                
        return False

    def start_solving(self):
        if self.is_solving: return # Cegah double click
        self.is_solving = True
        self.start_time = time.time()
        
        try:
            found = self.solve_visual()
        except tk.TclError:
            return 
            
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.is_solving = False
        
        self.lbl_stats.config(text=f"Backtracks: {self.backtracks} | Time: {duration:.4f}s")
        
        if found:
            messagebox.showinfo("Success", f"Solusi Ditemukan!\nTotal Backtracks: {self.backtracks}\nWaktu: {duration:.4f} detik")
        else:
            messagebox.showerror("Failed", "Tidak ada solusi untuk papan ini!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuUI(root)
    root.mainloop()