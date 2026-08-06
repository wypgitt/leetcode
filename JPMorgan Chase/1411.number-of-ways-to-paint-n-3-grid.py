#
# @lc app=leetcode id=1411 lang=python3
#
# [1411] Number of Ways to Paint N × 3 Grid
#
# https://leetcode.com/problems/number-of-ways-to-paint-n-3-grid/description/
#
# algorithms
# Hard (80.55%)
# Likes:    1679
# Dislikes: 92
# Total Accepted:    138K
# Total Submissions: 171K
# Testcase Example:  "1"
#
# You have a grid of size n x 3 and you want to paint each cell of the grid
# with exactly one of the three colors: Red, Yellow, or Green while making sure
# that no two adjacent cells have the same color (i.e., no two cells that share
# vertical or horizontal sides have the same color).
#
# Given n the number of rows of the grid, return the number of ways you can
# paint this grid. As the answer may grow large, the answer must be computed
# modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 1
# Output: 12
# Explanation: There are 12 possible way to paint the grid as shown.
#
# Example 2:
#
# Input: n = 5000
# Output: 30228214
#
# Constraints:
#
# n == grid.length
#
# 1 <= n <= 5000
#

# @lc code=start
class Solution:
    def numOfWays(self, n: int) -> int:
        """
        Interview explanation:
        Paint n x 3 grid with 3 colors, adjacent different (incl. vertical).
        Two pattern types for a row: ABA (121-type) and ABC (123-type).
        Count transitions between types; closed-form DP recurrence.

        Algorithm:
        (type DP)
        - a0=6 ABA patterns, b0=6 ABC patterns for first row.
        - a = 3*a_prev + 2*b_prev; b = 2*a_prev + 2*b_prev (mod 10^9+7)
        - Iterate n-1 times; return (a+b)%MOD

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        a = b = 6  # ways ending with ABA / ABC after 1 row
        for _ in range(n - 1):
            a, b = (3 * a + 2 * b) % MOD, (2 * a + 2 * b) % MOD
        return (a + b) % MOD

    def numOfWays_states(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: enumerate all valid 3-color row colorings (27→filter), then
        DP[row][mask] transitioning only between vertically compatible masks.

        Algorithm:
        - Generate valid rows; dp transitions; sum after n rows.

        Complexity: O(n * S^2) with S<=12 valid states, O(S) space.
        """
        MOD = 10**9 + 7
        colors = (0, 1, 2)
        valid = []
        for a in colors:
            for b in colors:
                for c in colors:
                    if a != b and b != c:
                        valid.append((a, b, c))
        S = len(valid)
        compat = [[] for _ in range(S)]
        for i, r1 in enumerate(valid):
            for j, r2 in enumerate(valid):
                if all(r1[k] != r2[k] for k in range(3)):
                    compat[i].append(j)
        dp = [1] * S
        for _ in range(n - 1):
            ndp = [0] * S
            for i in range(S):
                for j in compat[i]:
                    ndp[j] = (ndp[j] + dp[i]) % MOD
            dp = ndp
        return sum(dp) % MOD
# @lc code=end
