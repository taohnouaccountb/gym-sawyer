import numpy as np
import rospy

from sawyer.garage.baselines.linear_feature_baseline import LinearFeatureBaseline
from sawyer.ros.envs.sawyer.pick_and_place_env import PickAndPlaceEnv
from sawyer.garage.misc.instrument import run_experiment
from sawyer.garage.theano.algos import TRPO
from sawyer.garage.theano.envs import TheanoEnv
from sawyer.garage.theano.policies import GaussianMLPPolicy

INITIAL_ROBOT_JOINT_POS = {
    'right_j0': -0.140923828125,
    'right_j1': -1.2789248046875,
    'right_j2': -3.043166015625,
    'right_j3': -2.139623046875,
    'right_j4': -0.047607421875,
    'right_j5': -0.7052822265625,
    'right_j6': -1.4102060546875,
}


def run_task(*_):
    initial_goal = np.array([0.6, -0.1, 0.80])

    rospy.init_node('trpo_real_sawyer_pnp_exp', anonymous=True)

    pnp_env = TheanoEnv(
        PickAndPlaceEnv(
            initial_goal,
            initial_joint_pos=INITIAL_ROBOT_JOINT_POS,
            simulated=False))

    rospy.on_shutdown(pnp_env.shutdown)

    pnp_env.initialize()

    env = pnp_env

    policy = GaussianMLPPolicy(env_spec=env.spec, hidden_sizes=(32, 32))

    baseline = LinearFeatureBaseline(env_spec=env.spec)

    algo = TRPO(
        env=env,
        policy=policy,
        baseline=baseline,
        batch_size=4000,
        max_path_length=100,
        n_itr=100,
        discount=0.99,
        step_size=0.01,
        plot=False,
        force_batch_sampler=True,
    )
    algo.train()


run_experiment(
    run_task,
    n_parallel=1,
    plot=False,
)
