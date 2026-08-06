#
# @lc app=leetcode id=2912 lang=python3
#
# [2912] Number of Ways to Reach Destination in the Grid
#
# https://leetcode.com/problems/number-of-ways-to-reach-destination-in-the-grid/description/
#
# algorithms
# Hard (57.61%)
# Likes:    19
# Dislikes: 5
# Total Accepted:    1.2K
# Total Submissions: 2.1K
# Testcase Example:  "3\n2\n2\n[1,1]\n[2,2]"
#
#
# You are given two integers n and m which represent the size of a
# 1-indexed grid. You are also given an integer k, a 1-indexed integer
# array source and a 1-indexed integer array dest, where source and dest
# are in the form [x, y] representing a cell on the given grid.
#
# You can move through the grid in the following way:
#
# You can go from cell [x_1, y_1] to cell [x_2, y_2] if either x_1 == x_2
# or y_1 == y_2.
#
# Note that you can't move to the cell you are already in e.g. x_1 == x_2
# and y_1 == y_2.
#
# Return the number of ways you can reach dest from source by moving
# through the grid exactly k times.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 3, m = 2, k = 2, source = [1,1], dest = [2,2]
# Output: 2
# Explanation: There are 2 possible sequences of reaching [2,2] from
# [1,1]:
# - [1,1] -> [1,2] -> [2,2]
# - [1,1] -> [2,1] -> [2,2]
#
# Example 2:
#
# Input: n = 3, m = 4, k = 3, source = [1,2], dest = [2,3]
# Output: 9
# Explanation: There are 9 possible sequences of reaching [2,3] from
# [1,2]:
# - [1,2] -> [1,1] -> [1,3] -> [2,3]
# - [1,2] -> [1,1] -> [2,1] -> [2,3]
# - [1,2] -> [1,3] -> [3,3] -> [2,3]
# - [1,2] -> [1,4] -> [1,3] -> [2,3]
# - [1,2] -> [1,4] -> [2,4] -> [2,3]
# - [1,2] -> [2,2] -> [2,1] -> [2,3]
# - [1,2] -> [2,2] -> [2,4] -> [2,3]
# - [1,2] -> [3,2] -> [2,2] -> [2,3]
# - [1,2] -> [3,2] -> [3,3] -> [2,3]
#
# Constraints:
#
# 2 <= n, m <= 10^9
#
# 1 <= k <= 10^5
#
# source.length == dest.length == 2
#
# 1 <= source[1], dest[1] <= n
#
# 1 <= source[2], dest[2] <= m
#
# @lc code=start
from typing import List


class Solution:
    def numberOfWays(
        self, n: int, m: int, k: int, source: List[int], dest: List[int]
    ) -> int:
        """
        Interview explanation:
        Premium. 1-indexed n x m grid; from a cell move to any other cell in
        the same row or column. Count ways from source to dest in exactly k
        moves, mod 10^9+7.

        Algorithm:
        - Collapse positions into 4 states relative to dest: at dest; same
          row; same col; elsewhere. Transition each move in O(1); run k steps.
        - Start from source's state; answer is ways in "at dest" after k moves.

        Complexity: O(k) time, O(1) space.
        """
        MOD = 10**9 + 7
        # a=at dest, b=same col (diff row), c=same row (diff col), d=other
        # Note: doocs uses a,b,c,d with transitions from dest-centric view
        # starting as if at dest, then pick by (source vs dest).
        a, b, c, d = 1, 0, 0, 0
        for _ in range(k):
            aa = ((n - 1) * b + (m - 1) * c) % MOD
            bb = (a + (n - 2) * b + (m - 1) * d) % MOD
            cc = (a + (m - 2) * c + (n - 1) * d) % MOD
            dd = (b + c + (n - 2) * d + (m - 2) * d) % MOD
            a, b, c, d = aa, bb, cc, dd
        if source[0] == dest[0]:
            return a if source[1] == dest[1] else c
        return b if source[1] == dest[1] else d
# @lc code=end
