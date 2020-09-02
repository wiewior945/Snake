from tf_agents.agents.dqn import dqn_agent
from tf_agents.policies import random_tf_policy
from tf_agents.trajectories import trajectory

from snake import Snake
import tensorflow as tf
import matplotlib.pyplot as plt

from tf_agents.networks import q_network
from tf_agents.environments import tf_py_environment
from tf_agents.utils import common
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.environments import utils

learningRate = 0.001
replay_buffer_max_length = 100000
learningIterations = 20000
stepsIteration = 200
batchSegmentSize = 1000
batchSize = 100000


def averageRewardReturn(environment, policy, episodes):
    totalReturn = 0
    for _ in range(episodes):
        timeStep = environment.reset()
        episodeReturn = 0
        countStep = 0
        while not timeStep.is_last() and countStep<stepsIteration:
            countStep += 1
            actionStep = policy.action(timeStep)
            timeStep = environment.step(actionStep.action)
            episodeReturn += timeStep.reward
        print("Steps: " + str(countStep))
        totalReturn += episodeReturn
    averageReturn = totalReturn / episodes
    print("Average: " + str(averageReturn))
    return averageReturn

def collect_step(environment, policy, buffer):
    time_step = environment.current_time_step()
    action_step = policy.action(time_step)
    next_time_step = environment.step(action_step.action)
    traj = trajectory.from_transition(time_step, action_step, next_time_step)
    buffer.add_batch(traj)
print("Start")
snakeTrain = Snake()
snakeEval = Snake()

train_env = tf_py_environment.TFPyEnvironment(snakeTrain)
eval_env = tf_py_environment.TFPyEnvironment(snakeEval)

print("Environments ready")

random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(), train_env.action_spec()) #policy losująca randomowe akcje
print("Random policy ready")
# averageRewardReturn(eval_env, random_policy, 5)
q_net = q_network.QNetwork(train_env.observation_spec(), train_env.action_spec()) # sieć dla agenta
print("Network ready")

optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learningRate) #optimizer dla agenta
train_step_counter = tf.Variable(0) # specjalna zmienna tensorflow, którą gdzieś tam sobie zarządza z tyłu
print("Optimizer ready")

agent = dqn_agent.DqnAgent(train_env.time_step_spec(), train_env.action_spec(), q_network=q_net, optimizer=optimizer, td_errors_loss_fn=common.element_wise_squared_loss, train_step_counter=train_step_counter)
agent.initialize()
print("Agent ready")

eval_policy = agent.policy
collect_policy = agent.collect_policy
print("Policies ready")
print(type(eval_policy))

#
# replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(data_spec=agent.collect_data_spec, batch_size=train_env.batch_size, max_length=replay_buffer_max_length)
# print("Replay buffer ready")
#
# for _ in range(100):
#     collect_step(train_env, random_policy, replay_buffer)
# print("Random steps collected")
#
# dataset = replay_buffer.as_dataset(num_parallel_calls=3, sample_batch_size=batchSize, num_steps=2).prefetch(3)
# iterator = iter(dataset)
# print("Dataset ready")
#
# agent.train_step_counter.assign(0)
# avgBeforeTraining = averageRewardReturn(eval_env, agent.policy, 1)
# returns = [avgBeforeTraining]
# returns100 = [avgBeforeTraining]
# steps = [0]
# steps100 = [0]
# print("Start")
# for _ in range(learningIterations):
#     for _ in range(stepsIteration):
#         collect_step(train_env, agent.collect_policy, replay_buffer)
#     experience, unusedInfo = next(iterator)
#     train_loss = agent.train(experience).loss
#     step = agent.train_step_counter.numpy()
#     print("Step: " + str(step))
#     if step % 10 == 0:
#         returns.append(averageRewardReturn(eval_env, agent.policy, 10))
#         steps.append(step)
#         if step % 100 == 0:
#             returns100.append(averageRewardReturn(eval_env, agent.policy, 10))
#             steps100.append(step)
#
# print("-------------------------")
# print(returns)
# print(steps)
# print(returns100)
# print(steps100)
# plt.plot(steps, returns)
# plt.xlabel('step')
# plt.ylabel('score')
# plt.show()