"""
Module: node.py
Description: Defines absolute geographical directions and the structural Node 
             class used to construct the maze graph.
"""

from enum import IntEnum

class Direction(IntEnum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

class Node:
    """Represents a discrete intersection in the maze."""
    def __init__(self, index: int = 0):
        self.index = index
        self.successors = [] # Format: (Node, Direction, distance)

    def get_index(self) -> int:
        return self.index

    def get_successors(self) -> list:
        return self.successors

    def set_successor(self, successor, direction: int, length: int = 1):
        """Links this node to an adjacent node."""
        self.successors.append((successor, Direction(direction), int(length)))

    def get_direction(self, node) -> Direction:
        """Returns the relative direction to an adjacent node."""
        for succ_node, direction, length in self.successors:
            if succ_node.index == node.index:
                return direction

        print(f"[Error] Node {node.index} is not adjacent to Node {self.index}")
        return 0

    def is_successor(self, node) -> bool:
        """Checks if a specified node is directly accessible."""
        for succ in self.successors:
            if succ[0] == node:
                return True
        return False