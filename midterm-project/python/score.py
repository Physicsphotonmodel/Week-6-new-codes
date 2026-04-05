"""
Module: score.py
Description: Manages interactions with the central scoring server over Socket.IO 
             and provides a fake local scoreboard for offline testing.
"""

import abc
import csv
import logging
import re
from typing import Optional, Tuple, cast

import requests
import socketio

log = logging.getLogger("scoreboard")

class Scoreboard(abc.ABC):
    """Abstract base class for scoreboard integration."""
    
    @abc.abstractmethod
    def add_UID(self, UID_str: str) -> Tuple[int, float]:
        """Submits UID to server. Returns (score, time_remaining)."""
        pass

    @abc.abstractmethod
    def get_current_score(self) -> Optional[int]:
        """Fetches total score from server."""
        pass

class ScoreboardFake(Scoreboard):
    """Local simulation of the scoreboard for offline development."""
    
    def __init__(self, teamname, filepath):
        self.total_score = 0
        self.team = teamname
        log.info("Using fake scoreboard.")
        log.info(f"{self.team} is playing.")
        self._read_UID_file(filepath)
        self.visit_list = set()

    def _read_UID_file(self, filepath: str):
        self.uid_to_score = {}
        with open(filepath, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            for row in rows[1:]:
                uid, score = row
                self.uid_to_score[uid] = int(score)
        log.info("Successfully read the UID simulation file.")

    def add_UID(self, UID_str: str) -> Tuple[int, float]:
        log.debug(f"Adding UID: {UID_str}")

        if not isinstance(UID_str, str):
            raise ValueError(f"UID format error (expected: str, got: {UID_str})")
        if not re.match(r"^[0-9A-Fa-f]{8}$", UID_str):
            raise ValueError(f"UID format error (expected: 8 hex digits, got: {UID_str})")

        if UID_str not in self.uid_to_score:
            log.info(f"UID not registered: {UID_str}")
            return 0, 0
        elif UID_str in self.visit_list:
            log.info(f"UID already visited: {UID_str}")
            return 0, 0
        else:
            point = self.uid_to_score[UID_str]
            self.total_score += point
            log.info(f"Treasure found! Acquired {point} points.")
            self.visit_list.add(UID_str)
            return point, 0

    def get_current_score(self):
        return int(self.total_score)

class ScoreboardServer(Scoreboard):
    """Networked client handling real-time Socket.IO interactions with the competition server."""
    
    def __init__(self, teamname: str, host=f"http://localhost:3000", debug=False):
        self.teamname = teamname
        self.ip = host

        log.info(f"{self.teamname} initialized.")
        log.info(f"Connecting to server: {self.ip}")

        self.socket = socketio.Client(logger=debug, engineio_logger=debug)
        self.socket.register_namespace(TeamNamespace("/team"))
        self.socket.connect(self.ip, socketio_path="scoreboard.io")
        self.sid = self.socket.get_sid(namespace="/team")

        log.info("Starting game sequence...")
        self._start_game(self.teamname)

    def _start_game(self, teamname: str):
        payload = {"teamname": teamname}
        res = self.socket.call("start_game", payload, namespace="/team")
        log.info(res)

    def add_UID(self, UID_str: str) -> Tuple[int, float]:
        log.debug(f"Submitting UID: {UID_str}")

        if not isinstance(UID_str, str):
            raise ValueError(f"UID format error (expected: str, got: {UID_str})")
        if not re.match(r"^[0-9A-Fa-f]{8}$", UID_str):
            raise ValueError(f"UID format error (expected: 8 hex digits, got: {UID_str})")

        res = self.socket.call("add_UID", UID_str, namespace="/team")
        if not res:
            log.error("Failed to append UID to server.")
            return 0, 0
            
        res = cast(dict, res)
        message = res.get("message", "No message")
        score = res.get("score", 0)
        time_remaining = res.get("time_remaining", 0)
        log.info(message)
        return score, time_remaining

    def get_current_score(self) -> Optional[int]:
        try:
            log.debug(f"{self.ip}/current_score?sid={self.sid}")
            res = requests.get(self.ip + "/current_score", params={"sid": self.sid})
            return res.json()["current_score"]
        except Exception as e:
            log.error(f"Failed to fetch current score: {e}")
            return None

class TeamNamespace(socketio.ClientNamespace):
    def on_connect(self):
        client = cast(socketio.Client, self.client)
        log.info(f"Connected with SID: {client.get_sid(namespace='/team')}")

    def on_UID_added(self, message):
        log.info(message)

    def on_disconnect(self):
        log.info("Disconnected from remote server.")