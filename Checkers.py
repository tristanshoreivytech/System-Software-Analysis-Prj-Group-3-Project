import pygame
import sys
import time
import random
import copy

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
BACKGROUND_COLOR = (121, 144, 104)  # Color #799068
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
FONT_SIZE = 36

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
screen_width, screen_height = screen.get_size()
font = pygame.font.Font(None, FONT_SIZE)

# Calculate board position for centering
board_width = BOARD_SIZE * SQUARE_SIZE
board_height = BOARD_SIZE * SQUARE_SIZE
board_x_offset = (screen_width - board_width) // 2
board_y_offset = (screen_height - board_height) // 2

# Game states
STATE_MAIN_MENU = "main_menu"
STATE_PLAYER_SETUP = "player_setup"
STATE_BOT_SETUP = "bot_setup"
STATE_DIFFICULTY_SELECTION = "difficulty_selection"
STATE_GAME = "game"
STATE_WINNER = "winner"
game_state = STATE_MAIN_MENU
winner_message = ""

# Input fields for player names
player1_name = ""
player2_name = ""
active_input = None  # Track which input is active

# Player colors and turn
player1_color = BLACK
player2_color = RED
current_turn = BLACK  # Start with Player 1

# Piece types for clarity
BLACK_PIECE = "B"
RED_PIECE = "R"
BLACK_KING = "BK"
RED_KING = "RK"

# Pieces
black_piece = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
pygame.draw.circle(black_piece, BLACK, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 10)
red_piece = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
pygame.draw.circle(red_piece, RED, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 10)

# Board setup
board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
selected_piece = None
invalid_move_timer = None  # Timer for displaying "X" for invalid moves

#bot settings
bot_game = False
bot_difficulty = None
bot_color = BLACK

# Functions
def initialize_board():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if row < 3 and (row + col) % 2 != 0:
                board[row][col] = BLACK_PIECE  # Black piece
            elif row > 4 and (row + col) % 2 != 0:
                board[row][col] = RED_PIECE  # Red piece

def switch_turn():
    global current_turn
    current_turn = RED if current_turn == BLACK else BLACK

def get_square_under_mouse():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    row = (mouse_y - board_y_offset) // SQUARE_SIZE
    col = (mouse_x - board_x_offset) // SQUARE_SIZE
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return row, col
    return None, None

def is_valid_move(start, end):
    """Validate the move according to checkers rules, including simple moves and captures."""
    start_row, start_col = start
    end_row, end_col = end
    piece = board[start_row][start_col]
    direction = 1 if piece in [BLACK_PIECE, BLACK_KING] else -1  # Black moves down, red moves up
    
    king_piece = (piece == BLACK_KING or piece == RED_KING)

    # Move must be diagonal
    if abs(start_col - end_col) != abs(start_row - end_row):
        return False

    # Regular move
    if abs(start_row - end_row) == 1 and board[end_row][end_col] is None:
        # Single piece can only move forward, while king can move in any direction
        if piece in [BLACK_PIECE, RED_PIECE] and end_row - start_row != direction:
            return False
        return True

    # Capture move
    elif abs(start_row - end_row) == 2:
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        mid_piece = board[mid_row][mid_col]
        if mid_piece and (piece in [BLACK_PIECE, BLACK_KING] and mid_piece in [RED_PIECE, RED_KING]) or \
           (piece in [RED_PIECE, RED_KING] and mid_piece in [BLACK_PIECE, BLACK_KING]):
            # Ensure regular pieces can only capture forward
            if not king_piece and (end_row - start_row != 2 * direction):
                return False
            # Ensure the destination is empty
            if board[end_row][end_col] is None:
                return True

    return False

def get_valid_moves(color):
    """Get all valid moves for a given color"""
    valid_moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and ((piece in [BLACK_PIECE, BLACK_KING] and color == BLACK) or (piece in [RED_PIECE, RED_KING] and color == RED)):
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                        if board[new_row][new_col] is None and is_valid_move((row, col), (new_row, new_col)):
                            valid_moves.append(((row, col), (new_row, new_col)))
                    new_row, new_col = row + 2*dr, col + 2*dc
                    if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                        if board[new_row][new_col] is None and is_valid_move((row, col), (new_row, new_col)):
                            valid_moves.append(((row, col), (new_row, new_col)))
    return valid_moves

