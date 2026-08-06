#
# @lc app=leetcode id=2189 lang=python3
#
# [2189] Number of Ways to Build House of Cards
#
# https://leetcode.com/problems/number-of-ways-to-build-house-of-cards/description/
#
# algorithms
# Medium (62.84%)
# Likes:    70
# Dislikes: 18
# Total Accepted:    4K
# Total Submissions: 6.4K
# Testcase Example:  "16"
#
#
# You are given an integer n representing the number of playing cards you
# have. A house of cards meets the following conditions:
#
# A house of cards consists of one or more rows of triangles and
# horizontal cards.
#
# Triangles are created by leaning two cards against each other.
#
# One card must be placed horizontally between all adjacent triangles in a
# row.
#
# Any triangle on a row higher than the first must be placed on a
# horizontal card from the previous row.
#
# Each triangle is placed in the leftmost available spot in the row.
#
# Return the number of distinct house of cards you can build using all n
# cards. Two houses of cards are considered distinct if there exists a row
# where the two houses contain a different number of cards.
#
# Example 1:
#
# Input: n = 16
# Output: 2
# Explanation: The two valid houses of cards are shown.
# The third house of cards in the diagram is not valid because the
# rightmost triangle on the top row is not placed on top of a horizontal
# card.
#
# Example 2:
#
# Input: n = 2
# Output: 1
# Explanation: The one valid house of cards is shown.
#
# Example 3:
#
# Input: n = 4
# Output: 0
# Explanation: The three houses of cards in the diagram are not valid.
# The first house of cards needs a horizontal card placed between the two
# triangles.
# The second house of cards uses 5 cards.
# The third house of cards uses 2 cards.
#
# Constraints:
#
# 1 <= n <= 500
#
# @lc code=start
from functools import cache


class Solution:
    def houseOfCards(self, n: int) -> int:
        """
        Interview explanation:
        Premium. Build houses of cards using exactly n cards. Row with k
        triangles uses 3*k+2 cards (2 per triangle + 1 between adjacent, plus
        base horizontals pattern). Rows must use strictly decreasing triangle
        counts going up... Actually: each row uses 3*t+2 cards for t triangles,
        and we use distinct row sizes as a partition of n into parts of form
        3k+2 (knapsack / choose subset of row sizes).

        Algorithm:
        (DFS memo / knapsack)
        - dfs(remain, k): decide whether to place a row costing 3*k+2.
        - Classic: number of ways to write n as sum of distinct 3k+2 values
          (order of rows fixed by size).

        Complexity: O(n^2) time/space with memo.
        """
        @cache
        def dfs(remain: int, k: int) -> int:
            x = 3 * k + 2
            if x > remain:
                return 0
            if x == remain:
                return 1
            return dfs(remain - x, k + 1) + dfs(remain, k + 1)

        return dfs(n, 0)

    def houseOfCards_dp(self, n: int) -> int:
        """
        Interview explanation:
        Alternate bottom-up knapsack: parts are 2,5,8,...; each used at most once.

        Algorithm:
        - dp[0]=1; for each part, update dp backward.

        Complexity: O(n^2) time, O(n) space.
        """
        dp = [0] * (n + 1)
        dp[0] = 1
        k = 0
        while True:
            part = 3 * k + 2
            if part > n:
                break
            for s in range(n, part - 1, -1):
                dp[s] += dp[s - part]
            k += 1
        return dp[n]
# @lc code=end
