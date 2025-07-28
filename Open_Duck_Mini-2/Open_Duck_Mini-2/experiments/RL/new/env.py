import numpy as np
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box

FRAME_SKIP = 10


class BDXEnv(MujocoEnv, utils.EzPickle):
    """
    ## Action space

    | Num  | Action                                                            | Control Min | Control Max | Name (in corresponding XML file) | Joint    | Unit         |
    | ---- | ----------------------------------------------------------------- | ----------- | ----------- | -------------------------------- | -------- |------------- |
    | 0    | Set position of right_hip_yaw                                     | -0.58TODO   | 0.58TODO    | right_hip_yaw                    | cylinder | pos (rad)    |
    | 1    | Set position of right_hip_roll                                    | -0.58TODO   | 0.58TODO    | right_hip_roll                   | cylinder | pos (rad)    |
    | 2    | Set position of right_hip_pitch                                   | -0.58TODO   | 0.58TODO    | right_hip_pitch                  | cylinder | pos (rad)    |
    | 3    | Set position of right_knee_pitch                                  | -0.58TODO   | 0.58TODO    | right_knee_pitch                 | cylinder | pos (rad)    |
    | 4    | Set position of right_ankle_pitch                                 | -0.58TODO   | 0.58TODO    | right_ankle_pitch                | cylinder | pos (rad)    |
    | 5    | Set position of left_hip_yaw                                      | -0.58TODO   | 0.58TODO    | left_hip_yaw                     | cylinder | pos (rad)    |
    | 6    | Set position of left_hip_roll                                     | -0.58TODO   | 0.58TODO    | left_hip_roll                    | cylinder | pos (rad)    |
    | 7    | Set position of left_hip_pitch                                    | -0.58TODO   | 0.58TODO    | left_hip_pitch                   | cylinder | pos (rad)    |
    | 8    | Set position of left_knee_pitch                                   | -0.58TODO   | 0.58TODO    | left_knee_pitch                  | cylinder | pos (rad)    |
    | 9    | Set position of left_ankle_pitch                                  | -0.58TODO   | 0.58TODO    | left_ankle_pitch                 | cylinder | pos (rad)    |
    | 9    | Set position of head_pitch1                                       | -0.58TODO   | 0.58TODO    | left_ankle_pitch                 | cylinder | pos (rad)    |
    | 9    | Set position of head_pitch2                                       | -0.58TODO   | 0.58TODO    | left_ankle_pitch                 | cylinder | pos (rad)    |
    | 9    | Set position of head_yaw                                          | -0.58TODO   | 0.58TODO    | left_ankle_pitch                 | cylinder | pos (rad)    |


    ## Observation space

    | Num | Observation                                              | Min  | Max | Name (in corresponding XML file) | Joint    | Unit                     |
    | --- | -------------------------------------------------------- | ---- | --- | -------------------------------- | -------- | ------------------------ |
    | 0   | Rotation right_hip_yaw                                   | -Inf | Inf | right_hip_yaw                    | cylinder | angle (rad)              |
    | 1   | Rotation right_hip_roll                                  | -Inf | Inf | right_hip_roll                   | cylinder | angle (rad)              |
    | 2   | Rotation right_hip_pitch                                 | -Inf | Inf | right_hip_pitch                  | cylinder | angle (rad)              |
    | 3   | Rotation right_knee_pitch                                | -Inf | Inf | right_knee_pitch                 | cylinder | angle (rad)              |
    | 4   | Rotation right_ankle_pitch                               | -Inf | Inf | right_ankle_pitch                | cylinder | angle (rad)              |
    | 5   | Rotation left_hip_yaw                                    | -Inf | Inf | left_hip_yaw                     | cylinder | angle (rad)              |
    | 6   | Rotation left_hip_roll                                   | -Inf | Inf | left_hip_roll                    | cylinder | angle (rad)              |
    | 7   | Rotation left_hip_pitch                                  | -Inf | Inf | left_hip_pitch                   | cylinder | angle (rad)              |
    | 8   | Rotation left_knee_pitch                                 | -Inf | Inf | left_knee_pitch                  | cylinder | angle (rad)              |
    | 9   | Rotation left_ankle_pitch                                | -Inf | Inf | left_ankle_pitch                 | cylinder | angle (rad)              |
    | 10  | Rotation neck_pitch                                      | -Inf | Inf | head_pitch1                      | cylinder | angle (rad)              |
    | 11  | Rotation head_pitch                                      | -Inf | Inf | head_pitch2                      | cylinder | angle (rad)              |
    | 12  | Rotation head_yaw                                        | -Inf | Inf | head_yaw                         | cylinder | angle (rad)              |
    | 13  | Velocity of right_hip_yaw                                | -Inf | Inf | right_hip_yaw                    | cylinder | speed (rad/s)            |
    | 14  | Velocity of right_hip_roll                               | -Inf | Inf | right_hip_roll                   | cylinder | speed (rad/s)            |
    | 15  | Velocity of right_hip_pitch                              | -Inf | Inf | right_hip_pitch                  | cylinder | speed (rad/s)            |
    | 16  | Velocity of right_knee_pitch                             | -Inf | Inf | right_knee_pitch                 | cylinder | speed (rad/s)            |
    | 17  | Velocity of right_ankle_pitch                            | -Inf | Inf | right_ankle_pitch                | cylinder | speed (rad/s)            |
    | 18  | Velocity of left_hip_yaw                                 | -Inf | Inf | left_hip_yaw                     | cylinder | speed (rad/s)            |
    | 19  | Velocity of left_hip_roll                                | -Inf | Inf | left_hip_roll                    | cylinder | speed (rad/s)            |
    | 20  | Velocity of left_hip_pitch                               | -Inf | Inf | left_hip_pitch                   | cylinder | speed (rad/s)            |
    | 21  | Velocity of left_knee_pitch                              | -Inf | Inf | left_knee_pitch                  | cylinder | speed (rad/s)            |
    | 22  | Velocity of left_ankle_pitch                             | -Inf | Inf | left_ankle_pitch                 | cylinder | speed (rad/s)            |
    | 23  | Velocity of neck_pitch                                   | -Inf | Inf | head_pitch1                      | cylinder | speed (rad/s)            |
    | 24  | Velocity of head_pitch                                   | -Inf | Inf | head_pitch2                      | cylinder | speed (rad/s)            |
    | 25  | Velocity of head_yaw                                     | -Inf | Inf | head_yaw                         | cylinder | speed (rad/s)            |


    | 26  | roll angular velocity                                    | -Inf | Inf |                                  |          |                          |e
    | 27  | pitch angular velocity                                   | -Inf | Inf |                                  |          |                          |
    | 28  | yaw angular velocity                                     | -Inf | Inf |                                  |          |                          |
    | 29  | current x linear velocity                                | -Inf | Inf |                                  |          |                          |
    | 30  | current y linear velocity                                | -Inf | Inf |                                  |          |                          |
    | 31  | current z linear velocity                                | -Inf | Inf |                                  |          |                          |
    | 32  | current x target linear velocity                         | -Inf | Inf |                                  |          |                          |
    | 33  | current y target linear velocity                         | -Inf | Inf |                                  |          |                          |
    | 34  | current yaw target angular velocity                      | -Inf | Inf |                                  |          |                          |

    Changed to control history
    | 35  | t-1 right_hip_yaw rotation error                         | -Inf | Inf |                                  |          |                          |
    | 36  | t-1 right_hip_roll rotation error                        | -Inf | Inf |                                  |          |                          |
    | 37  | t-1 right_hip_pitch rotation error                       | -Inf | Inf |                                  |          |                          |
    | 38  | t-1 right_knee_pitch rotation error                      | -Inf | Inf |                                  |          |                          |
    | 39  | t-1 right_ankle_pitch rotation error                     | -Inf | Inf |                                  |          |                          |
    | 40  | t-1 left_hip_yaw rotation error                          | -Inf | Inf |                                  |          |                          |
    | 41  | t-1 left_hip_roll rotation error                         | -Inf | Inf |                                  |          |                          |
    | 42  | t-1 left_hip_pitch rotation error                        | -Inf | Inf |                                  |          |                          |
    | 43  | t-1 left_knee_pitch rotation error                       | -Inf | Inf |                                  |          |                          |
    | 44  | t-1 left_ankle_pitch rotation error                      | -Inf | Inf |                                  |          |                          |
    | 45  | t-1 neck_pitch rotation error                            | -Inf | Inf |                                  |          |                          |
    | 46  | t-1 head_pitch rotation error                            | -Inf | Inf |                                  |          |                          |
    | 47  | t-1 head_yaw rotation error                              | -Inf | Inf |                                  |          |                          |

    | 48  | t-2 right_hip_yaw rotation error                         | -Inf | Inf |                                  |          |                          |
    | 49  | t-2 right_hip_roll rotation error                        | -Inf | Inf |                                  |          |                          |
    | 50  | t-2 right_hip_pitch rotation error                       | -Inf | Inf |                                  |          |                          |
    | 51  | t-2 right_knee_pitch rotation error                      | -Inf | Inf |                                  |          |                          |
    | 52  | t-2 right_ankle_pitch rotation error                     | -Inf | Inf |                                  |          |                          |
    | 53  | t-2 left_hip_yaw rotation error                          | -Inf | Inf |                                  |          |                          |
    | 54  | t-2 left_hip_roll rotation error                         | -Inf | Inf |                                  |          |                          |
    | 55  | t-2 left_hip_pitch rotation error                        | -Inf | Inf |                                  |          |                          |
    | 56  | t-2 left_knee_pitch rotation error                       | -Inf | Inf |                                  |          |                          |
    | 57  | t-2 left_ankle_pitch rotation error                      | -Inf | Inf |                                  |          |                          |
    | 58  | t-2 neck_pitch rotation error                            | -Inf | Inf |                                  |          |                          |
    | 59  | t-2 head_pitch rotation error                            | -Inf | Inf |                                  |          |                          |
    | 60  | t-2 head_yaw rotation error                              | -Inf | Inf |                                  |          |                          |
    | 61  | t-3 right_hip_yaw rotation error                         | -Inf | Inf |                                  |          |                          |
    | 62  | t-3 right_hip_roll rotation error                        | -Inf | Inf |                                  |          |                          |
    | 63  | t-3 right_hip_pitch rotation error                       | -Inf | Inf |                                  |          |                          |
    | 64  | t-3 right_knee_pitch rotation error                      | -Inf | Inf |                                  |          |                          |
    | 65  | t-3 right_ankle_pitch rotation error                     | -Inf | Inf |                                  |          |                          |
    | 66  | t-3 left_hip_yaw rotation error                          | -Inf | Inf |                                  |          |                          |
    | 67  | t-3 left_hip_roll rotation error                         | -Inf | Inf |                                  |          |                          |
    | 68  | t-3 left_hip_pitch rotation error                        | -Inf | Inf |                                  |          |                          |
    | 69  | t-3 left_knee_pitch rotation error                       | -Inf | Inf |                                  |          |                          |
    | 70  | t-3 left_ankle_pitch rotation error                      | -Inf | Inf |                                  |          |                          |
    | 71  | t-3 neck_pitch rotation error                            | -Inf | Inf |                                  |          |                          |
    | 72  | t-3 head_pitch rotation error                            | -Inf | Inf |                                  |          |                          |
    | 73  | t-3 head_yaw rotation error                              | -Inf | Inf |                                  |          |                          |

    | 74  | left foot in contact with the floor                      | -Inf | Inf |                                  |          |                          |
    | 75  | right foot in contact with the floor                     | -Inf | Inf |                                  |          |                          |

    | x76  | t                                                        | -Inf | Inf |                                  |          |                          |
    | x74  | sinus                                                   | -Inf | Inf |                                  |          |                          |

    """

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 50,
    }

    # Ideas
    # Low pass filter on the joint angles

    def __init__(self, **kwargs):
        utils.EzPickle.__init__(self, **kwargs)
        observation_space = Box(low=-np.inf, high=np.inf, shape=(86,), dtype=np.float64)
        self.target_velocity = np.asarray([0, 0, 0])  # x, y, yaw
        self.joint_history_length = 3
        self.joint_error_history = self.joint_history_length * [15 * [0]]
        self.joint_ctrl_history = self.joint_history_length * [15 * [0]]

        self.left_foot_in_contact = 0
        self.right_foot_in_contact = 0
        self.startup_cooldown = 1.0

        self.prev_t = 0
        self.init_pos = np.array(
            [
                -0.013946457213457239,
                0.07918837709879874,
                0.5325073962634973,
                -1.6225192902713386,
                0.9149246381274986,
                0.013627156377842975,
                0.07738878096596595,
                0.5933527914082196,
                -1.630548419252953,
                0.8621333440557593,
                -0.17453292519943295,
                -0.17453292519943295,
                8.65556854322817e-27,
                0,
                0,
            ]
        )
        MujocoEnv.__init__(
            self,
            "/home/antoine/MISC/mini_BDX/mini_bdx/robots/bdx/scene.xml",
            FRAME_SKIP,
            observation_space=observation_space,
            **kwargs,
        )

    def check_contact(self, body1_name, body2_name):
        body1_id = self.data.body(body1_name).id
        body2_id = self.data.body(body2_name).id

        for i in range(self.data.ncon):
            contact = self.data.contact[i]

            if (
                self.model.geom_bodyid[contact.geom1] == body1_id
                and self.model.geom_bodyid[contact.geom2] == body2_id
            ) or (
                self.model.geom_bodyid[contact.geom1] == body2_id
                and self.model.geom_bodyid[contact.geom2] == body1_id
            ):
                return True

        return False

    def feet_contact_reward(self):
        return self.right_foot_in_contact + self.left_foot_in_contact

    def velocity_tracking_reward(self):
        base_velocity = list(self.data.body("base").cvel[3:][:2]) + [
            self.data.body("base").cvel[:3][2]
        ]
        base_velocity = np.asarray(base_velocity)
        return np.exp(-np.square(base_velocity - self.target_velocity).sum())

    def smoothness_reward(self):
        # Warning, this function only works if the history is 3 :)
        smooth = 0
        t0 = self.joint_ctrl_history[0]
        t_minus1 = self.joint_ctrl_history[1]
        t_minus2 = self.joint_ctrl_history[2]

        for i in range(15):
            smooth += 2.5 * np.square(t0[i] - t_minus1[i]) + 1.5 * np.square(
                t0[i] - 2 * t_minus1[i] + t_minus2[i]
            )

        return -smooth

    def smoothness_reward2(self):
        # Warning, this function only works if the history is 3 :)
        smooth = 0
        t0 = self.joint_ctrl_history[0]
        t_minus1 = self.joint_ctrl_history[1]
        t_minus2 = self.joint_ctrl_history[2]

        for i in range(15):
            smooth += np.square(t0[i] - t_minus1[i]) + np.square(
                t_minus1[i] - t_minus2[i]
            )
            # smooth += 2.5 * np.square(t0[i] - t_minus1[i]) + 1.5 * np.square(
            #     t0[i] - 2 * t_minus1[i] + t_minus2[i]
            # )

        return -smooth

    def joint_velocity_reward(self):
        return -np.square(self.data.qvel[:]).sum()

    def walking_height_reward(self):
        return (
            -np.square((self.get_body_com("base")[2] - 0.15)) * 100
        )  # "normal" walking height is about 0.15m

    def upright_reward(self):
        # angular distance to upright position in reward
        Z_vec = np.array(self.data.body("base").xmat).reshape(3, 3)[:, 2]
        return np.square(np.dot(np.array([0, 0, 1]), Z_vec))

    def init_position_reward(self):
        return -np.square(self.data.qpos[7 : 7 + 15] - self.init_pos).sum()

    def is_terminated(self) -> bool:
        rot = np.array(self.data.body("base").xmat).reshape(3, 3)
        Z_vec = rot[:, 2]
        upright = np.array([0, 0, 1])
        return (
            self.data.body("base").xpos[2] < 0.08 or np.dot(upright, Z_vec) <= 0
        )  # base z is below 0.08m or base has more than 90 degrees of tilt

    def action_LFP(self, action):
        # Low pass filter for the actions
        action_tminus1 = self.joint_ctrl_history[0]
        action_tminus2 = self.joint_ctrl_history[1]
        action_tminus3 = self.joint_ctrl_history[2]
        # return action * 0.5 + action_tminus1 * 0.5
        return (
            action * 0.5
            + action_tminus1 * 0.3
            + action_tminus2 * 0.15
            + action_tminus3 * 0.05
        )

        d_action = action - action_tminus1

        action = [
            a if abs(d) < 0.1 else b
            for a, b, d in zip(action, action_tminus1, d_action)
        ]
        return action

    def step(self, a):
        # https://www.nature.com/articles/s41598-023-38259-7.pdf

        # add random force
        # if np.random.rand() < 0.05:
        #     self.data.xfrc_applied[self.data.body("base").id][:3] = [
        #         np.random.randint(-5, 5),
        #         np.random.randint(-5, 5),
        #         np.random.randint(-5, 5),
        #     ]  # absolute

        t = self.data.time
        dt = t - self.prev_t
        if self.startup_cooldown > 0:
            self.startup_cooldown -= dt

        if self.startup_cooldown > 0:
            self.do_simulation(self.init_pos, FRAME_SKIP)
            reward = 0
        else:
            self.do_simulation(a, FRAME_SKIP)
            # self.do_simulation(self.action_LFP(a), 4)
            self.right_foot_in_contact = self.check_contact("foot_module", "floor")
            self.left_foot_in_contact = self.check_contact("foot_module_2", "floor")

            reward = (
                0.05  # time reward
                # + 0.1 * self.walking_height_reward()
                # + 0.1 * self.upright_reward()
                # + 0.1 * self.velocity_tracking_reward()
                + 0.01 * self.smoothness_reward2()
                + 0.1 * self.init_position_reward()
                # + 0.1 * self.feet_contact_reward()
                # + 0.1 * self.joint_angle_deviation_reward()
                # + 0.01 * self.follow_walk_engine_reward(dt)
                # + 0.001 * self.joint_velocity_reward()
            )

        ob = self._get_obs()

        if self.render_mode == "human":
            self.render()

        self.prev_t = t

        return (ob, reward, self.is_terminated(), False, {})  # terminated  # truncated

    def reset_model(self):
        self.prev_t = self.data.time
        self.startup_cooldown = 1.0

        # self.model.opt.gravity[:] = [0, 0, 0]  # no gravity

        self.goto_init()

        self.joint_error_history = self.joint_history_length * [15 * [0]]
        self.joint_ctrl_history = self.joint_history_length * [15 * [0]]
        # qpos = self.data.qpos

        # LATEST
        # added randomization to the initial position
        # for i in range(7, len(qpos)):
        #     qpos[i] = np.random.uniform(-0.3, 0.3)

        # self.init_qpos = qpos.copy().flatten()

        # Randomize later
        # self.target_velocity = np.asarray([0, 0, 0])  # x, y, yaw
        self.target_velocity = np.asarray([0, 0, 0])  # x, y, yaw

        self.set_state(self.data.qpos, self.data.qvel)
        return self._get_obs()

    def goto_init(self):
        self.data.qpos[:] = np.zeros(len(self.data.qpos[:]))
        self.data.qpos[2] = 0.15
        # self.data.qpos[3 : 3 + 4] = [1, 0, 0, 0]
        self.data.qpos[3 : 3 + 4] = [1, 0, 0.08, 0]

        self.data.qvel[:] = np.zeros(len(self.data.qvel[:]))
        self.data.qpos[7 : 7 + 15] = self.init_pos
        self.data.ctrl[:] = self.init_pos

    def _get_obs(self):
        joints_rotations = self.data.qpos[7 : 7 + 15]
        joints_velocities = self.data.qvel[6 : 6 + 15]

        # joints_error = self.data.ctrl - self.data.qpos[7 : 7 + 13]
        # self.joint_error_history.append(joints_error)
        # self.joint_error_history = self.joint_error_history[
        #     -self.joint_history_length :
        # ]

        angular_velocity = self.data.body("base").cvel[
            :3
        ]  # TODO this is imu, add noise to it later
        linear_velocity = self.data.body("base").cvel[3:]

        self.joint_ctrl_history.append(self.data.ctrl.copy())
        self.joint_ctrl_history = self.joint_ctrl_history[-self.joint_history_length :]

        return np.concatenate(
            [
                joints_rotations,
                joints_velocities,
                angular_velocity,
                linear_velocity,
                self.target_velocity,
                np.array(self.joint_ctrl_history).flatten(),
                [self.left_foot_in_contact, self.right_foot_in_contact],
            ]
        )
