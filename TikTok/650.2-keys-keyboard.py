#
# @lc app=leetcode id=650 lang=python3
#
# [650] 2 Keys Keyboard
#
# https://leetcode.com/problems/2-keys-keyboard/description/
#
# algorithms
# Medium (59.44%)
# Likes:    4451
# Dislikes: 247
# Total Accepted:    303K
# Total Submissions: 510K
# Testcase Example:  "3"
#
# There is only one character 'A' on the screen of a notepad. You can perform
# one of two operations on this notepad for each step:
#
# Copy All: You can copy all the characters present on the screen (a partial
# copy is not allowed).
#
# Paste: You can paste the characters which are copied last time.
#
# Given an integer n, return the minimum number of operations to get the
# character 'A' exactly n times on the screen.
#
# Example 1:
#
# Input: n = 3
# Output: 3
# Explanation: Initially, we have one character 'A'.
# In step 1, we use Copy All operation.
# In step 2, we use Paste operation to get 'AA'.
# In step 3, we use Paste operation to get 'AAA'.
#
# Example 2:
#
# Input: n = 1
# Output: 0
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start

class Solution:
    def minSteps(self, n: int) -> int:
        """
        Interview explanation:
        Start with one 'A'. Operations: Copy All / Paste. Min ops to get n 'A's
        equals sum of prime factors of n (factorization DP/math).

        Algorithm:
        - Factor n from 2..sqrt: while n % d == 0: ans += d; n //= d.
        - If n > 1: ans += n.

        Complexity: O(sqrt(n)) time, O(1) space.
        """
        ans = 0
        d = 2
        while d * d <= n:
            while n % d == 0:
                ans += d
                n //= d
            d += 1
        if n > 1:
            ans += n
        return ans

    def minSteps_dp(self, n: int) -> int:
        """
        Interview explanation:
        Alternate classic DP: dp[i] = min ops for i chars; for factor j of i,
        dp[i] = min(dp[j] + i//j) (copy once then paste).

        Algorithm:
        - dp[i] = i initially; for each factor j of i update with dp[j]+i//j.

        Complexity: O(n sqrt n) or O(n^2), O(n) space.
        """
        dp = [0] * (n + 1)
        for i in range(2, n + 1):
            dp[i] = i
            j = 2
            while j * j <= i:
                if i % j == 0:
                    dp[i] = min(dp[i], dp[j] + i // j, dp[i // j] + j)
                j += 1
        return dp[n]
# @lc code=end
