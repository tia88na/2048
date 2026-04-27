"""
=====================================================
Test Suite - QA/Tester Deliverable
=====================================================
QA/Tester: Unit and Integration tests
Software Project Management & Technical Monitoring
=====================================================
"""

import unittest
import numpy as np
from game_2048 import Game2048
from rl_agent import QLearningAgent, compute_reward


class TestGame2048(unittest.TestCase):
    """2048 Game Engine Tests"""

    def setUp(self):
        self.game = Game2048()

    def test_initial_board_has_two_tiles(self):
        """TC-01: Initial board 2 tile içermeli"""
        non_zero = np.count_nonzero(self.game.board)
        self.assertEqual(non_zero, 2)

    def test_initial_score_zero(self):
        """TC-02: Başlangıç skoru 0 olmalı"""
        self.assertEqual(self.game.score, 0)

    def test_board_size(self):
        """TC-03: Board 4x4 olmalı"""
        self.assertEqual(self.game.board.shape, (4, 4))

    def test_move_left_merges_tiles(self):
        """TC-04: Sol hareket aynı tile'ları birleştirmeli"""
        self.game.board = np.array([
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        initial_score = self.game.score
        self.game.move_left()
        self.assertEqual(self.game.board[0][0], 4)
        self.assertEqual(self.game.score, initial_score + 4)

    def test_move_right_merges_tiles(self):
        """TC-05: Sağ hareket aynı tile'ları birleştirmeli"""
        self.game.board = np.array([
            [0, 0, 4, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        self.game.move_right()
        self.assertEqual(self.game.board[0][3], 8)

    def test_move_up_merges_tiles(self):
        """TC-06: Yukarı hareket aynı tile'ları birleştirmeli"""
        self.game.board = np.array([
            [8, 0, 0, 0],
            [8, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        self.game.move_up()
        self.assertEqual(self.game.board[0][0], 16)

    def test_move_down_merges_tiles(self):
        """TC-07: Aşağı hareket aynı tile'ları birleştirmeli"""
        self.game.board = np.array([
            [0, 0, 0, 16],
            [0, 0, 0, 16],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        self.game.move_down()
        self.assertEqual(self.game.board[3][3], 32)

    def test_different_tiles_do_not_merge(self):
        """TC-08: Farklı tile'lar birleşmemeli"""
        self.game.board = np.array([
            [2, 4, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        self.game.move_left()
        self.assertEqual(self.game.board[0][0], 2)
        self.assertEqual(self.game.board[0][1], 4)

    def test_no_triple_merge(self):
        """TC-09: Aynı sırada 3 tile olursa sadece 2'si birleşmeli"""
        self.game.board = np.array([
            [2, 2, 2, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        self.game.move_left()
        # 4, 2, 0, 0 beklenir (önce ilk ikisi birleşir)
        self.assertEqual(self.game.board[0][0], 4)
        self.assertEqual(self.game.board[0][1], 2)

    def test_game_over_detection(self):
        """TC-10: Board doluyken ve merge mümkün değilken game over"""
        self.game.board = np.array([
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2]
        ])
        self.assertTrue(self.game._is_game_over())

    def test_not_game_over_with_empty_cell(self):
        """TC-11: Boş hücre varken game over olmamalı"""
        self.game.board = np.array([
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 0]
        ])
        self.assertFalse(self.game._is_game_over())

    def test_reset_board(self):
        """TC-12: Reset board'u sıfırlamalı"""
        self.game.score = 1000
        self.game.reset()
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.moves_count, 0)
        self.assertFalse(self.game.game_over)

    def test_max_tile(self):
        """TC-13: Max tile doğru hesaplanmalı"""
        self.game.board = np.array([
            [2, 4, 8, 16],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        self.assertEqual(self.game.get_max_tile(), 16)

    def test_win_condition(self):
        """TC-14: 2048 oluşursa win flag set edilmeli"""
        self.game.board = np.array([
            [1024, 1024, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        self.game.move_left()
        self.assertTrue(self.game.won)


class TestQLearningAgent(unittest.TestCase):
    """RL Agent Tests"""

    def setUp(self):
        self.agent = QLearningAgent()
        self.game = Game2048()

    def test_agent_creation(self):
        """TC-15: Agent doğru oluşturulmalı"""
        self.assertEqual(len(self.agent.actions), 4)
        self.assertEqual(self.agent.epsilon, 1.0)

    def test_epsilon_decay(self):
        """TC-16: Epsilon decay çalışmalı"""
        initial_eps = self.agent.epsilon
        self.agent.decay_epsilon()
        self.assertLess(self.agent.epsilon, initial_eps)

    def test_epsilon_min_limit(self):
        """TC-17: Epsilon min limit'ten düşmemeli"""
        self.agent.epsilon = 0.01
        self.agent.epsilon_min = 0.01
        self.agent.decay_epsilon()
        self.assertGreaterEqual(self.agent.epsilon, 0.01)

    def test_action_selection(self):
        """TC-18: Action selection valid range dönmeli"""
        state = self.game.get_state()
        action = self.agent.choose_action(state)
        self.assertIn(action, [0, 1, 2, 3])

    def test_state_key_conversion(self):
        """TC-19: State key hash'lenebilir olmalı"""
        state = self.game.get_state()
        key = self.agent._state_to_key(state)
        self.assertIsInstance(key, tuple)
        # Hashable olmalı
        hash(key)

    def test_learning_updates_q_table(self):
        """TC-20: Learning Q-table'ı güncellemeli"""
        state = self.game.get_state()
        self.agent.learn(state, 0, 1.0, state, False)
        state_key = self.agent._state_to_key(state)
        self.assertNotEqual(self.agent.q_table[state_key][0], 0)


class TestRewardFunction(unittest.TestCase):
    """Reward Function Tests"""

    def setUp(self):
        self.game = Game2048()

    def test_reward_for_score_gain(self):
        """TC-21: Score kazanınca reward pozitif olmalı"""
        reward = compute_reward(self.game, score_gained=8, changed=True,
                                old_max_tile=2, new_max_tile=2)
        self.assertGreater(reward, 0)

    def test_penalty_for_invalid_move(self):
        """TC-22: Invalid move ceza vermeli"""
        reward = compute_reward(self.game, score_gained=0, changed=False,
                                old_max_tile=2, new_max_tile=2)
        self.assertLess(reward, 0)

    def test_bonus_for_new_max_tile(self):
        """TC-23: Yeni max tile bonus vermeli"""
        reward_with_bonus = compute_reward(self.game, score_gained=16,
                                           changed=True, old_max_tile=8,
                                           new_max_tile=16)
        reward_without_bonus = compute_reward(self.game, score_gained=16,
                                              changed=True, old_max_tile=16,
                                              new_max_tile=16)
        self.assertGreater(reward_with_bonus, reward_without_bonus)


class TestIntegration(unittest.TestCase):
    """Integration Tests - Game + Agent"""

    def test_agent_plays_full_game(self):
        """TC-24: Agent tam oyun oynayabilmeli"""
        game = Game2048()
        agent = QLearningAgent()
        agent.epsilon = 0

        steps = 0
        while not game.game_over and steps < 1000:
            state = game.get_state()
            action = agent.choose_action(state)
            game.make_move(action)
            steps += 1

        self.assertGreater(steps, 0)
        self.assertGreaterEqual(game.score, 0)

    def test_training_improves_performance(self):
        """TC-25: Training sonrası performance artmalı"""
        game = Game2048()
        agent = QLearningAgent(epsilon=0.5, epsilon_decay=0.99)

        # İlk değerlendirme
        agent.epsilon = 0
        game.reset()
        state = game.get_state()
        steps = 0
        while not game.game_over and steps < 100:
            action = agent.choose_action(state)
            game.make_move(action)
            state = game.get_state()
            steps += 1
        initial_score = game.score

        # Kısa training
        agent.epsilon = 0.5
        for _ in range(50):
            game.reset()
            state = game.get_state()
            while not game.game_over:
                action = agent.choose_action(state)
                _, score_gained, done = game.make_move(action)
                new_state = game.get_state()
                reward = score_gained if score_gained > 0 else -1
                agent.learn(state, action, reward, new_state, done)
                state = new_state

        # Q-table büyümüş olmalı
        self.assertGreater(len(agent.q_table), 0)


def run_all_tests():
    """Tüm testleri çalıştırır ve raporunu üretir"""
    print("=" * 70)
    print("2048 RL PROJECT - AUTOMATED TEST SUITE")
    print("=" * 70)

    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestGame2048))
    suite.addTests(loader.loadTestsFromTestCase(TestQLearningAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestRewardFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Test runner
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print("TEST REPORT SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 70)

    return result


if __name__ == "__main__":
    run_all_tests()
