#
# @lc app=leetcode id=3902 lang=python3
#
# [3902] Zigzag Level Sum of Binary Tree
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given the root of a binary tree.
#
# Traverse the tree level by level.
#
# For each level:
#   - odd-numbered levels, 1-indexed, are processed left to right
#   - even-numbered levels are processed right to left
#
# While processing nodes in that direction, stop immediately before the first
# node that violates the level rule:
#
#   odd level:  stop before the first node that does not have a left child
#   even level: stop before the first node that does not have a right child
#
# Only nodes processed before the stop contribute to that level's sum.
#
# Return the list of level sums.
#
#
# Important interpretation
# The stopping rule affects only the sum for the current level.
#
# It should NOT stop the BFS from discovering the next level. Even if a node is
# not included in the level sum because processing stopped, its children still
# exist in the tree and must be part of the next level.
#
# Example 1:
#   root = [5,2,8,1,null,9,6]
#
# Level 1, left to right:
#   process 5 -> sum 5
#
# Level 2, right to left:
#   order is [8, 2]
#   process 8, then stop before 2 because 2 has no right child
#   sum 8
#
# Level 3 still contains [1, 9, 6].
#   left-to-right order starts at 1
#   1 has no left child, so sum 0
#
# Answer: [5, 8, 0]
#
#
# Algorithm: BFS by levels
# Use a queue/list for the current level.
#
# For each level:
#   1. Build next_level from all children of all nodes in the current level.
#      This is independent of the stopping rule.
#
#   2. Determine processing order:
#        odd level:  current_level
#        even level: reversed(current_level)
#
#   3. Walk nodes in that order:
#        if the node violates the child condition, break
#        otherwise add node.val to the level sum
#
#   4. Append the sum.
#   5. Move to next_level.
#
#
# Why BFS?
# The task is explicitly level-based. BFS naturally gives all nodes at the same
# depth together.
#
# DFS could also collect nodes by depth, but BFS is simpler and avoids recursion
# depth issues for a tree with up to 1e5 nodes.
#
#
# Data structure choice
# We use lists:
#   current_level: nodes at the current depth
#   next_level: nodes at the next depth
#
# A deque is not necessary because we process entire levels at a time.
#
# This keeps the code direct:
#   iterate current_level once to collect children,
#   iterate current_level or reversed(current_level) once to compute the sum.
#
#
# Walkthrough of the code
# 1. If root is None, return [].
#    The constraints say at least one node, but this keeps the method robust.
#
# 2. Start:
#      level = 1
#      current = [root]
#
# 3. While current is not empty:
#      - collect next_level children
#      - choose order based on level parity
#      - sum nodes until the first violation
#      - append sum
#      - current = next_level
#      - level += 1
#
#
# Correctness proof
#
# Lemma 1: At the start of each loop, current contains exactly the nodes at the
# current tree level from left to right.
# Proof:
# Initially current = [root], which is level 1. During each loop, next_level is
# built by appending each node's left child then right child while scanning the
# current level left to right. This is exactly the left-to-right order of the
# next level. Induction proves the claim.
#
# Lemma 2: The algorithm uses the correct processing order for each level.
# Proof:
# By Lemma 1, current is left-to-right. On odd levels the algorithm uses current
# directly. On even levels it uses reversed(current), which is right-to-left.
#
# Lemma 3: The computed sum for each level includes exactly the nodes required
# by the statement.
# Proof:
# The algorithm scans nodes in the correct order from Lemma 2. Before adding a
# node, it checks the level's required child condition. If the condition fails,
# it stops immediately before that node. Otherwise it adds the node's value.
# This exactly matches the processing rule.
#
# Lemma 4: The stopping rule does not affect future levels in the algorithm.
# Proof:
# The algorithm collects all children into next_level before, and independently
# from, the summing break condition. Therefore all tree nodes remain available
# for later levels, as required.
#
# Theorem: The algorithm returns the correct zigzag level sums.
# Proof:
# By Lemma 1, every loop corresponds to one tree level. By Lemma 3, the appended
# sum for that level is correct. By Lemma 4, future levels are not accidentally
# lost. Therefore the returned list contains exactly the required sums for all
# levels.
#
#
# Complexity analysis
#
# Let N be the number of nodes.
#
# Time:
#   Each node appears in exactly one current_level and has its children inspected
#   once. It may also be checked once for the level sum.
#   Overall time complexity: O(N).
#
# Space:
#   current_level and next_level together can hold O(W) nodes, where W is the
#   maximum tree width. In the worst case W = O(N).
#   Overall space complexity: O(N).
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      [5,2,8,1,null,9,6] -> [5,8,0]
#
# 2. Example 2:
#      [1,2,3,4,5,null,7] -> [1,5,0]
#
# 3. Single node:
#      The root has no left child, so level 1 sum is 0.
#      This follows the statement literally for odd levels.
#
# 4. Complete binary tree:
#      No early stop until the last level, where leaves violate the child
#      condition and contribute 0.
#
# 5. Skewed tree:
#      Verifies level collection and alternating directions.
#
#
# Edge cases
#
# - root can be None defensively, though constraints give at least one node.
# - Node values can be negative, so sums can be negative.
# - A level can contribute 0 either because values sum to 0 or because processing
#   stops before any node.
#
#
# Possible improvements
#
# - A deque could process directions by popping from different ends, but we still
#   need complete level storage for child collection, so lists are simpler.
# - DFS grouped by depth is possible but recursion depth can be risky at 1e5
#   nodes.
#
# -------------------------------------------------------------------------------

# @lc code=start
from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def zigzagLevelSum(self, root: Optional["TreeNode"]) -> list[int]:
        if root is None:
            return []

        answer = []
        current = [root]
        level = 1

        while current:
            next_level = []
            for node in current:
                if node.left:
                    next_level.append(node.left)
                if node.right:
                    next_level.append(node.right)

            level_sum = 0
            nodes = current if level % 2 == 1 else reversed(current)

            for node in nodes:
                if level % 2 == 1:
                    if node.left is None:
                        break
                else:
                    if node.right is None:
                        break
                level_sum += node.val

            answer.append(level_sum)
            current = next_level
            level += 1

        return answer


# @lc code=end
