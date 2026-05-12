#
# @lc app=leetcode id=1306 lang=python3
#
# [1306] Jump Game III
#
# https://leetcode.com/problems/jump-game-iii/description/
#
# algorithms
# Medium (66.84%)
# Likes:    4349
# Dislikes: 118
# Total Accepted:    302K
# Total Submissions: 451.6K
# Testcase Example:  '[4,2,3,0,3,1,2]\n5'
#
# Given an array of non-negative integers arr, you are initially positioned at
# start index of the array. When you are at index i, you can jump to i + arr[i]
# or i - arr[i], check if you can reach any index with value 0.
# 
# Notice that you can not jump outside of the array at any time.
# 
# 
# Example 1:
# 
# 
# Input: arr = [4,2,3,0,3,1,2], start = 5
# Output: true
# Explanation: 
# All possible ways to reach at index 3 with value 0 are: 
# index 5 -> index 4 -> index 1 -> index 3 
# index 5 -> index 6 -> index 4 -> index 1 -> index 3 
# 
# 
# Example 2:
# 
# 
# Input: arr = [4,2,3,0,3,1,2], start = 0
# Output: true 
# Explanation: 
# One possible way to reach at index 3 with value 0 is: 
# index 0 -> index 4 -> index 1 -> index 3
# 
# 
# Example 3:
# 
# 
# Input: arr = [3,0,2,1,2], start = 2
# Output: false
# Explanation: There is no way to reach at index 1 with value 0.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 5 * 10^4
# 0 <= arr[i] < arr.length
# 0 <= start < arr.length
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def canReach(self, arr: List[int], start: int) -> bool:
        n = len(arr)
        seen = [False] * n
        stack = [start]

        while stack:
            index = stack.pop()
            if index < 0 or index >= n or seen[index]:
                continue

            if arr[index] == 0:
                return True

            seen[index] = True
            jump = arr[index]
            stack.append(index + jump)
            stack.append(index - jump)

        return False
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Treat each array index as a graph node. From index `i`, there are up to two
# directed edges: `i + arr[i]` and `i - arr[i]`. The question is whether any
# reachable node contains 0, so DFS or BFS is the natural fit.
#
# Data structure:
# `stack` performs iterative DFS. `seen` prevents infinite loops such as
# bouncing between two indices.
#
# Walkthrough:
# 1. Start DFS from `start`.
# 2. Skip out-of-bounds or already visited indices.
# 3. If the current value is 0, we found a valid path.
# 4. Otherwise, mark it visited and push both possible jumps.
#
# Edge cases:
# - `start` already points at 0: returns True immediately.
# - Jumps that leave the array: ignored.
# - Cycles: `seen` guarantees each index is processed once.
#
# Complexity:
# - Time: O(n), each index is visited at most once.
# - Space: O(n), for the visited array and DFS stack.
#
# Tests to discuss:
# - arr = [4,2,3,0,3,1,2], start = 5 -> True.
# - arr = [3,0,2,1,2], start = 2 -> False because the reachable component has
#   no zero.
