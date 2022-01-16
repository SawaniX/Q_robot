import game
import numpy as np
import random


actions = [0, 1, 2, 3]      # 0 - forward, 1 - backward, 2 - right, 3 - left
N_actions = len(actions)
N_states = 3
obs_space = (41, 41, 41, 41)            # observation space, front sensor, back, right, left

qtab = np.zeros(obs_space + (N_actions,), dtype='float16')          # Q matrix initialization

scale = 5

rewards = []

# ======================================================================================================================
# ============================================   HYPERPARAMETERS   =====================================================
# ======================================================================================================================

total_episodes = 5000
learning_rate = 0.2
max_steps = 99
gamma = 0.95

epsilon = 1.0
max_epsilon = 1.0
min_epsilon = 0.01
decay_rate = 0.0035

# ======================================================================================================================


def take_a_step(action, pos, robot_direction):      # perform step in game.py
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


def perform(pos, robot_direction, vgh):
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
        elif vgh == 1:
            reward = -20
            done = False
        elif front > (150 / scale) or back > (150 / scale) or right > (150 / scale) or left > (150 / scale):
            reward = 0
            done = False
        else:
            reward = -10
            done = False
    elif vgh == 1:
        reward = -20
        done = False
    elif front > (150 / scale) or back > (150 / scale) or right > (150 / scale) or left > (150 / scale):
        reward = 0
        done = False
    else:
        reward = -10
        done = False

    return state, reward, done


def train(epsilon):
    d = 0
    xd = np.arange(0, total_episodes / 10)
    wyn = []
    for episode in range(total_episodes):
        last_action = 5
        # map = random.randint(0, 9)         # choose if training on one or 10 maps
        map = 4
        pos = game.pygame.Rect(game.robot_start_position[0], game.robot_start_position[1], game.robot_width,
                               game.robot_length)
        robot_direction = 0  # direction of the front of the robot: 0-down, 1-up, 2-left, 3-right

        game.env(pos, robot_direction, map)

        front, back, right, left = game.measure(pos, robot_direction)
        state = tuple([int(front / scale), int(back / scale), int(right / scale), int(left / scale)])

        done = False
        total_rewards = 0

        for step in range(max_steps):
            vgh = 0
            ran = random.uniform(0, 1)       # random number between 0 and 1 to choose explortion or exploitation

            if ran > epsilon:               # if ran > epsilon -> exploitation, we pick action with the biggest reward
                action = np.argmax(qtab[state])
            else:                           # if not -> exploration, we explore enviornment
                nmb = random.randint(0, N_actions - 1)
                action = actions[nmb]

            pos, robot_direction = take_a_step(action, pos, robot_direction)

            game.env(pos, robot_direction, map)

            if action == 0 and last_action == 1:
                vgh = 1
            elif action == 1 and last_action == 0:
                vgh = 1

            new_state, reward, done = perform(pos, robot_direction, vgh)         # get new state, reward

            q_value = qtab[state][action]               # update Q matrix
            best_q = np.max(qtab[new_state])
            qtab[state][action] = (1 - learning_rate) * q_value + learning_rate * (reward + gamma * best_q)

            total_rewards += reward

            state = new_state
            last_action = action

            if done:
                break

        epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay_rate * episode)
        rewards.append(total_rewards)

        if total_rewards > 0:
            d += 1
        if (episode + 1) % 10 == 0:
            wyn.append(d)
            print("Episode: " + str(episode) + ", success: " + str(d) + ", accuracy: " + str(d * 100 / 1000))
            d = 0

    print("Score: " + str(sum(rewards) / total_episodes))
    np.save('Q_matrix', qtab)


def test(epsilon):
    qtab = np.load('10map_60proc.npy')          # load q matrix from file

    episodes = 1000
    count = 0
    s = 0

    for episode in range(episodes):
        u = 0
        last_action = 5
        print(episode)
        map = random.randint(0, 9)
        #map = 6
        pos = game.pygame.Rect(game.robot_start_position[0], game.robot_start_position[1], game.robot_width,
                               game.robot_length)
        robot_direction = 0  # direction of the front of the robot: 0-down, 1-up, 2-left, 3-right

        game.env(pos, robot_direction, map)

        front, back, right, left = game.measure(pos, robot_direction)
        state = tuple([int(front / scale), int(back / scale), int(right / scale), int(left / scale)])

        done = False
        total_rewards = 0

        for step in range(max_steps):

            vgh = 0
            u += 1
            action = np.argmax(qtab[state])

            pos, robot_direction = take_a_step(action, pos, robot_direction)

            game.env(pos, robot_direction, map)

            if action == 0 and last_action == 1:
                vgh = 1
            elif action == 1 and last_action == 0:
                vgh = 1

            new_state, reward, done = perform(pos, robot_direction, vgh)  # get new state, reward

            total_rewards = total_rewards + reward

            state = new_state
            last_action = action

            if done:
                break

        rewards.append(total_rewards)

        if total_rewards > 0:
            count += 1
            s += u
    print("Number of success: " + str(count) + "/" + str(episodes) + ". Accuracy: " + str(count * 100 / episodes))
    print("Avr. steps: " +str(s/count))


if __name__ == "__main__":
    train(epsilon)
    #test(epsilon)

