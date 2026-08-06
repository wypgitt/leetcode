#
# @lc app=leetcode id=887 lang=python3
#
# [887] Super Egg Drop
#
# https://leetcode.com/problems/super-egg-drop/description/
#
# algorithms
# Hard (30.7%)
# Likes:    3858
# Dislikes: 210
# Total Accepted:    106K
# Total Submissions: 344K
# Testcase Example:  "1"
#
# You are given k identical eggs and you have access to a building with n
# floors labeled from 1 to n.
#
# You know that there exists a floor f where 0 <= f <= n such that any egg
# dropped at a floor higher than f will break, and any egg dropped at or below
# floor f will not break.
#
# Each move, you may take an unbroken egg and drop it from any floor x (where 1
# <= x <= n). If the egg breaks, you can no longer use it. However, if the egg
# does not break, you may reuse it in future moves.
#
# Return the minimum number of moves that you need to determine with certainty
# what the value of f is.
#
# Example 1:
#
# Input: k = 1, n = 2
# Output: 2
# Explanation:
# Drop the egg from floor 1. If it breaks, we know that f = 0.
# Otherwise, drop the egg from floor 2. If it breaks, we know that f = 1.
# If it does not break, then we know f = 2.
# Hence, we need at minimum 2 moves to determine with certainty what the value
# of f is.
#
# Example 2:
#
# Input: k = 2, n = 6
# Output: 3
#
# Example 3:
#
# Input: k = 3, n = 14
# Output: 4
#
# Constraints:
#
# 1 <= k <= 100
#
# 1 <= n <= 10^4
#

# @lc code=start
class Solution:
    def superEggDrop(self, k: int, n: int) -> int:
        """
        Interview explanation:
        Minimize worst-case drops. Optimized DP: with m moves and k eggs,
        max floors coverable is sum C(m,i) for i=1..k. Find min m with
        coverage >= n (or DP with binary search per egg/floor).

        Algorithm (DP optimized — moves/eggs coverage):
        - dp[m][e] = 1 + dp[m-1][e-1] + dp[m-1][e] (break / survive).
        - Increase m until dp[m][k] >= n.

        Complexity: O(k * moves) ~ O(k log n / log ...) up to O(k*n) worst; O(k) space rolling.
        """
        # dp[e] = max floors with current moves and e eggs
        dp = [0] * (k + 1)
        moves = 0
        while dp[k] < n:
            moves += 1
            for e in range(k, 0, -1):
                dp[e] = dp[e] + dp[e - 1] + 1
        return moves

    def superEggDrop_binary_search_dp(self, k: int, n: int) -> int:
        """
        Interview explanation:
        Alternate classic: dp[eggs][moves] via binary search on drop floor for
        each state; or memo(K,N) with binary search on x to balance break/survive.

        Algorithm:
        - memo(k,n): binary search x in 1..n minimizing max(memo(k-1,x-1),
          memo(k,n-x))+1.

        Complexity: O(k * n * log n) time with memo, O(k*n) space.
        """
        from functools import lru_cache

        @lru_cache(None)
        def dp(eggs: int, floors: int) -> int:
            if floors <= 1 or eggs == 1:
                return floors
            lo, hi = 1, floors
            best = floors
            while lo <= hi:
                mid = (lo + hi) // 2
                broken = dp(eggs - 1, mid - 1)
                survived = dp(eggs, floors - mid)
                best = min(best, 1 + max(broken, survived))
                if broken < survived:
                    lo = mid + 1
                else:
                    hi = mid - 1
            return best

        return dp(k, n)
# @lc code=end

