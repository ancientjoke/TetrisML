import pygame
import logic
from logic import rotate, move_left, move_right, drop_down, make_random_piece, get_cpu_move
from collections import deque
from agent import Agent

BLOCK_SIZE = logic.BLOCK_SIZE
SCREEN_SIZE = (720, 1280)

'''
test_board = Board()
for i in range(3):
    test_board.state[17][i] = 'green'
test_piece = Piece(test_board.rows, test_board.cols, 'line')
pprint.pprint(possible_moves(test_piece, test_board))
'''

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE[0], SCREEN_SIZE[1]))
    clock = pygame.time.Clock()
    # Human player setup
    board_human = logic.Board()
    board_screen_human = pygame.Surface((BLOCK_SIZE * board_human.cols, BLOCK_SIZE * board_human.rows))
    white_box_human = pygame.Rect(0, 0, BLOCK_SIZE * board_human.cols, BLOCK_SIZE * board_human.rows)
    piece_human = make_random_piece(board_human)
    next_piece_human = make_random_piece(board_human)
    score_font = pygame.font.SysFont("Arial", 40)
    # Computer player setup
    board_cpu = logic.Board()
    board_screen_cpu = pygame.Surface((BLOCK_SIZE * board_cpu.cols, BLOCK_SIZE * board_cpu.rows))
    white_box_cpu = pygame.Rect(0, 0, BLOCK_SIZE * board_cpu.cols, BLOCK_SIZE * board_cpu.rows)
    piece_cpu = make_random_piece(board_cpu)
    next_piece_cpu = make_random_piece(board_cpu)
    agent = Agent(board_cpu)
    cpu_moves = deque()
    moved_down_human = False
    moved_down_cpu = False
    running = True
    frame = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    piece_human, next_piece_human, board_human, moved_down_human = move_down(piece_human, next_piece_human, board_human, moved_down_human)
                elif event.key == pygame.K_RIGHT:
                    move_right(piece_human, board_human)
                elif event.key == pygame.K_LEFT:
                    move_left(piece_human, board_human)
                elif event.key == pygame.K_UP:
                    rotate(piece_human, board_human)
                elif event.key == pygame.K_SPACE:
                    piece_human, next_piece_human, board_human = drop_down(piece_human, next_piece_human, board_human)
        # CPU logic
        if not cpu_moves:
            cpu_move = get_cpu_move(piece_cpu, agent)
            if cpu_move is not None:
                rotation, direction, offset = cpu_move
                neg_mod = {-1: 3, -2: 2, -3: 1}
                diff = rotation - piece_cpu.rotation
                if diff < 0:
                    diff = neg_mod[diff]
                for i in range(diff):
                    cpu_moves.append('rotate')
                for i in range(offset):
                    cpu_moves.append(direction)
                cpu_moves.append('drop')
        if frame % 2 == 0 and cpu_moves:
            next_move = cpu_moves.popleft()
            if next_move == 'rotate':
                rotate(piece_cpu, board_cpu)
            elif next_move == 'l':
                move_left(piece_cpu, board_cpu)
            elif next_move == 'r':
                move_right(piece_cpu, board_cpu)
            else:
                piece_cpu, next_piece_cpu, board_cpu = drop_down(piece_cpu, next_piece_cpu, board_cpu)
        if frame % 15 == 0:
            if not moved_down_human:
                piece_human, next_piece_human, board_human, moved_down_human = move_down(piece_human, next_piece_human, board_human, moved_down_human)
            moved_down_human = False
            if not moved_down_cpu:
                piece_cpu, next_piece_cpu, board_cpu, moved_down_cpu = move_down(piece_cpu, next_piece_cpu, board_cpu, moved_down_cpu)
            moved_down_cpu = False
        # Draw both boards side by side
        screen.fill('black')
        # Human board
        board_screen_human.fill('black')
        for block in piece_human.position:
            cords = logic.convert_cords(block)
            piece_block_object = pygame.Rect(cords[1], cords[0], BLOCK_SIZE-1, BLOCK_SIZE-1)
            pygame.draw.rect(board_screen_human, piece_human.color, piece_block_object)
        ghost_piece_human = logic.Piece(board_human.rows, board_human.cols, piece_human.name)
        ghost_piece_human.position = piece_human.position
        new_position = ghost_piece_human.move('d')
        while board_human.is_legal_position(new_position):
            ghost_piece_human.position = new_position
            new_position = ghost_piece_human.move('d')
        for block in ghost_piece_human.position:
            cords = logic.convert_cords(block)
            ghost_block = pygame.Rect(cords[1], cords[0], BLOCK_SIZE-1, BLOCK_SIZE-1)
            pygame.draw.rect(board_screen_human, 'grey', ghost_block, 1)
        for i, row in enumerate(board_human.state):
            for j, column in enumerate(row):
                if column != None:
                    cords = logic.convert_cords([i, j])
                    board_block_object = pygame.Rect(cords[1], cords[0], BLOCK_SIZE-1, BLOCK_SIZE-1)
                    pygame.draw.rect(board_screen_human, column, board_block_object)
        pygame.draw.rect(board_screen_human, 'white', white_box_human, 1)
        # CPU board
        board_screen_cpu.fill('black')
        for block in piece_cpu.position:
            cords = logic.convert_cords(block)
            piece_block_object = pygame.Rect(cords[1], cords[0], BLOCK_SIZE-1, BLOCK_SIZE-1)
            pygame.draw.rect(board_screen_cpu, piece_cpu.color, piece_block_object)
        ghost_piece_cpu = logic.Piece(board_cpu.rows, board_cpu.cols, piece_cpu.name)
        ghost_piece_cpu.position = piece_cpu.position
        new_position = ghost_piece_cpu.move('d')
        while board_cpu.is_legal_position(new_position):
            ghost_piece_cpu.position = new_position
            new_position = ghost_piece_cpu.move('d')
        for block in ghost_piece_cpu.position:
            cords = logic.convert_cords(block)
            ghost_block = pygame.Rect(cords[1], cords[0], BLOCK_SIZE-1, BLOCK_SIZE-1)
            pygame.draw.rect(board_screen_cpu, 'grey', ghost_block, 1)
        for i, row in enumerate(board_cpu.state):
            for j, column in enumerate(row):
                if column != None:
                    cords = logic.convert_cords([i, j])
                    board_block_object = pygame.Rect(cords[1], cords[0], BLOCK_SIZE-1, BLOCK_SIZE-1)
                    pygame.draw.rect(board_screen_cpu, column, board_block_object)
        pygame.draw.rect(board_screen_cpu, 'white', white_box_cpu, 1)
        # Blit both boards
        margin = 40
        screen.blit(board_screen_human, (margin, (SCREEN_SIZE[1] - BLOCK_SIZE * board_human.rows) // 2))
        screen.blit(board_screen_cpu, (SCREEN_SIZE[0]//2 + margin, (SCREEN_SIZE[1] - BLOCK_SIZE * board_cpu.rows) // 2))
        # Draw scores
        score_human = score_font.render("Human: " + str(board_human.score), True, 'white')
        score_cpu = score_font.render("CPU: " + str(board_cpu.score), True, 'white')
        screen.blit(score_human, (margin, 10))
        screen.blit(score_cpu, (SCREEN_SIZE[0]//2 + margin, 10))
        pygame.display.flip()
        frame += 1
        clock.tick(60)
        frame += 1
        clock.tick(60)
        


def find_white_box_cords(board):
    return ((SCREEN_SIZE[0] - (BLOCK_SIZE * board.cols)) // 2,
             (SCREEN_SIZE[1] - (BLOCK_SIZE * board.rows)) // 2)

def move_down(piece, next_piece, board, moved_down):
    new_position = piece.move('d')
    if board.is_legal_position(new_position):
        moved_down = True
        piece.position = new_position
    else:
        board.place_piece(piece)
        if not board.update():
            board.reset()
        piece = next_piece
        next_piece = make_random_piece(board)
    return piece, next_piece, board, moved_down
    
if __name__ == '__main__':
    main()