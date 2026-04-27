"""
=====================================================
Training Script - Train RL Agent on 2048
=====================================================
ML/RL Engineer: Training pipeline
Software Project Management & Technical Monitoring
=====================================================
"""

import numpy as np
import time
import json
from game_2048 import Game2048
from rl_agent import QLearningAgent, compute_reward


def train_agent(episodes=1000, save_interval=100, verbose=True):
    """
    RL Agent Training Pipeline
    
    Args:
        episodes: Training iteration count
        save_interval: Her X episode'da model kaydet
        verbose: Progress yazdırılacak mı
    
    Returns:
        Trained agent + training history
    """
    game = Game2048()
    agent = QLearningAgent(
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_decay=0.9995,
        epsilon_min=0.05
    )

    print("=" * 60)
    print("RL AGENT TRAINING STARTED")
    print("=" * 60)
    print(f"Episodes: {episodes}")
    print(f"Learning Rate: {agent.lr}")
    print(f"Discount Factor: {agent.gamma}")
    print(f"Initial Epsilon: {agent.epsilon}")
    print("=" * 60)

    start_time = time.time()
    best_score = 0
    best_max_tile = 0

    for episode in range(episodes):
        state = game.reset()
        total_reward = 0
        steps = 0

        while not game.game_over:
            old_max_tile = game.get_max_tile()

            # Action seç
            action = agent.choose_action(state)

            # Execute action
            changed, score_gained, done = game.make_move(action)

            new_state = game.get_state()
            new_max_tile = game.get_max_tile()

            # Reward hesapla
            reward = compute_reward(game, score_gained, changed,
                                    old_max_tile, new_max_tile)

            # Learn from experience
            agent.learn(state, action, reward, new_state, done)

            state = new_state
            total_reward += reward
            steps += 1

            # Safety break (infinite loop prevention)
            if steps > 10000:
                break

        # Epsilon decay
        agent.decay_epsilon()

        # Metrics tracking
        agent.training_history['episode_rewards'].append(total_reward)
        agent.training_history['episode_scores'].append(game.score)
        agent.training_history['episode_max_tiles'].append(game.get_max_tile())
        agent.training_history['episode_moves'].append(steps)
        agent.training_history['epsilon_history'].append(agent.epsilon)
        agent.training_history['q_table_size'].append(len(agent.q_table))

        # Best tracking
        if game.score > best_score:
            best_score = game.score
        if game.get_max_tile() > best_max_tile:
            best_max_tile = game.get_max_tile()

        # Verbose output
        if verbose and (episode + 1) % 50 == 0:
            recent_scores = agent.training_history['episode_scores'][-50:]
            recent_max_tiles = agent.training_history['episode_max_tiles'][-50:]
            avg_score = np.mean(recent_scores)
            avg_max_tile = np.mean(recent_max_tiles)

            print(f"Ep {episode + 1:5d} | "
                  f"Avg Score: {avg_score:7.1f} | "
                  f"Avg MaxTile: {avg_max_tile:5.0f} | "
                  f"Best: {best_score} ({best_max_tile}) | "
                  f"Eps: {agent.epsilon:.3f} | "
                  f"Q-Size: {len(agent.q_table):6d}")

        # Save periodically
        if (episode + 1) % save_interval == 0:
            agent.save_model('agent_checkpoint.pkl')

    elapsed = time.time() - start_time
    print("=" * 60)
    print(f"TRAINING COMPLETED in {elapsed:.1f} seconds")
    print(f"Best Score: {best_score}")
    print(f"Best Max Tile: {best_max_tile}")
    print(f"Q-Table Size: {len(agent.q_table)}")
    print("=" * 60)

    # Save final model
    agent.save_model('agent_final.pkl')

    # Save training history
    history_json = {k: [float(v) for v in vals]
                    for k, vals in agent.training_history.items()}
    with open('training_history.json', 'w') as f:
        json.dump(history_json, f, indent=2)

    return agent


def evaluate_agent(agent, num_games=20):
    """
    Trained agent'i test eder (epsilon=0 ile pure exploitation)
    """
    print("\n" + "=" * 60)
    print("AGENT EVALUATION")
    print("=" * 60)

    original_epsilon = agent.epsilon
    agent.epsilon = 0  # Pure exploitation

    game = Game2048()
    results = {
        'scores': [],
        'max_tiles': [],
        'moves': [],
        'games_won': 0
    }

    for i in range(num_games):
        game.reset()
        state = game.get_state()
        steps = 0
        consecutive_invalid = 0

        while not game.game_over and steps < 5000:
            action = agent.choose_action(state)
            changed, _, _ = game.make_move(action)

            # Invalid move handling - try other actions
            if not changed:
                consecutive_invalid += 1
                if consecutive_invalid >= 4:
                    # Tüm action'lar deniendi ama hiçbiri valid değil = game over
                    game.game_over = True
                    break
                # Farklı action dene
                for alt_action in [0, 1, 2, 3]:
                    if alt_action != action:
                        changed, _, _ = game.make_move(alt_action)
                        if changed:
                            consecutive_invalid = 0
                            break
            else:
                consecutive_invalid = 0

            state = game.get_state()
            steps += 1

        results['scores'].append(game.score)
        results['max_tiles'].append(game.get_max_tile())
        results['moves'].append(steps)
        if game.get_max_tile() >= 2048:
            results['games_won'] += 1

        print(f"Game {i + 1:2d}: Score={game.score:5d}, "
              f"MaxTile={game.get_max_tile():4d}, Moves={steps}")

    agent.epsilon = original_epsilon

    print("-" * 60)
    print(f"Avg Score: {np.mean(results['scores']):.1f}")
    print(f"Avg Max Tile: {np.mean(results['max_tiles']):.1f}")
    print(f"Max Tile Achieved: {max(results['max_tiles'])}")
    print(f"Games Won (2048+): {results['games_won']}/{num_games}")
    print(f"Win Rate: {100 * results['games_won'] / num_games:.1f}%")
    print("=" * 60)

    return results


if __name__ == "__main__":
    # Train agent
    trained_agent = train_agent(episodes=500, verbose=True)

    # Evaluate
    eval_results = evaluate_agent(trained_agent, num_games=10)
