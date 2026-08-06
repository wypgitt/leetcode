#
# @lc app=leetcode id=3792 lang=python3
#
# [3792] Sum of Increasing Product Blocks
#
# https://leetcode.com/problems/sum-of-increasing-product-blocks/description/
#
# algorithms
# Medium (67.68%)
# Likes:    4
# Dislikes: 1
# Total Accepted:    580
# Total Submissions: 857
# Testcase Example:  "3"
#
#
# You are given an integer n.
#
# A sequence is formed as follows:
#
# The 1^st block contains 1.
#
# The 2^nd block contains 2 * 3.
#
# The i^th block is the product of the next i consecutive integers.
#
# Let F(n) be the sum of the first n blocks.
#
# Return an integer denoting F(n) modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 3
#
# Output: 127
#
# Explanation:​​​​​​​
#
# Block 1: 1
#
# Block 2: 2 * 3 = 6
#
# Block 3: 4 * 5 * 6 = 120
#
# F(3) = 1 + 6 + 120 = 127
#
# Example 2:
#
# Input: n = 7
#
# Output: 6997165
#
# Explanation:
#
# Block 1: 1
#
# Block 2: 2 * 3 = 6
#
# Block 3: 4 * 5 * 6 = 120
#
# Block 4: 7 * 8 * 9 * 10 = 5040
#
# Block 5: 11 * 12 * 13 * 14 * 15 = 360360
#
# Block 6: 16 * 17 * 18 * 19 * 20 * 21 = 39070080
#
# Block 7: 22 * 23 * 24 * 25 * 26 * 27 * 28 = 5967561600
#
# F(7) = 6006997207 % (10^9 + 7) = 6997165
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def sumOfBlocks(self, n: int) -> int:
        """
        Interview explanation:
        Block i is the product of the next i consecutive integers after the prior
        blocks. Sum the first n block products modulo 10^9+7.

        Algorithm:
        - Start cursor k=1; for i=1..n multiply j=k..k+i-1 into x (mod), add to ans.
        - Advance k += i after each block.

        Complexity: O(n^2) time, O(1) space.
        """
        MOD = 10**9 + 7
        ans = 0
        k = 1
        for i in range(1, n + 1):
            x = 1
            for j in range(k, k + i):
                x = x * j % MOD
            ans = (ans + x) % MOD
            k += i
        return ans
# @lc code=end
