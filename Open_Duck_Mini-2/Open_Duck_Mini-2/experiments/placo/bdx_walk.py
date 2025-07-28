import argparse
import time
import warnings

import numpy as np
import placo
from placo_utils.visualization import (
    footsteps_viz,
    frame_viz,
    line_viz,
    robot_frame_viz,
    robot_viz,
)

from mini_bdx.bdx_mujoco_server import BDXMujocoServer
from mini_bdx.hwi import HWI

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument(
    "-p", "--pybullet", action="store_true", help="PyBullet visualization"
)
parser.add_argument(
    "-m", "--meshcat", action="store_true", help="MeshCat visualization"
)
parser.add_argument("-r", "--robot", action="store_true", help="run on real robot")
parser.add_argument("--mujoco", action="store_true", help="Mujoco visualization")
args = parser.parse_args()

DT = 0.01
REFINE = 10
model_filename = "../../mini_bdx/robots/bdx/robot.urdf"

# Loading the robot
robot = placo.HumanoidRobot(model_filename)
robot.set_joint_limits("left_knee", -2, -0.01)
robot.set_joint_limits("right_knee", -2, -0.01)

# Walk parameters - if double_support_ratio is not set to 0, should be greater than replan_frequency
parameters = placo.HumanoidParameters()

parameters.double_support_ratio = 0.2  # Ratio of double support (0.0 to 1.0)
parameters.startend_double_support_ratio = (
    1.5  # Ratio duration of supports for starting and stopping walk
)
parameters.planned_timesteps = 48  # Number of timesteps planned ahead
parameters.replan_timesteps = 10  # Replanning each n timesteps
# parameters.zmp_reference_weight = 1e-6

# Posture parameters
parameters.walk_com_height = 0.15  # Constant height for the CoM [m]
parameters.walk_foot_height = 0.006  # Height of foot rising while walking [m]
parameters.walk_trunk_pitch = np.deg2rad(10)  # Trunk pitch angle [rad]
parameters.walk_foot_rise_ratio = (
    0.2  # Time ratio for the foot swing plateau (0.0 to 1.0)
)

# Timing parameters
# parameters.single_support_duration = 1 / (
#     0.5 * np.sqrt(9.81 / parameters.walk_com_height)
# )  # Constant height for the CoM [m]  # Duration of single support phase [s]
parameters.single_support_duration = 0.2  # Duration of single support phase [s]
parameters.single_support_timesteps = (
    10  # Number of planning timesteps per single support phase
)

# Feet parameters
parameters.foot_length = 0.06  # Foot length [m]
parameters.foot_width = 0.006  # Foot width [m]
parameters.feet_spacing = 0.12  # Lateral feet spacing [m]
parameters.zmp_margin = 0.0  # ZMP margin [m]
parameters.foot_zmp_target_x = 0.0  # Reference target ZMP position in the foot [m]
parameters.foot_zmp_target_y = 0.0  # Reference target ZMP position in the foot [m]

# Limit parameters
parameters.walk_max_dtheta = 1  # Maximum dtheta per step [rad]
parameters.walk_max_dy = 0.1  # Maximum dy per step [m]
parameters.walk_max_dx_forward = 0.08  # Maximum dx per step forward [m]
parameters.walk_max_dx_backward = 0.03  # Maximum dx per step backward [m]

# Creating the kinematics solver
solver = placo.KinematicsSolver(robot)
solver.enable_velocity_limits(True)
# solver.enable_joint_limits(False)
robot.set_velocity_limits(12.0)
solver.dt = DT / REFINE

# Creating the walk QP tasks
tasks = placo.WalkTasks()
# tasks.trunk_mode = True
# tasks.com_x = 0.04
tasks.initialize_tasks(solver, robot)
tasks.left_foot_task.orientation().mask.set_axises("yz", "local")
tasks.right_foot_task.orientation().mask.set_axises("yz", "local")
# tasks.trunk_orientation_task.configure("trunk_orientation", "soft", 1e-4)
# tasks.left_foot_task.orientation().configure("left_foot_orientation", "soft", 1e-6)
# tasks.right_foot_task.orientation().configure("right_foot_orientation", "soft", 1e-6)

