#
# @lc app=leetcode id=133 lang=python3
#
# [133] Clone Graph
#
# https://leetcode.com/problems/clone-graph/description/
#
# algorithms
# Medium (65.22%)
# Likes:    10622
# Dislikes: 4204
# Total Accepted:    1.9M
# Total Submissions: 2.9M
# Testcase Example:  '[[2,4],[1,3],[2,4],[1,3]]'
#
# Given a reference of a node in a connected undirected graph.
# 
# Return a deep copy (clone) of the graph.
# 
# Each node in the graph contains a value (int) and a list (List[Node]) of its
# neighbors.
# 
# 
# class Node {
# ⁠   public int val;
# ⁠   public List<Node> neighbors;
# }
# 
# 
# 
# 
# Test case format:
# 
# For simplicity, each node's value is the same as the node's index
# (1-indexed). For example, the first node with val == 1, the second node with
# val == 2, and so on. The graph is represented in the test case using an
# adjacency list.
# 
# An adjacency list is a collection of unordered lists used to represent a
# finite graph. Each list describes the set of neighbors of a node in the
# graph.
# 
# The given node will always be the first node with val = 1. You must return
# the copy of the given node as a reference to the cloned graph.
# 
# 
# Example 1:
# 
# 
# Input: adjList = [[2,4],[1,3],[2,4],[1,3]]
# Output: [[2,4],[1,3],[2,4],[1,3]]
# Explanation: There are 4 nodes in the graph.
# 1st node (val = 1)'s neighbors are 2nd node (val = 2) and 4th node (val = 4).
# 2nd node (val = 2)'s neighbors are 1st node (val = 1) and 3rd node (val = 3).
# 3rd node (val = 3)'s neighbors are 2nd node (val = 2) and 4th node (val = 4).
# 4th node (val = 4)'s neighbors are 1st node (val = 1) and 3rd node (val =
# 3).
# 
# 
# Example 2:
# 
# 
# Input: adjList = [[]]
# Output: [[]]
# Explanation: Note that the input contains one empty list. The graph consists
# of only one node with val = 1 and it does not have any neighbors.
# 
# 
# Example 3:
# 
# 
# Input: adjList = []
# Output: []
# Explanation: This an empty graph, it does not have any nodes.
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the graph is in the range [0, 100].
# 1 <= Node.val <= 100
# Node.val is unique for each node.
# There are no repeated edges and no self-loops in the graph.
# The Graph is connected and all nodes can be visited starting from the given
# node.
# 
# 
#

"""
Optimal approach: graph traversal + hash map.

We are given a reference to one node in a connected undirected graph, and we
must return a deep copy of the entire graph.

Key observation:
    A graph can contain cycles. If we simply recurse through neighbors and
    create a new node every time we see an original node, we can loop forever
    or create duplicate copies of the same graph node.

Data structure:
    Use a dictionary:

        original node -> cloned node

    This dictionary has two jobs:
        1. It tells us whether an original node has already been cloned.
        2. It gives us the exact clone to reuse when another node points to it.

Algorithm:
    1. If the input node is None, return None.
    2. Run DFS from the given node.
    3. When DFS visits an original node for the first time:
        - Create its cloned node with the same value.
        - Store original -> clone in the dictionary immediately.
    4. Recursively clone each neighbor.
    5. Append each cloned neighbor into the current cloned node's neighbors.
    6. Return the clone corresponding to the starting node.

Why storing the clone immediately matters:
    In a cycle like 1 -- 2 -- 1, node 1's clone must be available before we
    finish cloning all of node 1's neighbors. Otherwise, when DFS reaches node 1
    again through node 2, it would not know that node 1 is already being cloned.

Correctness:
    Every reachable original node gets exactly one cloned node because the hash
    map creates a clone only the first time a node is seen. Every edge is copied
    because for each original node, we iterate through all of its neighbors and
    append the corresponding cloned neighbor. Since the graph is connected from
    the input node, DFS reaches the whole graph.

Complexity:
    Let V be the number of nodes and E be the number of undirected edges.

    Time:  O(V + E)
        We clone each node once and inspect every neighbor reference once. In an
        undirected adjacency list, each edge appears twice, but that is still
        O(E).

    Space: O(V)
        The dictionary stores one entry per node. The DFS recursion stack can
        also be O(V) in the worst case. The cloned graph itself is output space,
        so it is not counted as auxiliary space.
"""

# @lc code=start
"""
# Definition for a Node.
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []
"""

from typing import Optional


class Solution:
    def cloneGraph(self, node: Optional['Node']) -> Optional['Node']:
        if not node:
            return None

        clones = {}

        def dfs(current: 'Node') -> 'Node':
            if current in clones:
                return clones[current]

            clone = Node(current.val)
            clones[current] = clone

            for neighbor in current.neighbors:
                clone.neighbors.append(dfs(neighbor))

            return clone

        return dfs(node)
# @lc code=end
