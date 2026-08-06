#
# @lc app=leetcode id=1931 lang=python3
#
# [1931] Painting a Grid With Three Different Colors
#
# https://leetcode.com/problems/painting-a-grid-with-three-different-colors/description/
#
# algorithms
# Hard (76.94%)
# Likes:    946
# Dislikes: 58
# Total Accepted:    77.0K
# Total Submissions: 100K
# Testcase Example:  "1"
#
# You are given two integers m and n. Consider an m x n grid where each cell is
# initially white. You can paint each cell red, green, or blue. All cells must
# be painted.
#
# Return the number of ways to color the grid with no two adjacent cells having
# the same color. Since the answer can be very large, return it modulo 10^9 +
# 7.
#
# Example 1:
#
# Input: m = 1, n = 1
# Output: 3
# Explanation: The three possible colorings are shown in the image above.
#
# Example 2:
#
# Input: m = 1, n = 2
# Output: 6
# Explanation: The six possible colorings are shown in the image above.
#
# Example 3:
#
# Input: m = 5, n = 5
# Output: 580986
#
# Constraints:
#
# 1 <= m <= 5
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def colorTheGrid(self, m: int, n: int) -> int:
        """
        Interview explanation:
        Color m×n grid with 3 colors; adjacent cells (4-dir) different. m≤5 so
        column states are 3^m masks; DP between compatible consecutive columns.

        Algorithm:
        - Enumerate valid column colorings (no vertical equal neighbors).
          Transition if no horizontal conflict; DP[col][state] sum mod 1e9+7.

        Complexity: O(n * S^2) with S≤3^m ≤ 243, O(S) space.
        """
        MOD = 10**9 + 7
        colors = [0, 1, 2]

        def gen(pos, prev, cur, out):
            if pos == m:
                out.append(cur[:])
                return
            for c in colors:
                if c != prev:
                    cur.append(c)
                    gen(pos + 1, c, cur, out)
                    cur.pop()

        states = []
        gen(0, -1, [], states)
        S = len(states)
        compat = [[] for _ in range(S)]
        for i, a in enumerate(states):
            for j, b in enumerate(states):
                if all(a[k] != b[k] for k in range(m)):
                    compat[i].append(j)
        dp = [1] * S
        for _ in range(n - 1):
            ndp = [0] * S
            for i in range(S):
                if dp[i]:
                    for j in compat[i]:
                        ndp[j] = (ndp[j] + dp[i]) % MOD
            dp = ndp
        return sum(dp) % MOD
# @lc code=end
