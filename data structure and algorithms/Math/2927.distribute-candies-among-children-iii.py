#
# @lc app=leetcode id=2927 lang=python3
#
# [2927] Distribute Candies Among Children III
#
# https://leetcode.com/problems/distribute-candies-among-children-iii/description/
#
# algorithms
# Hard (57.18%)
# Likes:    25
# Dislikes: 7
# Total Accepted:    3.1K
# Total Submissions: 5.4K
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
# 1 <= n <= 10^8
#
# 1 <= limit <= 10^8
#
# @lc code=start

class Solution:
    def distributeCandies(self, n: int, limit: int) -> int:
        """
        Interview explanation:
        Premium: ways to split n identical candies among 3 kids with each getting
        at most limit. Same as II but n, limit up to 1e8 — need O(1) math.

        Algorithm:
        - Stars-and-bars C(n+2,2) with inclusion-exclusion for kids exceeding limit.

        Complexity: O(1) time, O(1) space.
        """

        def ways(x: int) -> int:
            # non-neg solutions to a+b+c = x
            return (x + 2) * (x + 1) // 2 if x >= 0 else 0

        return (
            ways(n)
            - 3 * ways(n - (limit + 1))
            + 3 * ways(n - 2 * (limit + 1))
            - ways(n - 3 * (limit + 1))
        )
# @lc code=end

