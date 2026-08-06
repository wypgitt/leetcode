#
# @lc app=leetcode id=598 lang=python3
#
# [598] Range Addition II
#
# https://leetcode.com/problems/range-addition-ii/description/
#
# algorithms
# Easy (59.07%)
# Likes:    1047
# Dislikes: 987
# Total Accepted:    139K
# Total Submissions: 236K
# Testcase Example:  "3"
#
# You are given an m x n matrix M initialized with all 0's and an array of
# operations ops, where ops[i] = [a_i, b_i] means M[x][y] should be incremented
# by one for all 0 <= x < a_i and 0 <= y < b_i.
#
# Count and return the number of maximum integers in the matrix after
# performing all the operations.
#
# Example 1:
#
# Input: m = 3, n = 3, ops = [[2,2],[3,3]]
# Output: 4
# Explanation: The maximum integer in M is 2, and there are four of it in M. So
# return 4.
#
# Example 2:
#
# Input: m = 3, n = 3, ops =
# [[2,2],[3,3],[3,3],[3,3],[2,2],[3,3],[3,3],[3,3],[2,2],[3,3],[3,3],[3,3]]
# Output: 4
#
# Example 3:
#
# Input: m = 3, n = 3, ops = []
# Output: 9
#
# Constraints:
#
# 1 <= m, n <= 4 * 10^4
#
# 0 <= ops.length <= 10^4
#
# ops[i].length == 2
#
# 1 <= a_i <= m
#
# 1 <= b_i <= n
#


# @lc code=start
from typing import List
class Solution:
    def maxCount(self, m: int, n: int, ops: List[List[int]]) -> int:
        """
        Interview explanation:
        Every op increments a prefix rectangle [0..a)×[0..b). The maximum
        value cells are exactly the intersection of all ops — a min(a)×min(b)
        rectangle. If ops is empty, the whole m×n matrix stays 0 (all max).

        Algorithm:
        - min_r = min of all op[0] (or m if no ops).
        - min_c = min of all op[1] (or n if no ops).
        - Return min_r * min_c.

        Complexity: O(len(ops)) time, O(1) space.
        """
        if not ops:
            return m * n
        min_r = m
        min_c = n
        for a, b in ops:
            min_r = min(min_r, a)
            min_c = min(min_c, b)
        return min_r * min_c
# @lc code=end

