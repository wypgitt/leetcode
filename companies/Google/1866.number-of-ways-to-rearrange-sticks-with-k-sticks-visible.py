#
# @lc app=leetcode id=1866 lang=python3
#
# [1866] Number of Ways to Rearrange Sticks With K Sticks Visible
#
# https://leetcode.com/problems/number-of-ways-to-rearrange-sticks-with-k-sticks-visible/description/
#
# algorithms
# Hard (62.24%)
# Likes:    780
# Dislikes: 26
# Total Accepted:    25.6K
# Total Submissions: 41.1K
# Testcase Example:  "3"
#
# There are n uniquely-sized sticks whose lengths are integers from 1 to n. You
# want to arrange the sticks such that exactly k sticks are visible from the
# left. A stick is visible from the left if there are no longer sticks to the
# left of it.
#
# For example, if the sticks are arranged [1,3,2,5,4], then the sticks with
# lengths 1, 3, and 5 are visible from the left.
#
# Given n and k, return the number of such arrangements. Since the answer may
# be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 3, k = 2
# Output: 3
# Explanation: [1,3,2], [2,3,1], and [2,1,3] are the only arrangements such
# that exactly 2 sticks are visible.
# The visible sticks are underlined.
#
# Example 2:
#
# Input: n = 5, k = 5
# Output: 1
# Explanation: [1,2,3,4,5] is the only arrangement such that all 5 sticks are
# visible.
# The visible sticks are underlined.
#
# Example 3:
#
# Input: n = 20, k = 11
# Output: 647427950
# Explanation: There are 647427950 (mod 10^9 + 7) ways to rearrange the sticks
# such that exactly 11 sticks are visible.
#
# Constraints:
#
# 1 <= n <= 1000
#
# 1 <= k <= n
#

# @lc code=start
class Solution:
    def rearrangeSticks(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Place sticks 1..n; a stick is visible from left if taller than all to
        its left. Count permutations with exactly k visible. DP: place tallest
        n — either at front (new visible) or hide behind some of n-1 positions.

        Algorithm (DP):
        - dp[i][j] = ways with i sticks, j visible.
        - dp[i][j] = dp[i-1][j-1] + (i-1)*dp[i-1][j]
          (put i at left / put i in one of i-1 non-left slots).

        Complexity: O(n*k) time/space (can roll to O(k) space).
        """
        MOD = 10**9 + 7
        dp = [[0] * (k + 1) for _ in range(n + 1)]
        dp[0][0] = 1
        for i in range(1, n + 1):
            for j in range(1, min(i, k) + 1):
                dp[i][j] = (dp[i - 1][j - 1] + (i - 1) * dp[i - 1][j]) % MOD
        return dp[n][k]

    def rearrangeSticks_rolled(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Alternate: same recurrence with rolling 1D DP array.

        Algorithm:
        - dp[j] ways for current i; update backward/with temp using prior row.

        Complexity: O(n*k) time, O(k) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (k + 1)
        dp[0] = 1
        for i in range(1, n + 1):
            ndp = [0] * (k + 1)
            for j in range(1, min(i, k) + 1):
                ndp[j] = (dp[j - 1] + (i - 1) * dp[j]) % MOD
            dp = ndp
        return dp[k]
# @lc code=end
