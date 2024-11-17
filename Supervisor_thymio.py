from agent import Agent
from styles import styles
import streamlit as st
import random
import ell
import numpy as np
from matplotlib import pyplot as plt
import re
from ell import Message
import time
from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
import asyncio

prox_left = None
prox_right = None


def init_thymio():
    thymio_serial_ports = ThymioSerialPort.get_ports()
    serial_port = thymio_serial_ports[0].device
    th = Thymio(use_tcp=False,
                serial_port=serial_port,
                host=None,
                refreshing_coverage={
                    "prox.horizontal",
                    "button.center",
                    "prox.ground.delta"
                }
                )
    th.connect(delay=3, progress=lambda : print("Connecting to Thymio..."))
    time.sleep(2)
    for node in th.nodes():
        print(node)
    return th


th = init_thymio()

class ThymioSupervisor:
    
    def __init__(self, n_agents=2, speed=100) -> None:
        # Initialize the Supervisor
        self.agents = list(th.nodes())
       
        self.speed = speed

        # Start the game
        self._run()
    
    def read_orders(self):
        import os
        order_received = False
        while not order_received:
            try:
                with open(f"orders.txt", "r") as f:
                    lines = f.read().split("\n")
                print("Read", lines)
                order_received = True
                break
            except FileNotFoundError:
                print('waiting for orders file')
                time.sleep(1)
                continue
        os.remove("orders.txt")

        return lines
                

    
    def _run(self):
        global prox_left, prox_right

        # Initialize the Thymio
        #assert len(self.agents) == len(th.nodes())

        for agent, node_id in zip(self.agents, th.nodes()):
            # agent.link_thymio(node_id)

            print(f"Agent {agent} linked to node {node_id}")

            # Init positions to node
            prox_left = th[node_id]["prox.ground.delta"][0]
            prox_right = th[node_id]["prox.ground.delta"][1]
            # print(f"Agent {agent.name}:{agent.node_id}, going to init node")
            prox_right, prox_left = th[agent]["prox.ground.delta"]
            self.play(agent)

        # While the game is running
        while True:

            # Interpret in robot space


            # Interpret in robot space
            orders = self.read_orders()
            print("FJZEFJZEFKER")
            for agent, direction in zip(self.agents, orders):
                print(direction)
                node_id = agent

                # Init sensor values
                prox_right, prox_left = th[node_id]["prox.ground.delta"]
                #agent.direction = "RIGHT" # TODO : change this
                self.rotate(node_id, direction)
                th[node_id]["motor.left.target"] = 0
                th[node_id]["motor.right.target"] = 0

                self.play(node_id)
                th[node_id]["motor.left.target"] = 0
                th[node_id]["motor.right.target"] = 0

            


    def rotate(self, node_id, rotation_order="RIGHT"):
    #rotation_time = 2.20
        rotation_time = 2.30
        if rotation_order == "RIGHT":
            th[node_id]["motor.left.target"] = self.speed
            th[node_id]["motor.right.target"] = -self.speed
        elif rotation_order == "LEFT":
            th[node_id]["motor.left.target"] = -self.speed
            th[node_id]["motor.right.target"] = self.speed
        elif rotation_order == "UP":
            th[node_id]["motor.left.target"] = self.speed
            th[node_id]["motor.right.target"] = self.speed
            rotation_time /= 4
        elif rotation_order == "DOWN":
            th[node_id]["motor.left.target"] = -self.speed
            th[node_id]["motor.right.target"] = self.speed
            rotation_time *= 2
            # TODO : fine tune
        else:
            raise ValueError("Invalid rotation order")

        time.sleep(rotation_time)
        print("Rotation done !")

        th[node_id]["motor.left.target"] = self.speed
        th[node_id]["motor.right.target"] = self.speed


    def intersection(self, node_id, prox_left, prox_right):

        ground_left = th[node_id]["prox.ground.delta"][0]
        ground_right = th[node_id]["prox.ground.delta"][1]

        thresh = 300
        # Check if intersection has been reached
        delta = max(prox_left - ground_left , prox_right - ground_right)
        print("delta", delta , "ground_left", ground_left, "prox_left", prox_left, "ground_right", ground_right, "prox_right", prox_right)

        if delta > thresh:
            print("Intersection detected !")
            # th.set_variable_observer(node_id, rotate) # a changer rihgt/left

            # Avoid correction at intersection
            th[node_id]["motor.left.target"] = self.speed
            th[node_id]["motor.right.target"] = self.speed
            time.sleep(1.9) # We need to wait a bit before rotating to get a good angle
            th[node_id]["motor.left.target"] = 0
            th[node_id]["motor.right.target"] = 0
            return True
        return False

    def play(self, node_id):
        th.set_variable_observer(node_id, line_behavior)
        print("Playing ", node_id)

        ground_left = th[node_id]["prox.ground.delta"][0]
        ground_right = th[node_id]["prox.ground.delta"][1]


        # TODO Take a decision from buffered values
        # TODO cooldown intersection
        while not self.intersection(node_id, ground_left, ground_right):
            ground_left = th[node_id]["prox.ground.delta"][0]
            ground_right = th[node_id]["prox.ground.delta"][1]
            time.sleep(0.1)

        th.set_variable_observer(node_id, lambda node_id: None)


def line_behavior(node_id, speed=100):
    global prox_left, prox_right
    max_steer = 10

    ground_left = th[node_id]["prox.ground.delta"][0]
    ground_right = th[node_id]["prox.ground.delta"][1]

    # Set motor speed and correction
    tmp = max_steer * ground_left - max_steer * ground_right
    steerL = tmp // speed
    th[node_id]["motor.left.target"] = speed + steerL
    th[node_id]["motor.right.target"] = speed - steerL
    print("Motor left", th[node_id]["motor.left.target"], "Motor right", th[node_id]["motor.right.target"] , "steerL", steerL)
    prox_left, prox_right = th[node_id]["prox.ground.delta"]

if __name__ == "__main__":
    s = ThymioSupervisor(n_agents=1)
    #print(s.read_orders())
    