# Creating a joint task to assign DoF values for upper body
elbow = -50 * np.pi / 180
shoulder_roll = 0 * np.pi / 180
shoulder_pitch = 20 * np.pi / 180
joints_task = solver.add_joints_task()
joints_task.set_joints(
    {
        # "left_shoulder_roll": shoulder_roll,
        # "left_shoulder_pitch": shoulder_pitch,
        # "left_elbow": elbow,
        # "right_shoulder_roll": -shoulder_roll,
        # "right_shoulder_pitch": shoulder_pitch,
        # "right_elbow": elbow,
        "head_pitch": 0.0,
        "head_yaw": 0.0,
        "neck_pitch": 0.0,
        "left_antenna": 0.0,
        "right_antenna": 0.0,
        # "left_ankle_roll": 0.0,
        # "right_ankle_roll": 0.0
    }
)
joints_task.configure("joints", "soft", 1.0)

# cam = solver.add_centroidal_momentum_task(np.array([0., 0., 0.]))
# cam.mask.set_axises("x", "custom")
# cam.mask.R_custom_world = robot.get_T_world_frame("trunk")[:3, :3].T
# cam.configure("cam", "soft", 1e-3)

# Placing the robot in the initial position
print("Placing the robot in the initial position...")
tasks.reach_initial_pose(
    np.eye(4),
    parameters.feet_spacing,
    parameters.walk_com_height,
    parameters.walk_trunk_pitch,
)
print("Initial position reached")


# Creating the FootstepsPlanner
repetitive_footsteps_planner = placo.FootstepsPlannerRepetitive(parameters)
d_x = 0.1
d_y = 0.0
d_theta = 0.0
nb_steps = 5
repetitive_footsteps_planner.configure(d_x, d_y, d_theta, nb_steps)

# Planning footsteps
T_world_left = placo.flatten_on_floor(robot.get_T_world_left())
T_world_right = placo.flatten_on_floor(robot.get_T_world_right())
footsteps = repetitive_footsteps_planner.plan(
    placo.HumanoidRobot_Side.left, T_world_left, T_world_right
)

supports = placo.FootstepsPlanner.make_supports(
    footsteps, True, parameters.has_double_support(), True
)

# Creating the pattern generator and making an initial plan
walk = placo.WalkPatternGenerator(robot, parameters)
trajectory = walk.plan(supports, robot.com_world(), 0.0)

if args.pybullet:
    # Loading the PyBullet simulation
    import pybullet as p
    from onshape_to_robot.simulation import Simulation

    sim = Simulation(model_filename, realTime=True, dt=DT, ignore_self_collisions=True)
elif args.meshcat:
    # Starting Meshcat viewer
    viz = robot_viz(robot)
    footsteps_viz(trajectory.get_supports())
elif args.robot:
    hwi = HWI()
    hwi.turn_on()
    time.sleep(2)
elif args.mujoco:
    time_since_last_right_contact = 0.0
    time_since_last_left_contact = 0.0
    bdx_mujoco_server = BDXMujocoServer(
        model_path="../../mini_bdx/robots/bdx", gravity_on=True
    )
    bdx_mujoco_server.start()
else:
    print("No visualization selected, use either -p or -m")
    exit()

