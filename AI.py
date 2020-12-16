from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.policies import policy_saver


from snake import Snake
import tensorflow as tf
import matplotlib.pyplot as plt
import os

from tf_agents.networks import q_network
from tf_agents.environments import tf_py_environment
from tf_agents.utils import common
from tf_agents.replay_buffers import tf_uniform_replay_buffer


policy_save_path = "E:\\Snake\\new\\policies"
learning_rate = 0.001
buffer_length = 100000
learning_iterations = 15000     # length of the training
steps_iteration = 1000  # how many steps will be performed in single learnign iteration
batch_segment_size = 1000
batch_size = 5000
best_avg = []
best_policy = []


def average_reward_return(environment, policy, episodes):
    totalReturn = 0
    for _ in range(episodes):
        timeStep = environment.reset()
        episodeReturn = 0
        countStep = 0
        while not timeStep.is_last() and countStep<steps_iteration:
            countStep += 1
            actionStep = policy.action(timeStep)
            timeStep = environment.step(actionStep.action)
            episodeReturn += timeStep.reward
        totalReturn += episodeReturn
        print("Steps: " + str(countStep))
    averageReturn = totalReturn / episodes
    averageReturn = averageReturn.numpy()[0]
    print("Average: " + str(averageReturn))
    return averageReturn


def bestPolicies(avg, policy):
    if best_avg[0] < avg:
        best_avg.insert(0, avg)
        best_policy.insert(0, policy)
    if len(best_avg) > 10:
        del best_avg[-1]
        del best_policy[-1]

print("Start")
snakeTrain = Snake()
snakeEval = Snake()

train_env = tf_py_environment.TFPyEnvironment(snakeTrain)
eval_env = tf_py_environment.TFPyEnvironment(snakeEval)
print("Environments ready")

q_net = q_network.QNetwork(train_env.observation_spec(), train_env.action_spec())
print("Network ready")

optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate)
train_step_counter = tf.Variable(0) # special variable which is managed by Tensorflow in background
print("Optimizer ready")

agent = dqn_agent.DqnAgent(train_env.time_step_spec(), train_env.action_spec(), q_network=q_net, optimizer=optimizer, td_errors_loss_fn=common.element_wise_squared_loss, train_step_counter=train_step_counter)
agent.initialize()
print("Agent ready")

collect_policy = agent.collect_policy
print("Policies ready")

replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(data_spec=agent.collect_data_spec, batch_size=train_env.batch_size, max_length=buffer_length)
print("Replay buffer ready")

collect_driver = dynamic_step_driver.DynamicStepDriver(train_env, agent.collect_policy, observers=[replay_buffer.add_batch], num_steps=steps_iteration)
collect_driver.run()
print("Initial steps collected")

dataset = replay_buffer.as_dataset(num_parallel_calls=3, sample_batch_size=batch_size, num_steps=2).prefetch(3)
iterator = iter(dataset)
print("Dataset ready")

agent.train_step_counter.assign(0)
avgBeforeTraining = average_reward_return(eval_env, agent.policy, 1)
best_avg.append(avgBeforeTraining)
best_policy.append(agent.policy)
returns = [avgBeforeTraining]
steps = [0]
print("Start")
for _ in range(learning_iterations):
    collect_driver.run()
    experience, unusedInfo = next(iterator)
    train_loss = agent.train(experience).loss
    step = agent.train_step_counter.numpy()
    print("Step: " + str(step))
    if step % 100 == 0:
        avg = average_reward_return(eval_env, agent.policy, 10)
        bestPolicies(avg, agent.policy)
        steps.append(step)
        returns.append(avg)



print("-------------------------")
print(returns)
print(steps)
plt.plot(steps, returns)
plt.xlabel('step')
plt.ylabel('score')
plt.show()

print("-------------------------")
print("Best avg:" + str(best_avg))
for i in range(len(best_policy)):
    path = policy_save_path + " " + str(best_avg[i])
    os.mkdir(path)
    tf_policy_saver = policy_saver.PolicySaver(best_policy[i])
    tf_policy_saver.save(path)


