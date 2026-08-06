#
# @lc app=leetcode id=629 lang=python3
#
# [629] K Inverse Pairs Array
#
# https://leetcode.com/problems/k-inverse-pairs-array/description/
#
# algorithms
# Hard (49.0%)
# Likes:    2794
# Dislikes: 332
# Total Accepted:    143K
# Total Submissions: 291K
# Testcase Example:  "3"
#
# For an integer array nums, an inverse pair is a pair of integers [i, j] where
# 0 <= i < j < nums.length and nums[i] > nums[j].
#
# Given two integers n and k, return the number of different arrays consisting
# of numbers from 1 to n such that there are exactly k inverse pairs. Since the
# answer can be huge, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 3, k = 0
# Output: 1
# Explanation: Only the array [1,2,3] which consists of numbers from 1 to 3 has
# exactly 0 inverse pairs.
#
# Example 2:
#
# Input: n = 3, k = 1
# Output: 2
# Explanation: The array [1,3,2] and [2,1,3] have exactly 1 inverse pair.
#
# Constraints:
#
# 1 <= n <= 1000
#
# 0 <= k <= 1000
#

# @lc code=start

class Solution:
    def kInversePairs(self, n: int, k: int) -> int:
        """
        Interview explanation:
        DP: dp[i][j] = #perms of 1..i with exactly j inverse pairs. Place i into
        a perm of 1..i-1: inserting i at position that creates t new inversions
        (0..i-1) gives transition dp[i][j] += dp[i-1][j-t].

        Algorithm:
        - Use prefix sums for O(1) range: dp[i][j] = sum(dp[i-1][j-i+1..j]).
        - Roll two 1D arrays; MOD = 10^9+7.

        Complexity: O(n*k) time, O(k) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (k + 1)
        dp[0] = 1
        for i in range(1, n + 1):
            ndp = [0] * (k + 1)
            prefix = 0
            for j in range(k + 1):
                prefix = (prefix + dp[j]) % MOD
                if j >= i:
                    prefix = (prefix - dp[j - i]) % MOD
                ndp[j] = prefix
            dp = ndp
        return dp[k]
# @lc code=end
