import pygame
import sys
import numpy as np

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
LIGHTGREEN = (128, 192, 128)
DARKGREEN = (0, 64, 0)

# Players
PLAYER_WHITE = 1
PLAYER_BLACK = 0
EMPTY = -1

# Board settings
BOTTOM_OFFSET = 60
WIDTH = 600
HEIGHT = 600
ROWS = 8
COLS = 8
SQUARE_SIZE = WIDTH // COLS

# Initialize pygame
pygame.init()

# Initialize the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT + BOTTOM_OFFSET))
pygame.display.set_caption("Reversi/Othello")

# Font settings
FONT = pygame.font.Font(None, 30)
WIN_FONT = pygame.font.Font(None, 50)

# Global variables
BOARD = None
BOT = None
DEPTH = None
CURR = None
RESET = True

def bot_selection_screen():
    """
    Choose bot and depth if applicable.
    """
    global BOT, DEPTH
    BOT = None
    DEPTH = None
    
    WIN.fill(GREEN)
    text_surface = FONT.render("Choose Bot", True, WHITE)
    WIN.blit(text_surface, (WIDTH // 2 - 70, HEIGHT // 2 - 140))

    button_no_bot = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 - 80, 120, 40)
    button_black_bot = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 - 20, 120, 40)
    button_white_bot = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 40, 120, 40)

    pygame.draw.rect(WIN, BLACK, button_no_bot, 2)
    pygame.draw.rect(WIN, BLACK, button_black_bot, 2)
    pygame.draw.rect(WIN, BLACK, button_white_bot, 2)

    text_no_bot = FONT.render("No Bot", True, WHITE)
    text_black_bot = FONT.render("Black Bot", True, WHITE)
    text_white_bot = FONT.render("White Bot", True, WHITE)

    WIN.blit(text_no_bot, (WIDTH // 2 - 43, HEIGHT // 2 - 70))
    WIN.blit(text_black_bot, (WIDTH // 2 - 57, HEIGHT // 2 - 10))
    WIN.blit(text_white_bot, (WIDTH // 2 - 58, HEIGHT // 2 + 50))
    
    pygame.display.update()
    
    while BOT == None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_no_bot.collidepoint(mouse_pos):
                    BOT = EMPTY
                    bot_selected = True
                elif button_black_bot.collidepoint(mouse_pos):
                    BOT = PLAYER_BLACK
                    bot_selected = True
                elif button_white_bot.collidepoint(mouse_pos):
                    BOT = PLAYER_WHITE
                    bot_selected = True
                
    if BOT == EMPTY:
        return
    
    WIN.fill(GREEN)
    text_surface_depth = FONT.render("Choose Depth Level (1-6)", True, WHITE)
    WIN.blit(text_surface_depth, (WIDTH // 2 - 130, HEIGHT // 2 - 140))

    for i in range(1, 7):
        button_depth = pygame.Rect(WIDTH // 2 - 150 + (i - 1) * 50, HEIGHT // 2 - 80, 40, 40)
        pygame.draw.rect(WIN, BLACK, button_depth, 2)
        text_depth = FONT.render(str(i), True, WHITE)
        WIN.blit(text_depth, (WIDTH // 2 - 135 + (i - 1) * 50, HEIGHT // 2 - 70))
        
    pygame.display.update()
    
    while DEPTH == None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i in range(1, 7):
                    button_depth = pygame.Rect(WIDTH // 2 - 150 + (i - 1) * 50, HEIGHT // 2 - 80, 40, 40)
                    if button_depth.collidepoint(mouse_pos):
                        DEPTH = i
                        

def draw_board():
    """
    Draw the game board and important information.
    """
    WIN.fill(GREEN)
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.rect(WIN, BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)
            if BOARD[row][col] == PLAYER_WHITE:
                pygame.draw.circle(WIN, WHITE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 2)
            elif BOARD[row][col] == PLAYER_BLACK:
                pygame.draw.circle(WIN, BLACK, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 2)

    valid_color = DARKGREEN if CURR == PLAYER_BLACK else LIGHTGREEN
    moves = get_valid_moves(CURR, BOARD)
    for move in moves:
        row, col = move
        pygame.draw.circle(WIN, valid_color, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 2)

    white_points = np.count_nonzero(BOARD == PLAYER_WHITE)
    black_points = np.count_nonzero(BOARD == PLAYER_BLACK)
    text_surface_white = FONT.render("White: {}".format(white_points), True, WHITE)
    text_surface_black = FONT.render("Black: {}".format(black_points), True, BLACK)
    WIN.blit(text_surface_white, (10, HEIGHT + BOTTOM_OFFSET - 55))
    WIN.blit(text_surface_black, (10, HEIGHT + BOTTOM_OFFSET - 25))

    restart_button = pygame.Rect(WIDTH - 120, HEIGHT + BOTTOM_OFFSET - 50, 100, 40)
    pygame.draw.rect(WIN, BLACK, restart_button, 2)
    restart_text = FONT.render("Restart", True, WHITE)
    WIN.blit(restart_text, (WIDTH - 105, HEIGHT + BOTTOM_OFFSET - 40))

    player_name = "Black" if CURR == PLAYER_BLACK else "White"
    if moves:
        text_surface = FONT.render("Turn: {} ".format(player_name), True, WHITE)
        WIN.blit(text_surface, (150, HEIGHT + BOTTOM_OFFSET - 55))
    else:
        if get_valid_moves(1 - CURR, BOARD):
            no_moves_text = FONT.render("No Valid Moves for {}".format(player_name), True, WHITE)
            WIN.blit(no_moves_text, (150, HEIGHT + BOTTOM_OFFSET - 55))
            continue_button = pygame.Rect(150, HEIGHT + BOTTOM_OFFSET - 30, 246, 27)
            pygame.draw.rect(WIN, BLACK, continue_button, 2)
            continue_text = FONT.render("Click Here to Continue", True, WHITE)
            WIN.blit(continue_text, (163, HEIGHT + BOTTOM_OFFSET - 25))
        else:
            if white_points > black_points:
                winner_text = "White Wins!"
            elif black_points > white_points:
                winner_text = "Black Wins!"
            else:
                winner_text = "It's a Tie!"
            text_surface_winner = WIN_FONT.render(winner_text, True, WHITE)
            WIN.blit(text_surface_winner, (150, HEIGHT + BOTTOM_OFFSET - 45))
        
    pygame.display.update()
    

def get_valid_moves(player, board):
    """
    Calculate valid moves, ordered descending by chips gained to help MinMax algorithm.
    """
    moves_dict = {}
    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] == player:
                for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    x, y = i + dx, j + dy
                    chips = 0
                    while 0 <= x < ROWS and 0 <= y < COLS and board[x][y] == 1 - player:
                        chips +=1
                        x += dx
                        y += dy
                    if 0 <= x < ROWS and 0 <= y < COLS and board[x][y] == -1 and chips > 0:
                        moves_dict[(x,y)] = moves_dict.get((x,y),0) + chips
                        
    moves_sorted = sorted(moves_dict.items(), key=lambda x: x[1], reverse=True)
    moves = set(moves_sorted[i][0] for i in range(len(moves_sorted)))
    return moves


def flip_pieces(player, row, col, board):
    """
    Flip pieces on the board and for the MinMax algorithm.
    """
    board[row][col] = player
    for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
        x, y = row + dx, col + dy
        to_flip = []
        while 0 <= x < ROWS and 0 <= y < COLS and board[x][y] == 1 - player:
            to_flip.append((x, y))
            x += dx
            y += dy
        if 0 <= x < ROWS and 0 <= y < COLS and board[x][y] == player:
            for i, j in to_flip:
                board[i][j] = player


def handle_mouse_input():
    """
    Handle mouse input for making moves, continuing after no move, reseting, and quitting.
    """
    global RESET
    moves = get_valid_moves(CURR, BOARD)
    restart_button = pygame.Rect(WIDTH - 120, HEIGHT + BOTTOM_OFFSET - 50, 100, 40)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if (moves):
                    row, col = mouse_pos[1] // SQUARE_SIZE, mouse_pos[0] // SQUARE_SIZE
                    if (row, col) in moves:
                        flip_pieces(CURR, row, col, BOARD)
                        return
                else:
                    continue_button = pygame.Rect(150, HEIGHT + BOTTOM_OFFSET - 30, 246, 27)
                    if continue_button.collidepoint(mouse_pos):
                        return
                if restart_button.collidepoint(mouse_pos):
                    RESET = True
                    return

def reset():
    """
    Reset the game
    """
    transposition_table.clear()    
    global BOARD, CURR, RESET
    BOARD = np.full((ROWS, COLS), EMPTY)
    BOARD[3][3] = PLAYER_WHITE
    BOARD[4][4] = PLAYER_WHITE
    BOARD[3][4] = PLAYER_BLACK
    BOARD[4][3] = PLAYER_BLACK
    CURR = PLAYER_BLACK
    RESET = False
    bot_selection_screen()

def end_game():
    """
    End the game and exit gracefully.
    """
    pygame.quit()
    sys.exit()


def evaluate_board(board):
    """
    Evaluate the board and return a score for MinMax.
    """
    bot_tiles = np.sum(board == BOT)
    player_tiles = np.sum(board == 1-BOT)
    return bot_tiles - player_tiles

transposition_table = {}
def minmax(board, depth, player, alpha, beta):
    """
    Implement the MinMax algorithm with alpha-beta pruning and transposition table.
    """
    valid_moves = get_valid_moves(player, board)
    board_hash = hash(board.tobytes())

    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        if entry['depth'] >= depth:
            return entry['score'], entry['move']

    if depth == 0 or not valid_moves:
        score = evaluate_board(board)
        transposition_table[board_hash] = {'depth': depth, 'score': score, 'move': None}
        return score, None

    best_move = None

    if player == BOT:
        best_score = float('-inf')
        for move in valid_moves:
            new_board = board.copy()
            flip_pieces(player, move[0], move[1], new_board)
            score, _ = minmax(new_board, depth - 1, 1 - BOT, alpha, beta)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
    else:
        best_score = float('inf')
        for move in valid_moves:
            new_board = board.copy()
            flip_pieces(player, move[0], move[1], new_board)
            score, _ = minmax(new_board, depth - 1, BOT, alpha, beta)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if alpha >= beta:
                break

    transposition_table[board_hash] = {'depth': depth, 'score': best_score, 'move': best_move}
    return best_score, best_move
     
def main():
    """
    Main function to run the game loop.
    """
    global CURR
    while True:
        if RESET:
            reset()
        draw_board()
        if CURR == BOT:
            _, minmax_move = minmax(BOARD, DEPTH, CURR, float('-inf'), float('inf'))
            if minmax_move:
                flip_pieces(BOT, minmax_move[0], minmax_move[1], BOARD)
        else:
            handle_mouse_input()
        CURR = 1 - CURR


if __name__ == "__main__":
    main()