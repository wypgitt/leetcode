#
# @lc app=leetcode id=1259 lang=python3
#
# [1259] Handshakes That Don't Cross
#
# https://leetcode.com/problems/handshakes-that-dont-cross/description/
#
# algorithms
# Hard (61.51%)
# Likes:    259
# Dislikes: 17
# Total Accepted:    15.6K
# Total Submissions: 25.4K
# Testcase Example:  "4"
#
#
# You are given an even number of people numPeople that stand around a
# circle and each person shakes hands with someone else so that there are
# numPeople / 2 handshakes total.
#
# Return the number of ways these handshakes could occur such that none of
# the handshakes cross.
#
# Since the answer could be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: numPeople = 4
# Output: 2
# Explanation: There are two ways to do it, the first way is [(1,2),(3,4)]
# and the second one is [(2,3),(4,1)].
#
# Example 2:
#
# Input: numPeople = 6
# Output: 5
#
# Constraints:
#
# 2 <= numPeople <= 1000
#
# numPeople is even.
#
# @lc code=start

class Solution:
    def numberOfWays(self, numPeople: int) -> int:
        """
        Interview explanation:
        Premium. 2n people on a circle; count non-crossing perfect matchings
        = Catalan number C_n. DP: dp[n] = sum dp[i]*dp[n-1-i] for person 0
        shaking with even-distance partners (numPeople even).

        Algorithm:
        - Let n = numPeople/2; MOD=10^9+7.
        - dp[0]=1; for k=1..n: dp[k]=sum_{i=0}^{k-1} dp[i]*dp[k-1-i] % MOD.
        - Return dp[n].

        Complexity: O(n^2) time, O(n) space with n=numPeople/2.
        """
        MOD = 10**9 + 7
        n = numPeople // 2
        dp = [0] * (n + 1)
        dp[0] = 1
        for k in range(1, n + 1):
            s = 0
            for i in range(k):
                s = (s + dp[i] * dp[k - 1 - i]) % MOD
            dp[k] = s
        return dp[n]
# @lc code=end
