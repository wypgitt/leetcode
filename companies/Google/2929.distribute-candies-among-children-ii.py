#
# @lc app=leetcode id=2929 lang=python3
#
# [2929] Distribute Candies Among Children II
#
# https://leetcode.com/problems/distribute-candies-among-children-ii/description/
#
# algorithms
# Medium (55.64%)
# Likes:    570
# Dislikes: 176
# Total Accepted:    105.9K
# Total Submissions: 190.4K
# Testcase Example:  "5\n2"
#
#
# You are given two positive integers n and limit.
#
# Return the total number of ways to distribute n candies among 3 children
# such that no child gets more than limit candies.
#
# Example 1:
#
# Input: n = 5, limit = 2
# Output: 3
# Explanation: There are 3 ways to distribute 5 candies such that no child
# gets more than 2 candies: (1, 2, 2), (2, 1, 2) and (2, 2, 1).
#
# Example 2:
#
# Input: n = 3, limit = 3
# Output: 10
# Explanation: There are 10 ways to distribute 3 candies such that no
# child gets more than 3 candies: (0, 0, 3), (0, 1, 2), (0, 2, 1), (0, 3,
# 0), (1, 0, 2), (1, 1, 1), (1, 2, 0), (2, 0, 1), (2, 1, 0) and (3, 0, 0).
#
# Constraints:
#
# 1 <= n <= 10^6
#
# 1 <= limit <= 10^6
#

# @lc code=start

class Solution:
    def distributeCandies(self, n: int, limit: int) -> int:
        """
        Interview explanation:
        Ways to give n candies to 3 children with each <= limit. n can be large,
        so avoid O(n) loops.

        Algorithm:
        - Inclusion-exclusion on stars-and-bars C(n+2,2).

        Complexity: O(1) time, O(1) space.
        """

        def ways(x: int) -> int:
            return (x + 2) * (x + 1) // 2 if x >= 0 else 0

        return (
            ways(n)
            - 3 * ways(n - (limit + 1))
            + 3 * ways(n - 2 * (limit + 1))
            - ways(n - 3 * (limit + 1))
        )
# @lc code=end

