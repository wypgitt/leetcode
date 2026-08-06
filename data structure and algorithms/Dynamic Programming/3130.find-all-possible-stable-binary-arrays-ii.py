#
# @lc app=leetcode id=3130 lang=python3
#
# [3130] Find All Possible Stable Binary Arrays II
#
# https://leetcode.com/problems/find-all-possible-stable-binary-arrays-ii/description/
#
# algorithms
# Hard (58.50%)
# Likes:    267
# Dislikes: 30
# Total Accepted:    68.6K
# Total Submissions: 117.3K
# Testcase Example:  "1\n1\n2"
#
#
# You are given 3 positive integers num_zeros, num_ones, and limit.
#
# A binary array arr is called stable if:
#
# The number of occurrences of 0 in arr is exactly num_zeros.
#
# The number of occurrences of 1 in arr is exactly num_ones.
#
# Each subarray of arr with a size greater than limit must contain at
# least one occurrence of both 0 and 1.
#
# Return an integer denoting the total number of stable binary arrays.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: zero = 1, one = 1, limit = 2
#
# Output: 2
#
# Explanation:
#
# The two possible stable binary arrays are [1,0] and [0,1].
#
# Example 2:
#
# Input: zero = 1, one = 2, limit = 1
#
# Output: 1
#
# Explanation:
#
# The only possible stable binary array is [1,0,1].
#
# Example 3:
#
# Input: zero = 3, one = 3, limit = 2
#
# Output: 14
#
# Explanation:
#
# All the possible stable binary arrays are [0,0,1,0,1,1], [0,0,1,1,0,1],
# [0,1,0,0,1,1], [0,1,0,1,0,1], [0,1,0,1,1,0], [0,1,1,0,0,1],
# [0,1,1,0,1,0], [1,0,0,1,0,1], [1,0,0,1,1,0], [1,0,1,0,0,1],
# [1,0,1,0,1,0], [1,0,1,1,0,0], [1,1,0,0,1,0], and [1,1,0,1,0,0].
#
# Constraints:
#
# 1 <= zero, one, limit <= 1000
#

# @lc code=start
class Solution:
    def numberOfStableArrays(self, zero: int, one: int, limit: int) -> int:
        """
        Interview explanation:
        Same as Stable Binary Arrays I with larger bounds (up to 1000): count
        arrays with exact zero/one counts and no run longer than limit.

        Algorithm:
        - Identical O(zero*one) DP with run-length subtraction on append:
          dp[i][j][b] ways ending in bit b; subtract illegal long runs via
          dp[i-limit-1][...] / dp[...][j-limit-1].

        Complexity: O(zero*one) time and space.
        """
        MOD = 10**9 + 7
        dp = [[[0, 0] for _ in range(one + 1)] for _ in range(zero + 1)]
        for i in range(1, min(zero, limit) + 1):
            dp[i][0][0] = 1
        for j in range(1, min(one, limit) + 1):
            dp[0][j][1] = 1
        for i in range(1, zero + 1):
            for j in range(1, one + 1):
                dp[i][j][0] = (dp[i - 1][j][0] + dp[i - 1][j][1]) % MOD
                if i > limit:
                    dp[i][j][0] = (dp[i][j][0] - dp[i - limit - 1][j][1]) % MOD
                dp[i][j][1] = (dp[i][j - 1][0] + dp[i][j - 1][1]) % MOD
                if j > limit:
                    dp[i][j][1] = (dp[i][j][1] - dp[i][j - limit - 1][0]) % MOD
        return (dp[zero][one][0] + dp[zero][one][1]) % MOD
# @lc code=end
