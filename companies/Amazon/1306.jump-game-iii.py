#
# @lc app=leetcode id=1306 lang=python3
#
# [1306] Jump Game III
#
# https://leetcode.com/problems/jump-game-iii/description/
#
# algorithms
# Medium (70.37%)
# Likes:    4583
# Dislikes: 120
# Total Accepted:    401K
# Total Submissions: 570K
# Testcase Example:  "[4,2,3,0,3,1,2]"
#
# Given an array of non-negative integers arr, you are initially positioned at
# start index of the array. When you are at index i, you can jump to i + arr[i]
# or i - arr[i], check if you can reach any index with value 0.
#
# Notice that you can not jump outside of the array at any time.
#
# Example 1:
#
# Input: arr = [4,2,3,0,3,1,2], start = 5
# Output: true
# Explanation:
# All possible ways to reach at index 3 with value 0 are:
# index 5 -> index 4 -> index 1 -> index 3
# index 5 -> index 6 -> index 4 -> index 1 -> index 3
#
# Example 2:
#
# Input: arr = [4,2,3,0,3,1,2], start = 0
# Output: true
# Explanation:
# One possible way to reach at index 3 with value 0 is:
# index 0 -> index 4 -> index 1 -> index 3
#
# Example 3:
#
# Input: arr = [3,0,2,1,2], start = 2
# Output: false
# Explanation: There is no way to reach at index 1 with value 0.
#
# Constraints:
#
# 1 <= arr.length <= 5 * 10^4
#
# 0 <= arr[i] < arr.length
#
# 0 <= start < arr.length
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def canReach(self, arr: List[int], start: int) -> bool:
        """
        Interview explanation:
        From index i jump to i±arr[i]. Ask if any 0 is reachable. Graph BFS
        from start with visited set (cycles possible).

        Algorithm (BFS):
        - Queue start; if arr[i]==0 success; enqueue unvisited in-bound neighbors.

        Complexity: O(n) time, O(n) space.
        """
        n = len(arr)
        q = deque([start])
        seen = {start}
        while q:
            i = q.popleft()
            if arr[i] == 0:
                return True
            for j in (i + arr[i], i - arr[i]):
                if 0 <= j < n and j not in seen:
                    seen.add(j)
                    q.append(j)
        return False

    def canReach_dfs(self, arr: List[int], start: int) -> bool:
        """
        Interview explanation:
        Alternate DFS with visited marking.

        Algorithm:
        - dfs(i): false OOB/visited; true if 0; else mark and try ±arr[i].

        Complexity: O(n) time, O(n) space.
        """
        n = len(arr)
        seen = [False] * n

        def dfs(i: int) -> bool:
            if i < 0 or i >= n or seen[i]:
                return False
            if arr[i] == 0:
                return True
            seen[i] = True
            return dfs(i + arr[i]) or dfs(i - arr[i])

        return dfs(start)
# @lc code=end

