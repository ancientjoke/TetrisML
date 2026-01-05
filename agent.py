 
import torch
import random
from logic import possible_moves, get_metrics
from collections import deque
from model import Model, Trainer

MAX_MEM = 100000
BATCH_SIZE = 5000
LR = .001

class Agent:
    def __init__(self, board):
        self.board = board
        self.games = 0
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        self.gamma = 0.98 
        self.memory = deque(maxlen=MAX_MEM)
        self.model = Model(13, 256, 128, 4)
        self.trainer = Trainer(self.model, lr=LR, gamma=self.gamma)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        for entry in mini_sample:
            state, action, reward, next_state, done = entry
            self.trainer.train_step(state, action, reward, next_state, done)

    def get_move(self, possible):
        # Epsilon-greedy with decay
        if random.random() < self.epsilon:
            move = random.choice(list(possible.keys()))
        else:
            best_output = float('-inf')
            best_move = None
            for move in possible:
                board = possible[move]
                metrics = get_metrics(board.state)
                metrics.append(board.score - self.board.score)
                input_tensor = torch.tensor(metrics, dtype=torch.float)
                pred = self.model(input_tensor)
                pred_value = pred.max().item() if pred.numel() > 1 else pred.item()
                if pred_value > best_output:
                    best_output = pred_value
                    best_move = move
            move = best_move
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        return move

    def train(self, piece):
        old_state = get_metrics(self.board.state)
        old_score = self.board.score
        move_options = possible_moves(piece, self.board)
        move = self.get_move(move_options)
        done = not self.board.update()
        new_score = self.board.score
        new_state = get_metrics(self.board.state)
        old_state.append(new_score - old_score)
        new_state.append(new_score - old_score)
        reward = improved_reward(move_options[move].state, old_score, new_score)
        self.remember(old_state, move, reward, new_state, done)
        self.train_short_memory(old_state, move, reward, new_state, done)
        if done:
            self.train_long_memory()
            self.games += 1
        return move

def improved_reward(board_state, old_score, new_score):
    metrics = get_metrics(board_state)
    holes = metrics[0]
    bumpiness = metrics[2]
    heights = metrics[3:]
    max_height = max(heights) if heights else 0
    # Reward for clearing lines
    line_reward = 10 * (new_score - old_score)
    # Penalty for holes and bumpiness
    penalty = -2 * holes - 0.5 * bumpiness
    # Encourage lower placement
    lower_bonus = -0.2 * max_height
    # Encourage filling lower rows (more negative max_height = better)
    return line_reward + penalty + lower_bonus
