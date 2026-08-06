#
# @lc app=leetcode id=903 lang=python3
#
# [903] Valid Permutations for DI Sequence
#
# https://leetcode.com/problems/valid-permutations-for-di-sequence/description/
#
# algorithms
# Hard (56.57%)
# Likes:    755
# Dislikes: 46
# Total Accepted:    21.7K
# Total Submissions: 38.3K
# Testcase Example:  "\"DID\""
#
# You are given a string s of length n where s[i] is either:
#
# 'D' means decreasing, or
#
# 'I' means increasing.
#
# A permutation perm of n + 1 integers of all the integers in the range [0, n]
# is called a valid permutation if for all valid i:
#
# If s[i] == 'D', then perm[i] > perm[i + 1], and
#
# If s[i] == 'I', then perm[i] < perm[i + 1].
#
# Return the number of valid permutations perm. Since the answer may be large,
# return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "DID"
# Output: 5
# Explanation: The 5 valid permutations of (0, 1, 2, 3) are:
# (1, 0, 3, 2)
# (2, 0, 3, 1)
# (2, 1, 3, 0)
# (3, 0, 2, 1)
# (3, 1, 2, 0)
#
# Example 2:
#
# Input: s = "D"
# Output: 1
#
# Constraints:
#
# n == s.length
#
# 1 <= n <= 200
#
# s[i] is either 'I' or 'D'.
#

# @lc code=start
class Solution:
    def numPermsDISequence(self, s: str) -> int:
        """
        Interview explanation:
        Count perms of 0..n matching DI string. DP: dp[i][j] = ways using i+1
        numbers ending with rank j among them (relative).

        Algorithm (DP):
        - dp[0][0]=1. For each instruction:
          - 'D': new[j] = sum old[k] for k>=j (prefix from right)
          - 'I': new[j] = sum old[k] for k<j
        - Or rolling with cumulative sums.

        Complexity: O(n^2) time/space, n=len(s).
        """
        MOD = 10**9 + 7
        n = len(s)
        dp = [1]
        for i, ch in enumerate(s):
            ndp = [0] * (i + 2)
            if ch == "I":
                acc = 0
                for j in range(i + 1):
                    acc = (acc + dp[j]) % MOD
                    ndp[j + 1] = acc
            else:  # 'D'
                acc = 0
                for j in range(i, -1, -1):
                    acc = (acc + dp[j]) % MOD
                    ndp[j] = acc
            dp = ndp
        return sum(dp) % MOD
# @lc code=end

