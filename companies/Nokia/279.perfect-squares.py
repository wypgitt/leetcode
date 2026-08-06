#
# @lc app=leetcode id=279 lang=python3
#
# [279] Perfect Squares
#
# https://leetcode.com/problems/perfect-squares/description/
#
# algorithms
# Medium (56.77%)
# Likes:    11951
# Dislikes: 493
# Total Accepted:    1.1M
# Total Submissions: 1.9M
# Testcase Example:  "12"
#
# Given an integer n, return the least number of perfect square numbers that
# sum to n.
#
# A perfect square is an integer that is the square of an integer; in other
# words, it is the product of some integer with itself. For example, 1, 4, 9,
# and 16 are perfect squares while 3 and 11 are not.
#
# Example 1:
#
# Input: n = 12
# Output: 3
# Explanation: 12 = 4 + 4 + 4.
#
# Example 2:
#
# Input: n = 13
# Output: 2
# Explanation: 13 = 4 + 9.
#
# Constraints:
#
# 1 <= n <= 10^4
#

# @lc code=start
from collections import deque
from math import isqrt


class Solution:
    def numSquares(self, n: int) -> int:
        """
        Interview explanation:
        Least number of perfect squares summing to n — unbounded knapsack /
        coin change with coin set {1,4,9,...,k^2}.

        Algorithm (DP — primary):
        - dp[x] = min squares summing to x; dp[0] = 0.
        - For each square s, update dp[x] = min(dp[x], dp[x-s] + 1).

        Complexity: O(n * sqrt(n)) time, O(n) space.
        """
        dp = [0] + [float("inf")] * n
        squares = [i * i for i in range(1, isqrt(n) + 1)]
        for x in range(1, n + 1):
            best = dp[x]
            for s in squares:
                if s > x:
                    break
                best = min(best, dp[x - s] + 1)
            dp[x] = best
        return int(dp[n])

    def numSquaresBFS(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: BFS from 0; each edge adds one perfect square. First time we
        reach n is the minimum count (unweighted shortest path).

        Complexity: O(n * sqrt(n)) worst case, O(n) space.
        """
        squares = [i * i for i in range(1, isqrt(n) + 1)]
        q = deque([0])
        seen = {0}
        steps = 0
        while q:
            for _ in range(len(q)):
                cur = q.popleft()
                if cur == n:
                    return steps
                for s in squares:
                    nxt = cur + s
                    if nxt == n:
                        return steps + 1
                    if nxt > n or nxt in seen:
                        continue
                    seen.add(nxt)
                    q.append(nxt)
            steps += 1
        return steps
# @lc code=end

