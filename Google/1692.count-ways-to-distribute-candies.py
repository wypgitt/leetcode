#
# @lc app=leetcode id=1692 lang=python3
#
# [1692] Count Ways to Distribute Candies
#
# https://leetcode.com/problems/count-ways-to-distribute-candies/description/
#
# algorithms
# Hard (64.02%)
# Likes:    78
# Dislikes: 9
# Total Accepted:    3.2K
# Total Submissions: 5K
# Testcase Example:  "3\n2"
#
#
# There are n unique candies (labeled 1 through n) and k bags. You are
# asked to distribute all the candies into the bags such that every bag
# has at least one candy.
#
# There can be multiple ways to distribute the candies. Two ways are
# considered different if the candies in one bag in the first way are not
# all in the same bag in the second way. The order of the bags and the
# order of the candies within each bag do not matter.
#
# For example, (1), (2,3) and (2), (1,3) are considered different because
# candies 2 and 3 in the bag (2,3) in the first way are not in the same
# bag in the second way (they are split between the bags (2) and (1,3)).
# However, (1), (2,3) and (3,2), (1) are considered the same because the
# candies in each bag are all in the same bags in both ways.
#
# Given two integers, n and k, return the number of different ways to
# distribute the candies. As the answer may be too large, return it modulo
# 10^9 + 7.
#
# Example 1:
#
# Input: n = 3, k = 2
# Output: 3
# Explanation: You can distribute 3 candies into 2 bags in 3 ways:
# (1), (2,3)
# (1,2), (3)
# (1,3), (2)
#
# Example 2:
#
# Input: n = 4, k = 2
# Output: 7
# Explanation: You can distribute 4 candies into 2 bags in 7 ways:
# (1), (2,3,4)
# (1,2), (3,4)
# (1,3), (2,4)
# (1,4), (2,3)
# (1,2,3), (4)
# (1,2,4), (3)
# (1,3,4), (2)
#
# Example 3:
#
# Input: n = 20, k = 5
# Output: 206085257
# Explanation: You can distribute 20 candies into 5 bags in 1881780996
# ways. 1881780996 modulo 10^9 + 7 = 206085257.
#
# Constraints:
#
# 1 <= k <= n <= 1000
#
# @lc code=start
class Solution:
    def waysToDistribute(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Premium. Distribute n distinct candies into k identical bags nonempty
        (Stirling numbers of the second kind S(n,k)). DP:
        S(n,k)=k*S(n-1,k)+S(n-1,k-1). Mod 10^9+7.

        Algorithm (DP Stirling 2nd kind):
        - dp[j] = S(i,j) rolling; for i=1..n update j=min(i,k)..1.

        Complexity: O(n*k) time, O(k) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (k + 1)
        dp[0] = 1
        for i in range(1, n + 1):
            ndp = [0] * (k + 1)
            for j in range(1, min(i, k) + 1):
                ndp[j] = (j * dp[j] + dp[j - 1]) % MOD
            dp = ndp
        return dp[k]
# @lc code=end
