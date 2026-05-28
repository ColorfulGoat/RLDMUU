#!/usr/bin/env python3
#
# Copyright 2019 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Ryan Shim, Gilbert, Tomas

import copy
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from ..common.settings import ENABLE_VISUAL, ENABLE_STACKING, OBSERVE_STEPS, MODEL_STORE_INTERVAL, GRAPH_DRAW_INTERVAL, MAX_TRAINING_EPISODES

from ..common.storagemanager import StorageManager
from ..common.graph import Graph
from ..common.logger import Logger
if ENABLE_VISUAL:
    from ..common.visual import DrlVisual
from ..common import utilities as util

from .dqn import DQN
from .ddpg import DDPG
from .td3 import TD3
from .redq import REDQ

from turtlebot3_msgs.srv import DrlStep, Goal
from ros_gz_interfaces.srv import ControlWorld

import rclpy
from rclpy.node import Node
from ..common.replaybuffer import ReplayBuffer

class DrlAgent(Node):
    def __init__(self, training, algorithm, load_session="", load_episode=0, real_robot=0):
        super().__init__(algorithm + '_agent')
        self.algorithm = algorithm
        self.training = int(training)
        self.load_session = load_session
        self.episode = int(load_episode)
        self.real_robot = real_robot

        if (not self.training and not self.load_session):
            quit("\033[1m" + "\033[93m" + "Invalid command: Testing but no model to load specified, see readme for correct format" + "\033[0m}")
        self.device = util.check_gpu()
        self.sim_speed = util.get_simulation_speed(util.stage) if not self.real_robot else 1
        print(f"{'training' if (self.training) else 'testing' } on stage: {util.stage}")
        self.total_steps = 0
        self.observe_steps = OBSERVE_STEPS
        self.stop_training = False

        if self.algorithm == 'dqn':
            self.model = DQN(self.device, self.sim_speed)
        elif self.algorithm == 'ddpg':
            self.model = DDPG(self.device, self.sim_speed)
        elif self.algorithm == 'td3':
            self.model = TD3(self.device, self.sim_speed)
        elif self.algorithm == 'redq':
            self.model = REDQ(self.device, self.sim_speed)
        else:
            quit("\033[1m" + "\033[93m" + f"invalid algorithm specified ({self.algorithm}), choose one of: dqn, ddpg, td3, redq" + "\033[0m}")

        self.replay_buffer = ReplayBuffer(self.model.buffer_size)
        self.graph = Graph()

        # ===================================================================== #
        #                             Model loading                             #
        # ===================================================================== #

        self.sm = StorageManager(self.algorithm, self.load_session, self.episode, self.device, util.stage)

        if self.load_session:
            del self.model
            self.model = self.sm.load_model()
            self.model.device = self.device
            self.sm.load_weights(self.model.networks)
            if self.training:
                self.replay_buffer.buffer = self.sm.load_replay_buffer(self.model.buffer_size, os.path.join(self.load_session, 'stage'+str(self.sm.stage)+'_latest_buffer.pkl'))
            self.graph.session_dir = self.sm.session_dir
            self.total_steps = self.graph.set_graphdata(self.sm.load_graphdata(), self.episode)
            print(f"global steps: {self.total_steps}")
            print(f"loaded model {self.load_session} (eps {self.episode}): {self.model.get_model_parameters()}")
        else:
            self.sm.new_session_dir(util.stage)
            self.sm.store_model(self.model)

        self.graph.session_dir = self.sm.session_dir
        self.logger = Logger(self.training, self.sm.machine_dir, self.sm.session_dir, self.sm.session, self.model.get_model_parameters(), self.model.get_model_configuration(), str(util.stage), self.algorithm, self.episode)
        self._init_project_results_dir()
        if ENABLE_VISUAL:
            self.visual = DrlVisual(self.model.state_size, self.model.hidden_size)
            self.model.attach_visual(self.visual)
        # ===================================================================== #
        #                             Start Process                             #
        # ===================================================================== #

        self.step_comm_client = self.create_client(DrlStep, 'step_comm')
        self.goal_comm_client = self.create_client(Goal, 'goal_comm')
        if not self.real_robot:
            world_name = f'drl_stage{util.stage}'
            self.gazebo_control = self.create_client(
                ControlWorld, f'/world/{world_name}/control')
        self.process()



    def _get_workspace_root(self):
        """Return the project root used inside Docker. Usually /workspace."""
        base_path = os.getenv("DRLNAV_BASE_PATH")
        if base_path:
            return Path(base_path)

        if Path("/workspace").exists():
            return Path("/workspace")

        return Path.cwd()

    def _init_project_results_dir(self):
        """Create results/<algorithm>/<run_name>/ and initialize CSV logging."""
        self.workspace_root = self._get_workspace_root()

        # Use the actual session directory name so it matches the model folder.
        # Example: td3_0_stage_9
        self.run_name = Path(self.sm.session_dir).name

        self.project_results_dir = self.workspace_root / "results" / self.algorithm / self.run_name
        self.project_results_dir.mkdir(parents=True, exist_ok=True)

        self.project_csv_path = self.project_results_dir / ("train_log.csv" if self.training else "eval_log.csv")

        self.project_csv_fields = [
            "timestamp",
            "mode",
            "algorithm",
            "stage",
            "run_name",
            "episode",
            "total_steps",
            "episode_steps",
            "reward",
            "outcome",
            "outcome_label",
            "success",
            "collision",
            "timeout",
            "episode_duration_sec",
            "distance_traveled",
            "replay_buffer_size",
            "actor_loss_avg",
            "critic_loss_avg",
            "checkpoint_saved",
            "source_model_dir",
        ]

        if not self.project_csv_path.exists():
            with self.project_csv_path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.project_csv_fields)
                writer.writeheader()

        metadata_path = self.project_results_dir / "run_metadata.txt"
        if not metadata_path.exists():
            metadata_path.write_text(
                "\n".join([
                    f"algorithm={self.algorithm}",
                    f"stage={util.stage}",
                    f"mode={'train' if self.training else 'eval'}",
                    f"run_name={self.run_name}",
                    f"source_model_dir={self.sm.session_dir}",
                    f"results_dir={self.project_results_dir}",
                    f"created_at={datetime.now().isoformat(timespec='seconds')}",
                    f"model_parameters={self.model.get_model_parameters()}",
                    f"model_configuration={self.model.get_model_configuration()}",
                    "",
                ])
            )

        print(f"[project results] CSV -> {self.project_csv_path}")

    def _outcome_to_flags(self, outcome):
        label = util.translate_outcome(outcome)
        label_lower = str(label).lower()

        success = int("success" in label_lower)
        collision = int("collision" in label_lower)
        timeout = int("timeout" in label_lower or "time out" in label_lower)

        return label, success, collision, timeout

    def _write_project_csv_row(self, step, eps_duration, outcome, dist_traveled, reward_sum, loss_critic, loss_actor, checkpoint_saved):
        label, success, collision, timeout = self._outcome_to_flags(outcome)

        actor_loss_avg = (loss_actor / step) if (self.training and step > 0) else 0.0
        critic_loss_avg = (loss_critic / step) if (self.training and step > 0) else 0.0

        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "mode": "train" if self.training else "eval",
            "algorithm": self.algorithm,
            "stage": util.stage,
            "run_name": self.run_name,
            "episode": self.episode,
            "total_steps": self.total_steps,
            "episode_steps": step,
            "reward": reward_sum,
            "outcome": outcome,
            "outcome_label": label,
            "success": success,
            "collision": collision,
            "timeout": timeout,
            "episode_duration_sec": eps_duration,
            "distance_traveled": dist_traveled,
            "replay_buffer_size": self.replay_buffer.get_length() if self.training else "",
            "actor_loss_avg": actor_loss_avg,
            "critic_loss_avg": critic_loss_avg,
            "checkpoint_saved": int(checkpoint_saved),
            "source_model_dir": self.sm.session_dir,
        }

        try:
            with self.project_csv_path.open("a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.project_csv_fields)
                writer.writerow(row)
        except Exception as exc:
            print(f"[project results] WARNING: could not write CSV row: {exc}")

    def process(self):
        util.pause_simulation(self, self.real_robot)
        while rclpy.ok() and not self.stop_training:
            util.wait_new_goal(self)
            episode_done = False
            step, reward_sum, loss_critic, loss_actor = 0, 0, 0, 0
            action_past = [0.0, 0.0]
            state = util.init_episode(self)

            if ENABLE_STACKING:
                frame_buffer = [0.0] * (self.model.state_size * self.model.stack_depth * self.model.frame_skip)
                state = [0.0] * (self.model.state_size * (self.model.stack_depth - 1)) + list(state)
                next_state = [0.0] * (self.model.state_size * self.model.stack_depth)

            util.unpause_simulation(self, self.real_robot)
            time.sleep(0.5)
            episode_start = time.perf_counter()

            while not episode_done:
                if self.training and self.total_steps < self.observe_steps:
                    action = self.model.get_action_random()
                else:
                    action = self.model.get_action(state, self.training, step, ENABLE_VISUAL)

                action_current = action
                if self.algorithm == 'dqn':
                    action_current = self.model.possible_actions[action]

                # Take a step
                next_state, reward, episode_done, outcome, distance_traveled = util.step(self, action_current, action_past)
                action_past = copy.deepcopy(action_current)
                reward_sum += reward

                if ENABLE_STACKING:
                    frame_buffer = frame_buffer[self.model.state_size:] + list(next_state)      # Update big buffer with single step
                    next_state = []                                                         # Prepare next set of frames (state)
                    for depth in range(self.model.stack_depth):
                        start = self.model.state_size * (self.model.frame_skip - 1) + (self.model.state_size * self.model.frame_skip * depth)
                        next_state += frame_buffer[start : start + self.model.state_size]

                # Train
                if self.training == True:
                    self.replay_buffer.add_sample(state, action, [reward], next_state, [episode_done])
                    if self.replay_buffer.get_length() >= self.model.batch_size:
                        loss_c, loss_a, = self.model._train(self.replay_buffer)
                        loss_critic += loss_c
                        loss_actor += loss_a

                if ENABLE_VISUAL:
                    self.visual.update_reward(reward_sum)
                state = copy.deepcopy(next_state)
                step += 1
                time.sleep(self.model.step_time)

            # Episode done
            util.pause_simulation(self, self.real_robot)
            self.total_steps += step
            duration = time.perf_counter() - episode_start

            self.finish_episode(step, duration, outcome, distance_traveled, reward_sum, loss_critic, loss_actor)

    def finish_episode(self, step, eps_duration, outcome, dist_traveled, reward_sum, loss_critic, lost_actor):
            if self.total_steps < self.observe_steps:
                print(f"Observe phase: {self.total_steps}/{self.observe_steps} steps")
                return

            self.episode += 1
            print(f"Epi: {self.episode:<5}R: {reward_sum:<8.0f}outcome: {util.translate_outcome(outcome):<13}", end='')
            print(f"steps: {step:<6}steps_total: {self.total_steps:<7}time: {eps_duration:<6.2f}")

            checkpoint_saved = False

            if (not self.training):
                self.logger.update_test_results(step, outcome, dist_traveled, eps_duration, 0)
                self._write_project_csv_row(step, eps_duration, outcome, dist_traveled, reward_sum, 0, 0, checkpoint_saved)
                return

            self.graph.update_data(step, self.total_steps, outcome, reward_sum, loss_critic, lost_actor)
            self.logger.file_log.write(f"{self.episode}, {reward_sum}, {outcome}, {eps_duration}, {step}, {self.total_steps}, \
                                            {self.replay_buffer.get_length()}, {loss_critic / step}, {lost_actor / step}\n")
            self.logger.file_log.flush()

            if (self.episode % MODEL_STORE_INTERVAL == 0) or (self.episode == 1):
                self.sm.save_session(self.episode, self.model.networks, self.graph.graphdata, self.replay_buffer.buffer)
                self.logger.update_comparison_file(self.episode, self.graph.get_success_count(), self.graph.get_reward_average())
                checkpoint_saved = True

            if (self.episode % GRAPH_DRAW_INTERVAL == 0) or (self.episode == 1):
                self.graph.draw_plots(self.episode)

            self._write_project_csv_row(step, eps_duration, outcome, dist_traveled, reward_sum, loss_critic, lost_actor, checkpoint_saved)

            if self.training and MAX_TRAINING_EPISODES > 0 and self.episode >= MAX_TRAINING_EPISODES:
                print(f"Reached MAX_TRAINING_EPISODES={MAX_TRAINING_EPISODES}. Stopping training after episode {self.episode}.")
                self.stop_training = True




def main(args=sys.argv[1:]):
    rclpy.init(args=args)
    drl_agent = DrlAgent(*args)
    if getattr(drl_agent, "stop_training", False):
        drl_agent.destroy()
        rclpy.shutdown()
        return
    rclpy.spin(drl_agent)
    drl_agent.destroy()
    rclpy.shutdown()

def main_train(args=sys.argv[1:]):
    args = ['1'] + args
    main(args)

def main_test(args=sys.argv[1:]):
    args = ['0'] + args
    main(args)

def main_real(args=sys.argv[1:]):
    args = ['0'] + args + ['0']
    main(args)

if __name__ == '__main__':
    main()