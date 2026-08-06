#
# @lc app=leetcode id=2928 lang=python3
#
# [2928] Distribute Candies Among Children I
#
# https://leetcode.com/problems/distribute-candies-among-children-i/description/
#
# algorithms
# Easy (76.72%)
# Likes:    157
# Dislikes: 75
# Total Accepted:    44.3K
# Total Submissions: 57.8K
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
# 1 <= n <= 50
#
# 1 <= limit <= 50
#

# @lc code=start

class Solution:
    def distributeCandies(self, n: int, limit: int) -> int:
        """
        Interview explanation:
        Count non-negative triples (a,b,c) with a+b+c=n and each <= limit.
        Small constraints allow enumeration or the closed inclusion-exclusion form.

        Algorithm:
        - O(1) inclusion-exclusion: ways(x)=C(x+2,2) for x>=0 else 0; subtract
          cases where one/two/three kids get at least limit+1.

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

    def distributeCandies_brute(self, n: int, limit: int) -> int:
        """
        Interview explanation:
        Alternate: triple loop over feasible a,b (c determined).

        Algorithm:
        - For a,b in [0,limit], count if 0 <= n-a-b <= limit.

        Complexity: O(limit^2) time, O(1) space.
        """
        ans = 0
        for a in range(limit + 1):
            for b in range(limit + 1):
                c = n - a - b
                if 0 <= c <= limit:
                    ans += 1
        return ans
# @lc code=end