def check_for_king(row, col):
    """Promote to king if reaching the opposite side"""
    piece = board[row][col]
    if piece == BLACK_PIECE and row == BOARD_SIZE - 1:
        board[row][col] = BLACK_KING
    elif piece == RED_PIECE and row == 0:
        board[row][col] = RED_KING

def check_for_winner():
    """Count pieces and set the winner if one player has no pieces left"""
    global game_state, winner_message
    black_pieces = sum(row.count(BLACK_PIECE) + row.count(BLACK_KING) for row in board)
    red_pieces = sum(row.count(RED_PIECE) + row.count(RED_KING) for row in board)

    if black_pieces == 0:
        winner_message = f"{player2_name if player2_color == RED else player1_name} is the Winner!"
        game_state = STATE_WINNER
    elif red_pieces == 0:
        winner_message = f"{player1_name if player1_color == BLACK else player2_name} is the Winner!"
        game_state = STATE_WINNER

def draw_invalid_move_marker(row, col):
    x_pos = col * SQUARE_SIZE + board_x_offset + SQUARE_SIZE // 2
    y_pos = row * SQUARE_SIZE + board_y_offset + SQUARE_SIZE // 2
    pygame.draw.line(screen, RED, (x_pos - 15, y_pos - 15), (x_pos + 15, y_pos + 15), 3)
    pygame.draw.line(screen, RED, (x_pos - 15, y_pos + 15), (x_pos + 15, y_pos - 15), 3)

def draw_main_menu():
    screen.fill(BACKGROUND_COLOR)
    local_play_text = font.render("Local Play", True, BLACK)
    bot_play_text = font.render("Bot Play", True, BLACK)
    quit_text = font.render("Quit", True, BLACK)
    
    SELECTION_BACKGROUND_COLOR = (217, 217, 217)  # Color D9D9D9

    # Calculate background rectangles for each menu option
    local_play_rect = pygame.Rect(
        screen_width // 2 - local_play_text.get_width() // 2 - 20,
        screen_height // 2 - 100 - 10,
        local_play_text.get_width() + 40,
        local_play_text.get_height() + 20
    )
    bot_play_rect = pygame.Rect(
        screen_width // 2 - bot_play_text.get_width() // 2 - 20,
        screen_height // 2 - 10,
        bot_play_text.get_width() + 40,
        bot_play_text.get_height() + 20
    )
    quit_rect = pygame.Rect(
        screen_width // 2 - quit_text.get_width() // 2 - 20,
        screen_height // 2 + 100 - 10,
        quit_text.get_width() + 40,
        quit_text.get_height() + 20
    )

    # Draw rounded rectangles as background for each menu option
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, local_play_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, bot_play_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, quit_rect, border_radius=15)

    # Draw text on top of each background rectangle
    screen.blit(local_play_text, (local_play_rect.x + 20, local_play_rect.y + 10))
    screen.blit(bot_play_text, (bot_play_rect.x + 20, bot_play_rect.y + 10))
    screen.blit(quit_text, (quit_rect.x + 20, quit_rect.y + 10))