# Timestamps
start_t = time.time()
initial_delay = -1.0
t = initial_delay
last_display = time.time()
last_replan = 0
petage_de_gueule = False
got_input = False
while True:
    if got_input:
        repetitive_footsteps_planner.configure(d_x, d_y, d_theta, nb_steps)
        got_input = False

    # Invoking the IK QP solver
    for k in range(REFINE):
        # Updating the QP tasks from planned trajectory
        if not petage_de_gueule:
            tasks.update_tasks_from_trajectory(trajectory, t - DT + k * DT / REFINE)

        robot.update_kinematics()
        qd_sol = solver.solve(True)
    # solver.dump_status()

    # Ensuring the robot is kinematically placed on the floor on the proper foot to avoid integration drifts
    # if not trajectory.support_is_both(t):
    # robot.update_support_side(str(trajectory.support_side(t)))
    # robot.ensure_on_floor()

    # If enough time elapsed and we can replan, do the replanning
    if (
        t - last_replan > parameters.replan_timesteps * parameters.dt()
        and walk.can_replan_supports(trajectory, t)
    ):
        last_replan = t

        # Replanning footsteps from current trajectory
        supports = walk.replan_supports(repetitive_footsteps_planner, trajectory, t)

        # Replanning CoM trajectory, yielding a new trajectory we can switch to
        trajectory = walk.replan(supports, trajectory, t)

        if args.meshcat:
            # Drawing footsteps
            footsteps_viz(supports)

            # Drawing planned CoM trajectory on the ground
            coms = [
                [*trajectory.get_p_world_CoM(t)[:2], 0.0]
                for t in np.linspace(trajectory.t_start, trajectory.t_end, 100)
            ]
            line_viz("CoM_trajectory", np.array(coms), 0xFFAA00)

    # During the warmup phase, the robot is enforced to stay in the initial position
    if args.pybullet:
        if t < -2:
            T_left_origin = sim.transformation("origin", "left_foot_frame")
            T_world_left = sim.poseToMatrix(([0.0, 0.0, 0.05], [0.0, 0.0, 0.0, 1.0]))
            T_world_origin = T_world_left @ T_left_origin

            sim.setRobotPose(*sim.matrixToPose(T_world_origin))

        joints = {joint: robot.get_joint(joint) for joint in sim.getJoints()}
        applied = sim.setJoints(joints)
        sim.tick()

    # Updating meshcat display periodically
    elif args.meshcat:
        if time.time() - last_display > 0.01:
            last_display = time.time()
            viz.display(robot.state.q)

            # frame_viz("left_foot_target", trajectory.get_T_world_left(t))
            # frame_viz("right_foot_target", trajectory.get_T_world_right(t))
            # robot_frame_viz(robot, "left_foot")
            # robot_frame_viz(robot, "right_foot")

            T_world_trunk = np.eye(4)
            T_world_trunk[:3, :3] = trajectory.get_R_world_trunk(t)
            T_world_trunk[:3, 3] = trajectory.get_p_world_CoM(t)
            frame_viz("trunk_target", T_world_trunk)
            # footsteps_viz(trajectory.get_supports())

    if args.robot or args.mujoco:
        angles = {
            "right_hip_yaw": robot.get_joint("right_hip_yaw"),
            "right_hip_roll": robot.get_joint("right_hip_roll"),
            "right_hip_pitch": robot.get_joint("right_hip_pitch"),
            "right_knee": robot.get_joint("right_knee"),
            "right_ankle": robot.get_joint("right_ankle"),
            "left_hip_yaw": robot.get_joint("left_hip_yaw"),
            "left_hip_roll": robot.get_joint("left_hip_roll"),
            "left_hip_pitch": robot.get_joint("left_hip_pitch"),
            "left_knee": robot.get_joint("left_knee"),
            "left_ankle": robot.get_joint("left_ankle"),
            "neck_pitch": robot.get_joint("neck_pitch"),
            "head_pitch": robot.get_joint("head_pitch"),
            "head_yaw": robot.get_joint("head_yaw"),
        }
        if args.robot:
            hwi.set_position_all(angles)
        elif args.mujoco:
            right_contact, left_contact = bdx_mujoco_server.get_feet_contact()
            if left_contact:
                time_since_last_left_contact = 0.0
            if right_contact:
                time_since_last_right_contact = 0.0
            # print("time since last left contact :", time_since_last_left_contact)
            # print("time since last right contact :", time_since_last_right_contact)
            bdx_mujoco_server.send_action(list(angles.values()))

        if (
            time_since_last_left_contact > parameters.single_support_duration
            or time_since_last_right_contact > parameters.single_support_duration
        ):
            petage_de_gueule = True
            # print("pétage de gueule")
        else:
            petage_de_gueule = False

        time_since_last_left_contact += DT
        time_since_last_right_contact += DT

        if bdx_mujoco_server.key_pressed is not None:
            got_input = True
            d_x = 0.05
        else:
            got_input = True
            d_x = 0
            d_y = 0
            d_theta = 0

    t += DT
    # print(t)
    while time.time() < start_t + t:
        time.sleep(1e-5)
