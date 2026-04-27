"""
=====================================================
RL Agent - Q-Learning for 2048
=====================================================
ML/RL Engineer: RL algorithm implementation
Software Project Management & Technical Monitoring
=====================================================
"""

import numpy as np
import random
import pickle
import os
from collections import defaultdict


class QLearningAgent:
    """
    Q-Learning Agent for 2048 Game
    
    - State: Board hash (4x4 grid)
    - Action: 0=up, 1=down, 2=left, 3=right
    - Reward: Score gained from the move + survival bonus + tile merge bonus
    """

    def __init__(self, learning_rate=0.1, discount_factor=0.95,
                 epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Q-table: defaultdict ile memory efficient
        self.q_table = defaultdict(lambda: np.zeros(4))
        self.actions = [0, 1, 2, 3]  # up, down, left, right

        # Monitoring metrics
        self.training_history = {
            'episode_rewards': [],
            'episode_scores': [],
            'episode_max_tiles': [],
            'episode_moves': [],
            'epsilon_history': [],
            'q_table_size': []
        }

    def _state_to_key(self, state):
        """Board state'i hash'lenebilir key'e çevirir"""
        # Log2 transformation ile state space'i küçültüyoruz
        # 0, 2, 4, 8, ... -> 0, 1, 2, 3, ...
        log_state = np.zeros_like(state)
        log_state[state > 0] = np.log2(state[state > 0]).astype(int)
        return tuple(log_state.flatten())

    def choose_action(self, state, valid_actions=None):
        """
        Epsilon-greedy policy
        - epsilon olasılıkla random action (exploration)
        - 1-epsilon olasılıkla best action (exploitation)
        """
        if valid_actions is None:
            valid_actions = self.actions

        if random.random() < self.epsilon:
            return random.choice(valid_actions)

        state_key = self._state_to_key(state)
        q_values = self.q_table[state_key]

        # Sadece valid action'lar arasında en iyisini seç
        valid_q_values = {a: q_values[a] for a in valid_actions}
        return max(valid_q_values, key=valid_q_values.get)

    def learn(self, state, action, reward, next_state, done):
        """
        Q-Learning update rule:
        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        """
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)

        current_q = self.q_table[state_key][action]

        if done:
            target_q = reward
        else:
            max_next_q = np.max(self.q_table[next_state_key])
            target_q = reward + self.gamma * max_next_q

        # TD Error
        td_error = target_q - current_q
        self.q_table[state_key][action] += self.lr * td_error

    def decay_epsilon(self):
        """Epsilon'u decay ederek zaman içinde exploitation'a geçer"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_model(self, filepath):
        """Q-table'ı kaydeder"""
        with open(filepath, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load_model(self, filepath):
        """Q-table'ı yükler"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                loaded = pickle.load(f)
                self.q_table = defaultdict(lambda: np.zeros(4), loaded)

    def get_stats(self):
        """Model istatistiklerini döndürür"""
        return {
            'q_table_size': len(self.q_table),
            'current_epsilon': self.epsilon,
            'total_episodes': len(self.training_history['episode_rewards'])
        }


def compute_reward(game, score_gained, changed, old_max_tile, new_max_tile):
    """
    Custom Reward Function
    ---------------------
    - Score kazancı: primary reward
    - Yeni max tile: bonus reward (özellikle 2048 için)
    - Invalid move: ceza
    - Game over: büyük ceza (eğer düşük skorsa)
    """
    reward = 0

    # Base reward: score kazancı (log scaled)
    if score_gained > 0:
        reward += np.log2(score_gained + 1)

    # Bonus: yeni bir max tile oluştuysa
    if new_max_tile > old_max_tile:
        reward += np.log2(new_max_tile) * 2

    # Penalty: invalid move (tahta değişmediyse)
    if not changed:
        reward -= 5

    # Game over penalty
    if game.game_over:
        if game.get_max_tile() < 512:
            reward -= 20
        elif game.get_max_tile() >= 2048:
            reward += 100  # 2048'e ulaştık!

    return reward


if __name__ == "__main__":
    # Test agent creation
    agent = QLearningAgent()
    print("RL Agent created successfully")
    print(f"Actions: {agent.actions}")
    print(f"Initial epsilon: {agent.epsilon}")
