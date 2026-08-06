#
# @lc app=leetcode id=338 lang=python3
#
# [338] Counting Bits
#
# https://leetcode.com/problems/counting-bits/description/
#
# algorithms
# Easy (80.78%)
# Likes:    12052
# Dislikes: 616
# Total Accepted:    1.7M
# Total Submissions: 2.1M
# Testcase Example:  "2"
#
# Given an integer n, return an array ans of length n + 1 such that for each i
# (0 <= i <= n), ans[i] is the number of 1's in the binary representation of i.
#
# Do not solve it with built-in functions (i.e., like __builtin_popcount in
# C++).
#
# Example 1:
#
# Input: n = 2
# Output: [0,1,1]
# Explanation:
# 0 --> 0
# 1 --> 1
# 2 --> 10
#
# Example 2:
#
# Input: n = 5
# Output: [0,1,1,2,1,2]
# Explanation:
# 0 --> 0
# 1 --> 1
# 2 --> 10
# 3 --> 11
# 4 --> 100
# 5 --> 101
#
# Constraints:
#
# 0 <= n <= 10^5
#
# Follow up:
#
# It is very easy to come up with a solution with a runtime of O(n log n). Can
# you do it in linear time O(n) and possibly in a single pass?
#

# @lc code=start
from typing import List


class Solution:
    def countBits(self, n: int) -> List[int]:
        """
        Interview explanation:
        DP: bits(i) = bits(i >> 1) + (i & 1). Right-shift drops LSB; add whether
        the LSB was set.

        Algorithm:
        - ans[0] = 0; for i in 1..n: ans[i] = ans[i >> 1] + (i & 1).

        Complexity: O(n) time and space.
        """
        ans = [0] * (n + 1)
        for i in range(1, n + 1):
            ans[i] = ans[i >> 1] + (i & 1)
        return ans
# @lc code=end
