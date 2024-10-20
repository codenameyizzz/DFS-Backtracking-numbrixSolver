# solver.py

from board import Board
import copy

def solve(board, debug_level, step_callback=None):
    """
    Menyelesaikan puzzle Numbrix menggunakan Algoritma DFS (Backtracking).

    Parameter:
    - board: Papan permainan Numbrix yang akan diselesaikan.
    - debug_level: Tingkat detail log yang diinginkan ("none", "trace").
    - step_callback: Fungsi callback yang dipanggil setiap kali papan diperbarui.

    Cara Kerja:
        1. Menggunakan pendekatan backtracking untuk mencoba nilai pada sel yang belum diisi.
        2. Memanggil `step_callback` setiap kali sebuah nilai diatur pada papan.
        3. Mengembalikan solusi jika ditemukan, atau menyatakan kegagalan jika tidak.
    """
    i = 0
    leaves = 0
    cross_overs = 0

    seen = set()
    stack = [board]

    while len(stack) > 0:
        curr = stack.pop()
        i += 1
        if i % 100 == 0 and debug_level == "info":
            print(f"Iteration {i}, leaves: {leaves}, cross overs: {cross_overs}, current board:\n{curr}")
        elif debug_level == "trace" or debug_level == "pause":
            print(f"Iteration {i}, leaves: {leaves}, cross overs: {cross_overs}, current board:\n{curr}")
            if debug_level == "pause":
                input(":")
        
        if repr(curr) in seen or curr.is_not_feasible():
            if curr.is_not_feasible():
                leaves += 1
            else:
                cross_overs += 1
            continue

        if curr.is_complete():
            print(f"Success! Took {i} iterations, found {leaves} dead ends and {cross_overs} graph cross overs.")
            print("  --> Final board:")
            print(curr)
            return

        # Mark the current board as seen
        seen.add(repr(curr))

        # Generate the next possible boards
        boards = curr.get_next_boards()
        for next_board in boards:
            stack.append(next_board)
            if step_callback:
                # Memanggil callback setiap kali sebuah langkah diambil
                step_callback(copy.deepcopy(next_board))

    print(f"Failure, could not find a solution after {i} iterations. Saw {leaves} dead ends and {cross_overs} graph cross overs.")

def check_line(line):
    """Periksa:
        1. Pastikan baris memiliki sembilan nilai.
        2. Setiap nilai harus memiliki panjang 1 atau 2 karakter.
        3. Setiap nilai harus berupa digit atau tanda "-" (dash).
        4. Jika nilai adalah digit, harus berada dalam rentang 1 sampai 81.
    """
    vals = line.split()
    if not len(vals) == 9:
        return False

    for val in vals:
        if not (1 <= len(val) <= 2):
            return False
        if not (val.isdigit() or val == "-"):
            return False
        if val.isdigit() and not 1 <= int(val) <= 81:
            return False

    return True

def store_line(line, row, board):
    """Set a line of this solver's board."""
    for col, val in enumerate(line.split()):
        if val.isdigit():
            board.set(row, col, int(val), is_fixed=True)

def read_input_from_file(file, board):
    """Read a board from a file."""
    with open(file) as f:
        lines = f.readlines()
        if len(lines) != 9:
            raise ValueError("Input file must contain exactly 9 lines.")
        for row, line in enumerate(lines):
            if check_line(line.strip()):
                store_line(line.strip(), row, board)
            else:
                raise ValueError(f"Invalid line {row + 1} in input file.")

    print(f"All lines read from {file}, input board:\n{board}")

def read_input_from_stdin(board):
    """Read a board from stdin."""
    lines = 0
    while lines < 9:
        line = input("Please enter line " + str(lines + 1) + ": ")
        if check_line(line):
            store_line(line.strip(), lines, board)
            lines += 1
        else:
            print("Error while parsing line, expecting nine values, 1-81 or '-' separated by spaces, please try again")

    print(f"All lines entered, input board:\n{board}")
