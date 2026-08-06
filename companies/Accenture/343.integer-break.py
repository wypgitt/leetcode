#
# @lc app=leetcode id=343 lang=python3
#
# [343] Integer Break
#
# https://leetcode.com/problems/integer-break/description/
#
# algorithms
# Medium (62.59%)
# Likes:    5428
# Dislikes: 467
# Total Accepted:    458K
# Total Submissions: 732K
# Testcase Example:  "2"
#
# Given an integer n, break it into the sum of k positive integers, where k >=
# 2, and maximize the product of those integers.
#
# Return the maximum product you can get.
#
# Example 1:
#
# Input: n = 2
# Output: 1
# Explanation: 2 = 1 + 1, 1 × 1 = 1.
#
# Example 2:
#
# Input: n = 10
# Output: 36
# Explanation: 10 = 3 + 3 + 4, 3 × 3 × 4 = 36.
#
# Constraints:
#
# 2 <= n <= 58
#

# @lc code=start
class Solution:
    def integerBreak(self, n: int) -> int:
        """
        Interview explanation:
        Math: break into as many 3s as possible (optimal real break is e≈2.718).
        Prefer 3; avoid leaving remainder 1 (use 2+2 instead of 3+1). For n < 4
        special-case.

        Algorithm:
        - If n == 2 return 1; n == 3 return 2.
        - While n > 4: multiply by 3, n -= 3; then multiply remaining n.

        Complexity: O(n) time (or O(1) with // and %), O(1) space.
        """
        if n <= 3:
            return n - 1
        product = 1
        while n > 4:
            product *= 3
            n -= 3
        return product * n

    def integerBreak_dp(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: DP where dp[i] = max product breaking i. For j in 1..i-1,
        max(j * (i-j), j * dp[i-j]).

        Algorithm:
        - dp[1]=1; fill up to n; return dp[n].

        Complexity: O(n^2) time, O(n) space.
        """
        dp = [0] * (n + 1)
        dp[1] = 1
        for i in range(2, n + 1):
            for j in range(1, i):
                dp[i] = max(dp[i], j * (i - j), j * dp[i - j])
        return dp[n]
# @lc code=end
