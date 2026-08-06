#
# @lc app=leetcode id=3967 lang=python3
#
# [3967] Finish Time of Tasks II
#
# https://leetcode.com/problems/finish-time-of-tasks-ii/description/
#
# algorithms
# Hard (23.20%)
# Likes:    4
# Dislikes: 1
# Total Accepted:    197
# Total Submissions: 849
# Testcase Example:  "3\n[[0,1],[1,2]]\n[9,1,5]"
#
#
# You are given an integer n representing the number of tasks in a
# project, numbered from 0 to n - 1. These tasks are connected as an
# undirected tree. This is represented by a 2D integer array edges of
# length n - 1, where edges[i] = [u_i, v_i] indicates an undirected
# connection between task u_i and task v_i.
#
# You are also given an array baseTime of length n, where baseTime[i]
# represents the time to complete task i.
#
# For any chosen task as the root, the finish time of each task is
# calculated as follows:
#
# Leaf task: The finish time is baseTime[i].
#
# Non-leaf task:
#
# Let earliest be the minimum finish time among its children, and latest
# be the maximum finish time among its children.
#
# Let ownDuration be (latest - earliest) + baseTime[i].
#
# Finish time of task i is latest + ownDuration.
#
# Choose any task as the root and compute the finish time of that root
# based on the rules above.
#
# Return the minimum possible finish time among all choices of root.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[1,2]], baseTime = [9,1,5]
#
# Output: 14
#
# Explanation:
#
#      0 9  1 1  2 5
#
# The optimal choice is to treat task 1 as the root.
#
# Task 0 is a leaf, so its finish time is baseTime[0] = 9.
#
# Task 2 is a leaf, so its finish time is baseTime[2] = 5.
#
# Task 1 has two children with finish times 9 and 5:
#
# earliest = 5, latest = 9
#
# ownDuration = (latest - earliest) + baseTime[1] = (9 - 5) + 1 = 5
#
# Finish time of task 1 is latest + ownDuration = 9 + 5 = 14
#
# Thus, the minimum possible finish time among all choices of root is 14.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[0,2]], baseTime = [4,7,6]
#
# Output: 12
#
# Explanation:
#
#      0 4  1 7  2 6
#
# The optimal choice is to treat task 0 as the root.
#
# Task 1 is a leaf, so its finish time is baseTime[1] = 7.
#
# Task 2 is a leaf, so its finish time is baseTime[2] = 6.
#
# Task 0 has two children with finish times 7 and 6:
#
# earliest = 6, latest = 7
#
# ownDuration = (latest - earliest) + baseTime[0] = (7 - 6) + 4 = 5
#
# Finish time of task 0 is latest + ownDuration = 7 + 5 = 12
#
# Thus, the minimum possible finish time among all choices of root is 12.
#
# Example 3:
#
# Input: n = 4, edges = [[0,1],[0,2],[2,3]], baseTime = [5,8,2,1]
#
# Output: 16
#
# Explanation:
#
#       0 5  1 8  2 2  3 1
#
# The optimal choice is to treat task 1 as the root.
#
# Task 3 is a leaf, so its finish time is baseTime[3] = 1.
#
# Task 2 has one child task 3:
#
# earliest = latest = 1
#
# ownDuration = (latest - earliest) + baseTime[2] = 0 + 2 = 2
#
# Finish time of task 2 is latest + ownDuration = 1 + 2 = 3
#
# Task 0 has one child task 2:
#
# earliest = latest = 3
#
# ownDuration = (latest - earliest) + baseTime[0] = 0 + 5 = 5
#
# Finish time of task 0 is latest + ownDuration = 3 + 5 = 8
#
# Task 1 has one child task 0:
#
# earliest = latest = 8
#
# ownDuration = (latest - earliest) + baseTime[1] = 0 + 8 = 8
#
# Finish time of task 1 is latest + ownDuration = 8 + 8 = 16
#
# Thus, the minimum possible finish time among all choices of root is 16.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# edges.length = n - 1
#
# edges[i] == [u_i, v_i]
#
# 0 <= u_i, v_i <= n - 1
#
# u_i != v_i
#
# The input is generated such that edges represents a valid undirected
# tree.
#
# baseTime.length == n
#
# 1 <= baseTime[i] <= 10^5
#

# @lc code=start

import sys
from math import inf
from typing import List

sys.setrecursionlimit(200000)


class Solution:
    def finishTime(self, n: int, edges: List[List[int]], baseTime: List[int]) -> int:
        """
        Interview explanation:
        Same finish-time recurrence as Tasks I, but the root may be any node.
        Rerooting reuses downward finishes and an "up" finish from the parent side.

        Algorithm:
        - finish = baseTime for a leaf; else 2*max(children) - min(children) + baseTime.
        - DFS1: compute downward finish for every subtree from root 0.
        - DFS2: at each node combine neighbor finishes (down / up), track the min
          root finish; push the exclude-child "up" value when moving to a child.

        Complexity: O(n) time, O(n) space.
        """
        if n == 1:
            return baseTime[0]

        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)

        def combine(child_finishes: List[int], node: int) -> int:
            if not child_finishes:
                return baseTime[node]
            earliest = min(child_finishes)
            latest = max(child_finishes)
            return latest + (latest - earliest) + baseTime[node]

        down = [0] * n

        def dfs1(u: int, p: int) -> None:
            childs = []
            for v in g[u]:
                if v == p:
                    continue
                dfs1(v, u)
                childs.append(down[v])
            down[u] = combine(childs, u)

        dfs1(0, -1)
        ans = inf

        def dfs2(u: int, p: int, up) -> None:
            nonlocal ans
            vals = []
            child_finishes = []
            for v in g[u]:
                if v == p:
                    if up is not None:
                        vals.append((v, up))
                        child_finishes.append(up)
                else:
                    vals.append((v, down[v]))
                    child_finishes.append(down[v])
            ans = min(ans, combine(child_finishes, u))
            for v, _ in vals:
                if v == p:
                    continue
                others = [f for w, f in vals if w != v]
                dfs2(v, u, combine(others, u))

        dfs2(0, -1, None)
        return ans
# @lc code=end
