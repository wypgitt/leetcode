#
# @lc app=leetcode id=3857 lang=python3
#
# [3857] Minimum Cost to Split into Ones
#
# https://leetcode.com/problems/minimum-cost-to-split-into-ones/description/
#
# algorithms
# Medium (82.55%)
# Likes:    72
# Dislikes: 9
# Total Accepted:    52.7K
# Total Submissions: 63.9K
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
# Return an integer denoting the minimum total cost required to split the
# integer n into n ones.
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
# 1 <= n <= 500
#

# @lc code=start
class Solution:
    def minCost(self, n: int) -> int:
        """
        Interview explanation:
        Splitting x→(a,b) costs a*b. Any full reduction of n into ones has the
        same total cost: the triangular number n(n-1)/2.

        Algorithm:
        - Identity: cost(x)=a*b+cost(a)+cost(b) with a+b=x collapses to x(x-1)/2.
        - Return n * (n - 1) // 2.

        Complexity: O(1) time, O(1) space.
        """
        return n * (n - 1) // 2
# @lc code=end
