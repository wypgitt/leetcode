#
# @lc app=leetcode id=3965 lang=python3
#
# [3965] Finish Time of Tasks I
#
# https://leetcode.com/problems/finish-time-of-tasks-i/description/
#
# algorithms
# Medium (61.86%)
# Likes:    48
# Dislikes: 3
# Total Accepted:    20.2K
# Total Submissions: 32.6K
# Testcase Example:  "3\n[[0,1],[1,2]]\n[9,5,3]"
#
#
# You are given an integer n representing the number of tasks in a
# project, numbered from 0 to n - 1. These tasks are connected as a tree
# rooted at task 0. This is represented by a 2D integer array edges of
# length n - 1, where edges[i] = [u_i, v_i] indicates that task u_i is the
# parent of task v_i.
#
# You are also given an array baseTime of length n, where baseTime[i]
# represents the time to complete task i.
#
# The finish time of each task is calculated as follows:
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
# The finish time of task i is latest + ownDuration.
#
# Return the finish time of the root task 0.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[1,2]], baseTime = [9,5,3]
#
# Output: 17
#
# Explanation:
#
#      0 9  1 5  2 3
#
# Task 2 is a leaf, so its finish time is baseTime[2] = 3.
#
# Task 1 has one child task 2:
#
# earliest = latest = 3
#
# ownDuration = (latest - earliest) + baseTime[1] = 5
#
# Finish time of task 1 is 3 + 5 = 8
#
# Task 0 has one child with finish time 8:
#
# earliest = latest = 8
#
# ownDuration = (latest - earliest) + baseTime[0] = 9
#
# Finish time of task 0 is 8 + 9 = 17
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
# Example 3:
#
# Input: n = 4, edges = [[0,1],[0,2],[2,3]], baseTime = [5,8,2,1]
#
# Output: 18
#
# Explanation:
#
# Task 1 is a leaf, so its finish time is baseTime[1] = 8.
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
# Task 0 has two children with finish times 8 and 3:
#
# earliest = 3, latest = 8
#
# ownDuration = (latest - earliest) + baseTime[0] = (8 - 3) + 5 = 10
#
# Finish time of task 0 is latest + ownDuration = 8 + 10 = 18
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
# The input is generated such that edges represents a valid tree.
#
# baseTime.length == n
#
# 1 <= baseTime[i] <= 10^5​​​​​​​
#
# The finish time of every task is guaranteed to be less than 2^53.
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
        Finish time is defined bottom-up on the rooted tree: a leaf is baseTime,
        and an internal node waits for the latest child then adds
        (latest - earliest) + baseTime.

        Algorithm:
        - Build adjacency from parent to children.
        - DFS: leaf -> baseTime[i]; else 2*latest - earliest + baseTime[i].
        - Return finish time at root 0.

        Complexity: O(n) time, O(n) space.
        """
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)

        def dfs(i: int) -> int:
            if not g[i]:
                return baseTime[i]
            earliest, latest = inf, -inf
            for j in g[i]:
                a = dfs(j)
                earliest = min(earliest, a)
                latest = max(latest, a)
            return latest + (latest - earliest) + baseTime[i]

        return dfs(0)
# @lc code=end
