def map_direction_to_number(direction):
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

NUM_MODELS = 3

class Model(nn.Module):
    def __init__(self, input_size, hidden1_size, hidden2_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden1_size)
        self.linear2 = nn.Linear(hidden1_size, hidden2_size)
        self.linear3 = nn.Linear(hidden2_size, output_size)
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return self.linear3(x)
    def save(self):
        folder_path = './Models'
        base_model_name, file_ext = 'model', '.pth'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for i in range(1, NUM_MODELS + 1):
            if not os.path.exists(folder_path + '/' + base_model_name + str(i) + file_ext):
                torch.save(self.state_dict(), folder_path + '/' + base_model_name + str(i) + file_ext)
                return
        to_delete = input("All " + str(NUM_MODELS) + " spots are used, which would you like to delete? (Entering a nonvalid model number will delete the current model): ")
        try:
            if int(to_delete) in range(1, NUM_MODELS + 1):
                torch.save(self.state_dict(), folder_path + '/' + base_model_name + to_delete + file_ext)
        except TypeError:
            pass

class Trainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
    def train_step(self, state, action, reward, next_state, done):
        if isinstance(action, tuple):
            direction = map_direction_to_number(action[1])
            action = (action[0], direction, action[2])
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )
        pred = self.model(state)
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            if len(target.shape) == 2:
                if action.shape[-1] == target.shape[1]:
                    action_index = torch.argmax(action[idx]).item() if action[idx].dim() > 0 else action[idx].item()
                else:
                    action_index = torch.argmax(action[idx]).item() if action[idx].numel() > 1 else action[idx].item()
                target[idx][action_index] = Q_new
            else:
                target[idx] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()
def map_direction_to_number(direction):
    directions = {'l': 0, 'r': 1, 'u': 2, 'd': 3}
    return directions[direction]