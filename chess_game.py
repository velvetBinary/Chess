# chess.py

def create_board():
    board = [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p"] * 8,
        [" "] * 8,
        [" "] * 8,
        [" "] * 8,
        [" "] * 8,
        ["P"] * 8,
        ["R", "N", "B", "Q", "K", "B", "N", "R"]
    ]
    return board

def print_board(board):
    print("  a b c d e f g h")
    for i, row in enumerate(board):
        print(8 - i, end=" ")
        for piece in row:
            print(piece, end=" ")
        print(8 - i)
    print("  a b c d e f g h")

def main():
    board = create_board()
    print_board(board)

if __name__ == "__main__":
    main()
