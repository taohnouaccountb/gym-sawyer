import numpy as np
import time

def toyenv_distance(obs, waypoint):
    gripper_pos = obs[:3]
    goal_pos = waypoint[:3]
    return goal_pos - gripper_pos

def toyenv_action(dist, waypoint, epsilon=1e-8, action_scale=0.01):
    dist = dist / (np.linalg.norm(dist) + epsilon)
    action = dist * action_scale
    action = np.concatenate((action, [waypoint[3]]), axis=-1)
    return action

class WaypointSequencer:
    """
    For recording a demo of an env stepping through a series of waypoints.
    """
    def __init__(self,
                 env,
                 waypoints,
                 distance_fn,
                 action_fn,
                 max_n_steps=10000,
                 success_thresh=0.01):
        """
        Initializer.

        env: gym.Env
        waypoints: np.array w/ shape (n_waypts,) + env.action_space.shape
        distance_fn(obs, waypoint) --> (distance_vector)
        action_fn(distance_vector) --> action
        """
        self._env = env
        self._waypoints = waypoints
        self._distance_fn = distance_fn
        self._action_fn = action_fn
        self._max_n_steps = max_n_steps
        self._success_thresh = success_thresh

        assert waypoints.shape[1] == env.action_space.shape[0]

    def reset(self):
        """
        Resets for new recording.
        """
        return self._env.reset()

    def run(self, render=False):
        """
        Runs env, attempts to reach sequence of waypoints.
        Returns a dataset of actions and observations once complete.
        """
        obs = self.reset()
        step = 0
        waypoint_idx = 0
        recording = []

        for step in range(self._max_n_steps):
            waypoint = self._waypoints[waypoint_idx, :]
            # Determine distance to waypoint
            dist = self._distance_fn(obs, waypoint)
            if (np.linalg.norm(dist) < self._success_thresh and 
                np.linalg.norm(info['gripper_state'] - waypoint[3]) < 0.1):
                waypoint_idx += 1
                if waypoint_idx < self._waypoints.shape[0]:
                    print("Reached waypoint {0} with obs:\n{1}".
                          format(waypoint, obs))
                    continue
                else:
                    break

            # Generate action
            act = self._action_fn(dist, waypoint)
            recording.append((obs, act))

            # Step env
            obs, rew, done, info = self._env.step(act)
            if render:
                self._env.render()
                time.sleep(0.002)

            if done:
                print("Env terminated at step {0} at obs:\n{1}".format(step, obs))
                break

        print("Finished at step {}".format(step))
        recording = np.array(recording)
        return recording
