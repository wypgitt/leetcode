#
# @lc app=leetcode id=3339 lang=python3
#
# [3339] Find the Number of K-Even Arrays
#
# https://leetcode.com/problems/find-the-number-of-k-even-arrays/description/
#
# algorithms
# Medium (61.21%)
# Likes:    7
# Dislikes: 3
# Total Accepted:    666
# Total Submissions: 1.1K
# Testcase Example:  "3\n4\n2"
#
#
# You are given three integers n, m, and k.
#
# An array arr is called k-even if there are exactly k indices such that,
# for each of these indices i (0 <= i < n - 1):
#
# (arr[i] * arr[i + 1]) - arr[i] - arr[i + 1] is even.
#
# Return the number of possible k-even arrays of size n where all elements
# are in the range [1, m].
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 3, m = 4, k = 2
#
# Output: 8
#
# Explanation:
#
# The 8 possible 2-even arrays are:
#
# [2, 2, 2]
#
# [2, 2, 4]
#
# [2, 4, 2]
#
# [2, 4, 4]
#
# [4, 2, 2]
#
# [4, 2, 4]
#
# [4, 4, 2]
#
# [4, 4, 4]
#
# Example 2:
#
# Input: n = 5, m = 1, k = 0
#
# Output: 1
#
# Explanation:
#
# The only 0-even array is [1, 1, 1, 1, 1].
#
# Example 3:
#
# Input: n = 7, m = 7, k = 5
#
# Output: 5832
#
# Constraints:
#
# 1 <= n <= 750
#
# 0 <= k <= n - 1
#
# 1 <= m <= 1000
#

# @lc code=start

class Solution:
    def countOfArrays(self, n: int, m: int, k: int) -> int:
        """
        Interview explanation:
        (a*b - a - b) is even iff both a and b are even. So count length-n
        arrays over [1,m] with exactly k adjacent even-even pairs.

        Algorithm:
        - even = m//2, odd = m - even.
        - dp[j][0/1]: ways with j even-pairs so far, ending even/odd.
        - Append even: from odd (j stays) or even (j-1); append odd: j stays.

        Complexity: O(n k) time, O(k) space.
        """
        MOD = 10**9 + 7
        even = m // 2
        odd = m - even
        # dp[j][0]=even end, dp[j][1]=odd end
        dp = [[0, 0] for _ in range(k + 1)]
        dp[0][0] = even % MOD
        dp[0][1] = odd % MOD
        for _ in range(1, n):
            ndp = [[0, 0] for _ in range(k + 1)]
            for j in range(k + 1):
                # end with even
                ways = dp[j][1]
                if j > 0:
                    ways = (ways + dp[j - 1][0]) % MOD
                ndp[j][0] = ways * even % MOD
                # end with odd
                ndp[j][1] = (dp[j][0] + dp[j][1]) * odd % MOD
            dp = ndp
        return (dp[k][0] + dp[k][1]) % MOD
# @lc code=end

