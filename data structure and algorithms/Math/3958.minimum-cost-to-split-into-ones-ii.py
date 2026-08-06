#
# @lc app=leetcode id=3958 lang=python3
#
# [3958] Minimum Cost to Split into Ones II
#
# https://leetcode.com/problems/minimum-cost-to-split-into-ones-ii/description/
#
# algorithms
# Medium (68.36%)
# Likes:    3
# Dislikes: 1
# Total Accepted:    296
# Total Submissions: 433
# Testcase Example:  "3"
#
#
# You are given an integer n.
#
# In one operation, you may split an integer x into two positive integers
# a and b such that a + b = x.
#
# The cost of this operation is a * b.
#
# Return the minimum total cost required to split the integer n into n
# ones.
#
# Example 1:
#
# Input: n = 3
#
# Output: 3
#
# Explanation:
#
# One optimal set of operations is:
#
#                         x
#                         a
#                         b
#                         a + b
#                         a * b
#                         Cost
#
#                         3
#                         1
#                         2
#                         3
#                         2
#                         2
#
#                         2
#                         1
#                         1
#                         2
#                         1
#                         1
#
# Thus, the minimum total cost is 2 + 1 = 3.
#
# Example 2:
#
# Input: n = 4
#
# Output: 6
#
# Explanation:​​​​​​​
#
# One optimal set of operations is:
#
#                         x
#                         a
#                         b
#                         a + b
#                         a * b
#                         Cost
#
#                         4
#                         2
#                         2
#                         4
#                         4
#                         4
#
#                         2
#                         1
#                         1
#                         2
#                         1
#                         1
#
# Thus, the minimum total cost is 4 + 1 + 1 = 6.
#
# Constraints:
#
# 1 <= n <= 5 * 10^7
#

# @lc code=start
class Solution:
    def minCost(self, n: int) -> int:
        """
        Interview explanation:
        Splitting x→a+b costs a·b; any full split of n into ones totals
        1+2+…+(n-1) regardless of order (each pair of ones contributes 1).

        Algorithm:
        - Return n*(n-1)//2.

        Complexity: O(1).
        """
        return n * (n - 1) // 2

    def minCost_loop(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: accumulate 1..(n-1) explicitly.

        Algorithm:
        - sum(range(n)).

        Complexity: O(n) time, O(1) space.
        """
        return sum(range(n))
# @lc code=end
