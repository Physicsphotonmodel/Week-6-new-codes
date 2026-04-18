"""
Module: main.py
Description: Main asynchronous loop for vehicle control. 
             Implements event-driven dynamic replanning.
"""

import argparse
import logging
import sys
import time
import asyncio

from maze import Action, Maze
from score import ScoreboardServer, ScoreboardFake
from node import Direction
from hm10_bleak import HM10BleakClient

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)

DEBUG = 1

# Configuration Constants
TEAM_NAME = "TEAM_7"
SERVER_URL = "http://carcar.ntuee.org/scoreboard"
MAZE_FILE = "data/small_maze.csv"
TARGET_BT_NAME = "HM10_7" 

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="0: treasure-hunting, 1: self-testing", type=int)
    parser.add_argument("--maze-file", default=MAZE_FILE, help="Maze file", type=str)
    parser.add_argument("--bt-port", default="COM3", help="Bluetooth port", type=str)
    parser.add_argument("--team-name", default=TEAM_NAME, help="Your team name", type=str)
    parser.add_argument("--server-url", default=SERVER_URL, help="Server URL", type=str)
    return parser.parse_args()

async def main(mode: int, bt_port: str, team_name: str, server_url: str, maze_file: str):
    maze = Maze(maze_file)
    scoreboard = ScoreboardServer(team_name, server_url)

    # Global State Tracking
    TOTAL_TIME_LIMIT = 68.0 # 預留2秒緩衝
    start_time = None
    
    current_node = maze.get_start_point() 
    current_dir = Direction.NORTH 
    node_scores = maze.get_all_node_scores(current_node) # 或使用你的真實分數檔案
    
    unvisited = set(node_scores.keys())
    unvisited.discard(current_node.index)
    action_list = []

    def replan() -> bool:
        """
        Calculates the next optimal segment and fast-forwards the expected 
        state (current_node, current_dir) to the destination of this segment.
        """
        nonlocal current_node, current_dir, unvisited, action_list
        
        if start_time is None:
            remaining_time = TOTAL_TIME_LIMIT
        else:
            remaining_time = TOTAL_TIME_LIMIT - (time.time() - start_time)
            
        path_nodes = maze.get_next_target_path(current_node, current_dir, remaining_time, unvisited, node_scores)
        
        if not path_nodes or len(path_nodes) < 2:
            return False
            
        actions = maze.getActions(path_nodes)
        action_list = list(maze.actions_to_str(actions))
        
        # Remove targeted nodes from unvisited pool
        for n in path_nodes[1:]:
            unvisited.discard(n.index)
        
        # Fast-forward direction and node to expected arrival state
        temp_dir = current_dir
        for i in range(len(path_nodes)-1):
            _, temp_dir = maze.getAction(temp_dir, path_nodes[i], path_nodes[i+1])
        
        current_dir = temp_dir
        current_node = path_nodes[-1]
        return True

    # ==========================================
    # 1. Initialization and Connection
    # ==========================================
    log.info(f"Connecting to {TARGET_BT_NAME} via Bleak...")
    interface = HM10BleakClient(target_name=TARGET_BT_NAME)
    
    if not await interface.connect():
        log.error("Connection failed.")
        sys.exit(1)
        
    while True:
        response = interface.listen()
        if response and "READY" in response:
            log.info("Received READY signal. Initializing dynamic planner...")
            start_time = time.time()  # Start the mission clock
            
            if not replan():
                log.error("Failed to generate initial path.")
                sys.exit(1)
                
            log.info("Sending START command ('s')...")
            await interface.send('s')
            break 
        await asyncio.sleep(0.1)
        
    log.info("Vehicle started.")

    # ==========================================
    # 2. State Machine Main Loop
    # ==========================================
    if mode == 0:
        log.info("Mode 0: Treasure-hunting mode activated.")

        while True: 
            response = interface.listen()
            if DEBUG == 1:
                if response != '':
                    log.info(f"RAW RX: {repr(response)}")
                
            if response:
                for line in response.splitlines():
                    line = line.strip()
                    if not line: continue
                    
                    # --- Event: RFID Tag Read ---
                    if line.startswith("ID"): 
                        uid_str = line[2:] 
                        log.info(f"Card ID: {uid_str}")
                        scoreboard.add_UID(uid_str) 
                        time.sleep(0.1) 
                        
                    # --- Event: Node Arrival ---
                    elif line == "K":
                        log.info("Vehicle arrived at an intersection (K).")
                        
                        # If action list is empty, we have reached the destination of the current segment
                        if not action_list:
                            log.info("Segment completed. Replanning next segment based on real-time...")
                            if not replan():
                                log.info("Time limit reached or no viable targets. Halting.")
                                await interface.send('h')
                                continue
                                
                        # Dispatch the next sequential instruction
                        if action_list:
                            cmd = action_list.pop(0)
                            await interface.send(cmd)
                            log.info(f"Dispatched command: {cmd}")
                        else:
                            await interface.send('h') 
                            
                    # --- Event: Action Completed ---
                    elif line in ["L", "R", "B", "F", "S"]: 
                        log.info(f"Action completed ({line}). Resuming tracking...")
            
            await asyncio.sleep(0.05)
            
    elif mode == 1:
        log.info("Mode 1: Self-testing mode activated.")
        while True: 
            response = interface.listen()
            if response != '':
                log.info(f"RAW RX: {repr(response)}")
            await asyncio.sleep(0.05)
    else:
        log.error("Invalid mode selected.")
        sys.exit(1)

if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(main(**vars(args)))
    except KeyboardInterrupt:
        log.info("Program manually interrupted.")