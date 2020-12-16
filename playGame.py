import tensorflow as tf
from tf_agents.environments import tf_py_environment

from snake import Snake


def play_game(environment, policy):
    timeStep = environment.reset()
    sum = 0
    while not timeStep.is_last():
        actionStep = policy.action(timeStep)
        timeStep = environment.step(actionStep.action)
        print(timeStep)
        sum += timeStep.reward
    print("Sum: " + str(sum))
    return sum

env = Snake()
environment = tf_py_environment.TFPyEnvironment(env)

policyPath = "E:\\Snake\\new\\policies 802.1"
saved_policy = tf.compat.v2.saved_model.load(policyPath)

play_game(environment, saved_policy)