def draw_player_setup():
    global active_input, player1_name, player2_name
    screen.fill(BACKGROUND_COLOR)
    SELECTION_BACKGROUND_COLOR = (217, 217, 217)  # Color D9D9D9

    # Text elements for labels
    player1_text = font.render("Player 1 Name:", True, BLACK)
    player2_text = font.render("Player 2 Name:", True, BLACK)
    select_color_text = font.render("Select Color:", True, BLACK)
    start_text = font.render("Start Game", True, BLACK)
    back_text = font.render("Back", True, BLACK)
    
    # Background rectangles for labels
    player1_label_rect = pygame.Rect(screen_width // 2 - 200, screen_height // 2 - 200, player1_text.get_width() + 220, player1_text.get_height() + 20)
    player2_label_rect = pygame.Rect(screen_width // 2 - 200, screen_height // 2 - 100, player2_text.get_width() + 220, player2_text.get_height() + 20)
    start_rect = pygame.Rect(screen_width // 2 - start_text.get_width() // 2 - 20, screen_height // 2 + 200, start_text.get_width() + 40, start_text.get_height() + 20)
    back_rect = pygame.Rect(screen_width // 2 - back_text.get_width() // 2 - 20, screen_height // 2 + 250, back_text.get_width() + 40, back_text.get_height() + 20)

    # Draw rounded rectangles for labels and buttons
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, player1_label_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, player2_label_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, start_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, back_rect, border_radius=15)

    # Render and position label texts
    screen.blit(player1_text, (player1_label_rect.x + 10, player1_label_rect.y + 10))
    screen.blit(player2_text, (player2_label_rect.x + 10, player2_label_rect.y + 10))
    screen.blit(select_color_text, (screen_width // 2 - select_color_text.get_width() // 2, screen_height // 2 + 10))
    screen.blit(start_text, (start_rect.x + 20, start_rect.y + 10))
    screen.blit(back_text, (back_rect.x + 20, back_rect.y + 10))

    # Draw input boxes with player name texts
    pygame.draw.rect(screen, WHITE, (screen_width // 2, player1_label_rect.y, 200, player1_text.get_height() + 20))
    pygame.draw.rect(screen, WHITE, (screen_width // 2, player2_label_rect.y, 200, player2_text.get_height() + 20))
    player1_name_text = font.render(player1_name, True, BLACK)
    player2_name_text = font.render(player2_name, True, BLACK)
    screen.blit(player1_name_text, (screen_width // 2 + 10, player1_label_rect.y + 10))
    screen.blit(player2_name_text, (screen_width // 2 + 10, player2_label_rect.y + 10))

    # Draw color selection circles
    pygame.draw.circle(screen, BLACK, (screen_width // 2 - 50, screen_height // 2 + 60), 20)
    pygame.draw.circle(screen, RED, (screen_width // 2 + 50, screen_height // 2 + 60), 20)

    # Outline selected color
    if player1_color == BLACK:
        pygame.draw.circle(screen, WHITE, (screen_width // 2 - 50, screen_height // 2 + 60), 25, 2)
    else:
        pygame.draw.circle(screen, WHITE, (screen_width // 2 + 50, screen_height // 2 + 60), 25, 2)

    # Display selected color texts
    player1_color_text = font.render(f"Player 1 Color: {'Black' if player1_color == BLACK else 'Red'}", True, BLACK)
    player2_color_text = font.render(f"Player 2 Color: {'Black' if player2_color == BLACK else 'Red'}", True, BLACK)
    screen.blit(player1_color_text, (screen_width // 2 - player1_color_text.get_width() // 2, screen_height // 2 + 100))
    screen.blit(player2_color_text, (screen_width // 2 - player2_color_text.get_width() // 2, screen_height // 2 + 150))

def draw_bot_setup():
    global active_input, player1_name, player2_name
    screen.fill(BACKGROUND_COLOR)
    SELECTION_BACKGROUND_COLOR = (217, 217, 217)  # Color D9D9D9

    # Text elements for labels
    player1_text = font.render("Player Name:", True, BLACK)
    select_color_text = font.render("Select Color:", True, BLACK)
    start_text = font.render("Start Game", True, BLACK)
    back_text = font.render("Back", True, BLACK)
    
    # Background rectangles for labels
    player1_label_rect = pygame.Rect(screen_width // 2 - 200, screen_height // 2 - 200, player1_text.get_width() + 220, player1_text.get_height() + 20)
    start_rect = pygame.Rect(screen_width // 2 - start_text.get_width() // 2 - 20, screen_height // 2 + 200, start_text.get_width() + 40, start_text.get_height() + 20)
    back_rect = pygame.Rect(screen_width // 2 - back_text.get_width() // 2 - 20, screen_height // 2 + 250, back_text.get_width() + 40, back_text.get_height() + 20)

    # Draw rounded rectangles for labels and buttons
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, player1_label_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, start_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, back_rect, border_radius=15)

    # Render and position label texts
    screen.blit(player1_text, (player1_label_rect.x + 10, player1_label_rect.y + 10))
    screen.blit(select_color_text, (screen_width // 2 - select_color_text.get_width() // 2, screen_height // 2 + 10))
    screen.blit(start_text, (start_rect.x + 20, start_rect.y + 10))
    screen.blit(back_text, (back_rect.x + 20, back_rect.y + 10))

    # Draw input box with player name text
    pygame.draw.rect(screen, WHITE, (screen_width // 2, player1_label_rect.y, 200, player1_text.get_height() + 20))
    player1_name_text = font.render(player1_name, True, BLACK)
    screen.blit(player1_name_text, (screen_width // 2 + 10, player1_label_rect.y + 10))

    # Draw color selection circles
    pygame.draw.circle(screen, BLACK, (screen_width // 2 - 50, screen_height // 2 + 60), 20)
    pygame.draw.circle(screen, RED, (screen_width // 2 + 50, screen_height // 2 + 60), 20)

    # Outline selected color
    if player1_color == BLACK:
        pygame.draw.circle(screen, WHITE, (screen_width // 2 - 50, screen_height // 2 + 60), 25, 2)
    else:
        pygame.draw.circle(screen, WHITE, (screen_width // 2 + 50, screen_height // 2 + 60), 25, 2)

    # Display selected color texts
    bot_color_text = font.render(f"Bot Color: {'Red' if player1_color == BLACK else 'Black'}", True, BLACK)
    screen.blit(bot_color_text, (screen_width // 2 - bot_color_text.get_width() // 2, screen_height // 2 + 100))

def bot_moves():
    global winner_message, game_state
    moves = get_valid_moves(bot_color)
    if not moves:
        # Bot has no valid moves, player wins
        winner_message = f"{player1_name if player1_color == BLACK else player2_name} wins!"
        game_state = STATE_WINNER
        return

    if bot_difficulty == 'easy':
        # Random move
        move = random.choice(moves)
    elif bot_difficulty == 'medium':
        # Use minimax with moderate depth
        _, move = minimax(board, depth=3, alpha=float('-inf'), beta=float('inf'), maximizing_player=True, bot_color=bot_color)
    elif bot_difficulty == 'hard':
        # Use minimax with a deeper search
        _, move = minimax(board, depth=5, alpha=float('-inf'), beta=float('inf'), maximizing_player=True, bot_color=bot_color)

    # Execute move
    (start_row, start_col), (end_row, end_col) = move
    if abs(end_row - start_row) == 2:
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        board[mid_row][mid_col] = None
    board[end_row][end_col] = board[start_row][start_col]
    board[start_row][start_col] = None
    check_for_king(end_row, end_col)
    switch_turn()
    check_for_winner()
            
def evaluate_board(board, bot_color):
    black_pieces = 0
    red_pieces = 0
    
    for row in board:
        for piece in row:
            if piece == BLACK_PIECE:
                black_pieces += 1
            elif piece == RED_PIECE:
                red_pieces += 1
            elif piece == BLACK_KING:
                black_pieces += 1.5
            elif piece == RED_KING:
                red_pieces += 1.5
                
    if bot_color == BLACK:
        return black_pieces - red_pieces
    else:
        return red_pieces - black_pieces
    
def make_move(board, move):
        new_board = copy.deepcopy(board)
        (start_row, start_col), (end_row, end_col) = move
        piece = new_board[start_row][start_col]
        new_board[start_row][start_col] = None
        new_board[end_row][end_col] = piece
        
        if abs(end_row - start_row) == 2:
            mid_row = (start_row + end_row) // 2
            mid_col = (start_col + end_col) // 2
            new_board[mid_row][mid_col] = None
            
        if piece == BLACK_PIECE and end_row == BOARD_SIZE - 1:
            new_board[end_row][end_col] = BLACK_KING
        elif piece == RED_PIECE and end_row == 0:
            new_board[end_row][end_col] = RED_KING
            
        return new_board
    
def minimax(board, depth, alpha, beta, maximizing_player, bot_color):
    if depth == 0 or game_over(board):
        return evaluate_board(board, bot_color), None

    current_color = bot_color if maximizing_player else (RED if bot_color == BLACK else BLACK)
    moves = get_valid_moves(current_color)
    
    if not moves:
        return evaluate_board(board, bot_color), None

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            new_board = make_move(board, move)
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, bot_color)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            new_board = make_move(board, move)
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, bot_color)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move    

def draw_difficulty_selection():
    screen.fill(BACKGROUND_COLOR)
    SELECTION_BACKGROUND_COLOR = (217, 217, 217)  # Color D9D9D9

    # Text elements
    easy_text = font.render("Easy", True, BLACK)
    medium_text = font.render("Medium", True, BLACK)
    hard_text = font.render("Hard", True, BLACK)
    back_text = font.render("Back", True, BLACK)

    # Background rectangles for each option
    easy_rect = pygame.Rect(screen_width // 2 - easy_text.get_width() // 2 - 20, screen_height // 2 - 100, easy_text.get_width() + 40, easy_text.get_height() + 20)
    medium_rect = pygame.Rect(screen_width // 2 - medium_text.get_width() // 2 - 20, screen_height // 2, medium_text.get_width() + 40, medium_text.get_height() + 20)
    hard_rect = pygame.Rect(screen_width // 2 - hard_text.get_width() // 2 - 20, screen_height // 2 + 100, hard_text.get_width() + 40, hard_text.get_height() + 20)
    back_rect = pygame.Rect(screen_width // 2 - back_text.get_width() // 2 - 20, screen_height // 2 + 200, back_text.get_width() + 40, back_text.get_height() + 20)

    # Draw rounded rectangles as backgrounds
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, easy_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, medium_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, hard_rect, border_radius=15)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, back_rect, border_radius=15)

    # Render and position text elements
    screen.blit(easy_text, (easy_rect.x + 20, easy_rect.y + 10))
    screen.blit(medium_text, (medium_rect.x + 20, medium_rect.y + 10))
    screen.blit(hard_text, (hard_rect.x + 20, hard_rect.y + 10))
    screen.blit(back_text, (back_rect.x + 20, back_rect.y + 10))


def draw_board():
    screen.fill(BACKGROUND_COLOR)
    SELECTION_BACKGROUND_COLOR = (217, 217, 217)  # Color D9D9D9

    # Draw board squares and pieces
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, 
                             (col * SQUARE_SIZE + board_x_offset, row * SQUARE_SIZE + board_y_offset, 
                              SQUARE_SIZE, SQUARE_SIZE))
            piece = board[row][col]
            if piece in [BLACK_PIECE, BLACK_KING]:
                screen.blit(black_piece, (col * SQUARE_SIZE + board_x_offset, row * SQUARE_SIZE + board_y_offset))
                if piece == BLACK_KING:
                    pygame.draw.circle(screen, WHITE, (col * SQUARE_SIZE + board_x_offset + SQUARE_SIZE // 2, 
                                                       row * SQUARE_SIZE + board_y_offset + SQUARE_SIZE // 2), 10)
            elif piece in [RED_PIECE, RED_KING]:
                screen.blit(red_piece, (col * SQUARE_SIZE + board_x_offset, row * SQUARE_SIZE + board_y_offset))
                if piece == RED_KING:
                    pygame.draw.circle(screen, WHITE, (col * SQUARE_SIZE + board_x_offset + SQUARE_SIZE // 2, 
                                                       row * SQUARE_SIZE + board_y_offset + SQUARE_SIZE // 2), 10)

    # Define player name text and turn indicator triangle color
    player1_text = font.render(player1_name, True, player1_color)
    player2_text = font.render(player2_name, True, player2_color)
    triangle_color = BLACK if current_turn == BLACK else RED

    # Position the names and turn indicator triangle based on color selection
    if player1_color == RED:
        # Draw rounded background for Player 1 name at the bottom
        player1_name_rect = pygame.Rect(screen_width // 2 - player1_text.get_width() // 2 - 20, board_y_offset + board_height + 10, player1_text.get_width() + 40, player1_text.get_height() + 20)
        pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, player1_name_rect, border_radius=15)
        screen.blit(player1_text, (player1_name_rect.x + 20, player1_name_rect.y + 10))
        
        # Draw rounded background for Player 2 name at the top
        player2_name_rect = pygame.Rect(screen_width // 2 - player2_text.get_width() // 2 - 20, board_y_offset - 60, player2_text.get_width() + 40, player2_text.get_height() + 20)
        pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, player2_name_rect, border_radius=15)
        screen.blit(player2_text, (player2_name_rect.x + 20, player2_name_rect.y + 10))
    else:
        # Draw rounded background for Player 1 name at the top
        player1_name_rect = pygame.Rect(screen_width // 2 - player1_text.get_width() // 2 - 20, board_y_offset - 60, player1_text.get_width() + 40, player1_text.get_height() + 20)
        pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, player1_name_rect, border_radius=15)
        screen.blit(player1_text, (player1_name_rect.x + 20, player1_name_rect.y + 10))

        # Draw rounded background for Player 2 name at the bottom
        player2_name_rect = pygame.Rect(screen_width // 2 - player2_text.get_width() // 2 - 20, board_y_offset + board_height + 10, player2_text.get_width() + 40, player2_text.get_height() + 20)
        pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, player2_name_rect, border_radius=15)
        screen.blit(player2_text, (player2_name_rect.x + 20, player2_name_rect.y + 10))

    # Draw turn indicator triangle next to active player name
    triangle_points = []
    if current_turn == BLACK:
        triangle_points = [
            (player1_name_rect.x - 30, player1_name_rect.y + 20),   # top
            (player1_name_rect.x - 10, player1_name_rect.y + 10),   # bottom left
            (player1_name_rect.x - 10, player1_name_rect.y + 30)    # bottom right
        ]
    else:
        triangle_points = [
            (player2_name_rect.x - 30, player2_name_rect.y + 20),   # top
            (player2_name_rect.x - 10, player2_name_rect.y + 10),   # bottom left
            (player2_name_rect.x - 10, player2_name_rect.y + 30)    # bottom right
        ]
    pygame.draw.polygon(screen, triangle_color, triangle_points)

    # Draw "Back" button with rounded background
    back_text = font.render("Back", True, BLACK)
    back_rect = pygame.Rect(screen_width - 150, screen_height - 50, back_text.get_width() + 40, back_text.get_height() + 20)
    pygame.draw.rect(screen, SELECTION_BACKGROUND_COLOR, back_rect, border_radius=15)
    screen.blit(back_text, (back_rect.x + 20, back_rect.y + 10))


def draw_winner_screen():
    """Displays the winner message and option to return to the main menu."""
    screen.fill(BACKGROUND_COLOR)
    win_text = font.render(winner_message, True, BLACK)
    screen.blit(win_text, (screen_width // 2 - win_text.get_width() // 2, screen_height // 2 - FONT_SIZE // 2))

    # Option to return to main menu
    main_menu_text = font.render("Return to Main Menu", True, BLACK)
    screen.blit(main_menu_text, (screen_width // 2 - main_menu_text.get_width() // 2, screen_height // 2 + 50))

def game_over(board):
    black_moves = get_valid_moves(BLACK)
    red_moves = get_valid_moves(RED)
    if not black_moves or not red_moves:
        return True
    return False

# Main game loop
running = True
initialize_board()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            y_start = screen_height // 2 - 200  # Define y_start within the main loop
            if game_state == STATE_MAIN_MENU:
                player1_name = ""
                player2_name = ""
                bot_game = False
                active_input = None
                if screen_height // 2 - 100 <= mouse_y <= screen_height // 2 - 60:
                    game_state = STATE_PLAYER_SETUP
                elif screen_height // 2 <= mouse_y <= screen_height // 2 + 40:
                    game_state = STATE_DIFFICULTY_SELECTION
                elif screen_height // 2 + 100 <= mouse_y <= screen_height // 2 + 140:
                    pygame.quit()
                    sys.exit()
            elif game_state == STATE_PLAYER_SETUP:
                if y_start <= mouse_y <= y_start + 40 and screen_width // 2 <= mouse_x <= screen_width // 2 + 200:
                    active_input = "player1"
                elif y_start + 100 <= mouse_y <= y_start + 140 and screen_width // 2 <= mouse_x <= screen_width // 2 + 200:
                    active_input = "player2"
                elif y_start + 250 - 20 <= mouse_y <= y_start + 250 + 20:
                    if screen_width // 2 - 50 - 20 <= mouse_x <= screen_width // 2 - 50 + 20:
                        player1_color, player2_color = BLACK, RED
                    elif screen_width // 2 + 50 - 20 <= mouse_x <= screen_width // 2 + 50 + 20:
                        player1_color, player2_color = RED, BLACK
                elif y_start + 400 <= mouse_y <= y_start + 440:
                    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
                    initialize_board()
                    current_turn = BLACK
                    selected_piece = None
                    bot_game = False
                    game_state = STATE_GAME
                elif y_start + 450 <= mouse_y <= y_start + 490:
                    game_state = STATE_MAIN_MENU
            elif game_state == STATE_BOT_SETUP:
                if y_start <= mouse_y <= y_start + 40 and screen_width // 2 <= mouse_x <= screen_width // 2 + 200:
                    active_input = "player1"
                elif y_start + 250 - 20 <= mouse_y <= y_start + 250 +20:
                    if screen_width // 2 - 50 - 20 <= mouse_x <= screen_width // 2 - 50 + 20:
                        player1_color, bot_color = BLACK, RED
                    elif screen_width // 2 + 50 - 20 <= mouse_x <= screen_width // 2 + 50 + 20:
                        player1_color, bot_color = RED, BLACK
                elif y_start + 400 <= mouse_y <= y_start + 440:
                    player2_name = f"{bot_difficulty.capitalize()} Bot"
                    player2_color = bot_color
                    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
                    initialize_board()
                    current_turn = player1_color
                    selected_piece = None
                    game_state = STATE_GAME
                elif y_start + 450 <= mouse_y <= y_start + 490:
                    game_state = STATE_MAIN_MENU
            elif game_state == STATE_DIFFICULTY_SELECTION:
                y_start = screen_height // 2 - 100
                if y_start <= mouse_y <= screen_height // 2 + 40:
                    bot_game = True
                    bot_difficulty = 'easy'         # easy bot game
                    game_state = STATE_BOT_SETUP
                elif y_start +100 <= mouse_y <= screen_height // 2 + 140:
                    bot_game = True
                    bot_difficulty = 'medium'       # medium bot game
                    game_state = STATE_BOT_SETUP
                elif y_start + 200 <= mouse_y <= screen_height // 2 + 240:
                    bot_game = True
                    bot_difficulty = 'hard'         # hard bot game
                    game_state = STATE_BOT_SETUP
                elif y_start + 300 <= mouse_y <= screen_height // 2 + 340:
                    game_state = STATE_MAIN_MENU
            elif game_state == STATE_GAME:
                row, col = get_square_under_mouse()
                if row is not None and col is not None:
                    if selected_piece:
                        if is_valid_move(selected_piece, (row, col)):
                            old_row, old_col = selected_piece
                            if abs(row - old_row) == 2:
                                mid_row = (old_row +row) // 2
                                mid_col = (old_col + col) // 2
                                board[mid_row][mid_col] = None
                            board[row][col] = board[old_row][old_col]
                            board[old_row][old_col] = None
                            check_for_king(row, col)
                            selected_piece = None
                            switch_turn()
                            check_for_winner()  # Check for a winner after each valid move
                        else:
                            invalid_move_timer = {"position": (row, col), "start_time": time.time()}
                            selected_piece = None
                    elif board[row][col] and ((board[row][col] in [BLACK_PIECE, BLACK_KING] and current_turn == BLACK) or (board[row][col] in [RED_PIECE, RED_KING] and current_turn == RED)):
                        selected_piece = (row, col)
                elif screen_width - 150 <= mouse_x <= screen_width - 50 and screen_height - 50 <= mouse_y <= screen_height - 20:
                    game_state = STATE_MAIN_MENU
            elif game_state == STATE_WINNER:
                # If on the winner screen, check if the player clicks to return to the main menu
                main_menu_text = font.render("Return to Main Menu", True, BLACK)
                if screen_width // 2 - main_menu_text.get_width() // 2 <= mouse_x <= screen_width // 2 + main_menu_text.get_width() // 2 and \
                   screen_height // 2 + 50 <= mouse_y <= screen_height // 2 + 50 + FONT_SIZE:
                    game_state = STATE_MAIN_MENU

        elif event.type == pygame.KEYDOWN and active_input:
            if event.key == pygame.K_BACKSPACE:
                if active_input == "player1":
                    player1_name = player1_name[:-1]
                elif active_input == "player2":
                    player2_name = player2_name[:-1]
            elif event.unicode.isprintable():
                if active_input == "player1" and len(player1_name) < 10:
                    player1_name += event.unicode
                elif active_input == "player2" and len(player2_name) < 10:
                    player2_name += event.unicode
                    
    if game_state == STATE_GAME and bot_game and current_turn == bot_color:
        bot_moves()

    if invalid_move_timer and time.time() - invalid_move_timer["start_time"] > 2:
        invalid_move_timer = None

    if game_state == STATE_MAIN_MENU:
        draw_main_menu()
    elif game_state == STATE_PLAYER_SETUP:
        draw_player_setup()
    elif game_state == STATE_BOT_SETUP:
        draw_bot_setup()
    elif game_state == STATE_DIFFICULTY_SELECTION:
        draw_difficulty_selection()
    elif game_state == STATE_GAME:
        draw_board()
    elif game_state == STATE_WINNER:
        draw_winner_screen()

    pygame.display.flip()
