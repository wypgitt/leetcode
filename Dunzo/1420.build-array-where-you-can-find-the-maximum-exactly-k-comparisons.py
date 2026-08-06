#
# @lc app=leetcode id=1420 lang=python3
#
# [1420] Build Array Where You Can Find The Maximum Exactly K Comparisons
#
# https://leetcode.com/problems/build-array-where-you-can-find-the-maximum-exactly-k-comparisons/description/
#
# algorithms
# Hard (65.4%)
# Likes:    1498
# Dislikes: 96
# Total Accepted:    74.9K
# Total Submissions: 115K
# Testcase Example:  "2"
#
# You are given three integers n, m and k. Consider the following algorithm to
# find the maximum element of an array of positive integers:
#
# You should build the array arr which has the following properties:
#
# arr has exactly n integers.
#
# 1 <= arr[i] <= m where (0 <= i < n).
#
# After applying the mentioned algorithm to arr, the value search_cost is equal
# to k.
#
# Return the number of ways to build the array arr under the mentioned
# conditions. As the answer may grow large, the answer must be computed modulo
# 10^9 + 7.
#
# Example 1:
#
# Input: n = 2, m = 3, k = 1
# Output: 6
# Explanation: The possible arrays are [1, 1], [2, 1], [2, 2], [3, 1], [3, 2]
# [3, 3]
#
# Example 2:
#
# Input: n = 5, m = 2, k = 3
# Output: 0
# Explanation: There are no possible arrays that satisfy the mentioned
# conditions.
#
# Example 3:
#
# Input: n = 9, m = 1, k = 1
# Output: 1
# Explanation: The only possible array is [1, 1, 1, 1, 1, 1, 1, 1, 1]
#
# Constraints:
#
# 1 <= n <= 50
#
# 1 <= m <= 100
#
# 0 <= k <= n
#

# @lc code=start
from functools import lru_cache


class Solution:
    def numOfArrays(self, n: int, m: int, k: int) -> int:
        """
        Interview explanation:
        Count arrays length n, values in [1,m], search cost (left-to-right maxima
        count) exactly k. DP on (pos, max_so_far, cost_used).

        Algorithm:
        (3D DP)
        - dp[i][maxv][cost]: ways for length i, current max maxv, cost cost.
        - Transition: append x<=maxv (cost same) or x>maxv (cost+1, new max=x).

        Complexity: O(n * m^2 * k) time, O(n*m*k) or rolling O(m*k) space.
        """
        MOD = 10**9 + 7
        # dp[j][c] after processing some length: max=j, cost=c
        dp = [[0] * (k + 1) for _ in range(m + 1)]
        for j in range(1, m + 1):
            dp[j][1] = 1
        for _ in range(2, n + 1):
            ndp = [[0] * (k + 1) for _ in range(m + 1)]
            # prefix sums for fast sum over maxv
            for c in range(1, k + 1):
                pref = 0
                for j in range(1, m + 1):
                    # append <= j: j choices keeping max j
                    ndp[j][c] = (ndp[j][c] + dp[j][c] * j) % MOD
                    # append j when previous max < j → cost+1 from any max < j
                    ndp[j][c] = (ndp[j][c] + pref) % MOD
                    pref = (pref + dp[j][c - 1]) % MOD
            dp = ndp
        return sum(dp[j][k] for j in range(1, m + 1)) % MOD

    def numOfArrays_memo(self, n: int, m: int, k: int) -> int:
        """
        Interview explanation:
        Alternate top-down memo dfs(i, max_so_far, cost).

        Algorithm:
        - dfs(pos, mx, cost): try next value 1..m update mx/cost.

        Complexity: O(n*m*k*m) time, O(n*m*k) space.
        """
        MOD = 10**9 + 7

        @lru_cache(None)
        def dfs(pos: int, mx: int, cost: int) -> int:
            if cost > k:
                return 0
            if pos == n:
                return int(cost == k)
            ans = 0
            for x in range(1, m + 1):
                if x > mx:
                    ans += dfs(pos + 1, x, cost + 1)
                else:
                    ans += dfs(pos + 1, mx, cost)
            return ans % MOD

        return dfs(0, 0, 0)
# @lc code=end
