import game
import numpy as np
import random

actions = [0, 1, 2, 3]      # 0 - forward, 1 - backward, 2 - right, 3 - left
N_actions = len(actions)
N_states = 3
obs_space = (41, 41, 41, 41)            # observation space

qtab = np.zeros(obs_space + (N_actions,), dtype='float16')          # Q matrix initialization

scale = 5

rewards = []

# ======================================================================================================================
# ============================================   HYPERPARAMETERS   =====================================================
# ======================================================================================================================

total_episodes = 50000
learning_rate = 0.8
max_steps = 20
gamma = 0.95

epsilon = 1.0
max_epsilon = 1.0
min_epsilon = 0.01
decay_rate = 0.005

# ======================================================================================================================

def take_a_step(action, pos, robot_direction):
    if action == 0:
        pos = game.forward(pos, robot_direction)
    elif action == 1:
        pos = game.backward(pos, robot_direction)
    elif action == 2:
        robot_direction = game.right(robot_direction)
        pos = game.forward(pos, robot_direction)
    elif action == 3:
        robot_direction = game.left(robot_direction)
        pos = game.forward(pos, robot_direction)

    return pos, robot_direction


def perform(pos, robot_direction):
    front, back, right, left = game.measure(pos, robot_direction)       # measure distances from the nearest obstacle

    # max value in observation space is 200 so I add filter that change every distance > 200 to 200
    if front > 200:
        front = 200
    if back > 200:
        back = 200
    if right > 200:
        right = 200
    if left > 200:
        left = 200

    front = int(front / scale)                  # rescale
    back = int(back / scale)
    right = int(right / scale)
    left = int(left / scale)

    state = tuple([front, back, right, left])

    if front < (5 / scale) or back < (5 / scale) or right < (5 / scale) or left < (5 / scale):      # too close to wall
        reward = -400
        done = True
    elif left + right > (250 / scale):
        if left > (150 / scale) and right > (150 / scale):      # outside the room
            reward = 500
            done = True
        else:
            reward = - 10
            done = False
    else:
        reward = - 10
        done = False

    return state, reward, done


def train(epsilon):
    d = 0
    for episode in range(total_episodes):
        pos = game.pygame.Rect(game.robot_start_position[0], game.robot_start_position[1], game.robot_width,
                               game.robot_length)
        robot_direction = 0  # direction of the front of the robot: 0-down, 1-up, 2-left, 3-right

        game.env(pos, robot_direction)

        front, back, right, left = game.measure(pos, robot_direction)
        state = tuple([int(front / scale), int(back / scale), int(right / scale), int(left / scale)])

        done = False
        total_rewards = 0

        for step in range(max_steps):
            ran = random.uniform(0,1)       # random number between 0 and 1 to choose explortion or exploitation

            if ran > epsilon:               # if ran > epsilon -> exploitation, we pick action with the biggest reward
                action = np.argmax(qtab[state])
            else:                           # if not -> exploration, we explore enviornment
                nmb = random.randint(0,N_actions - 1)
                action = actions[nmb]

            pos, robot_direction = take_a_step(action, pos, robot_direction)

            new_state, reward, done = perform(pos, robot_direction)         # get new state, reward

            game.env(pos, robot_direction)

            q_value = qtab[state][action]               # update Q matrix
            best_q = np.max(qtab[new_state])
            qtab[state][action] = (1 - learning_rate) * q_value + learning_rate * (reward + gamma * best_q)

            total_rewards += reward

            state = new_state

            if done:
                break

        epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay_rate * episode)
        rewards.append(total_rewards)

        if total_rewards > 0:
            d += 1
        if (episode + 1) % 1000 == 0:
            print("Episode: " + str(episode) + ", success: " + str(d) + ", accuracy: " + str(d * 100 / 1000))
            d = 0

    print("Score: " + str(sum(rewards) / total_episodes))
    np.save('data', qtab)


def test(epsilon):
    qtab = np.load('data.npy')          # load q matrix from file

    episodes = 1000
    count = 0

    for episode in range(episodes):
        pos = game.pygame.Rect(game.robot_start_position[0], game.robot_start_position[1], game.robot_width,
                               game.robot_length)
        robot_direction = 0  # direction of the front of the robot: 0-down, 1-up, 2-left, 3-right

        game.env(pos, robot_direction)

        front, back, right, left = game.measure(pos, robot_direction)
        state = tuple([int(front / scale), int(back / scale), int(right / scale), int(left / scale)])

        done = False
        total_rewards = 0

        for step in range(max_steps):
            action = np.argmax(qtab[state])

            pos, robot_direction = take_a_step(action, pos, robot_direction)

            new_state, reward, done = perform(pos, robot_direction)  # get new state, reward

            game.env(pos, robot_direction)

            total_rewards = total_rewards + reward

            if done:
                break

            state = new_state

        if total_rewards > 0:
            count += 1
    print("Number of success: " + str(count) + "/" + str(episodes) + ". Accuracy: " + str(count * 100 / episodes))


if __name__ == "__main__":
    train(epsilon)
    # test(epsilon)

