#
# @lc app=leetcode id=3333 lang=python3
#
# [3333] Find the Original Typed String II
#
# https://leetcode.com/problems/find-the-original-typed-string-ii/description/
#
# algorithms
# Hard (45.45%)
# Likes:    506
# Dislikes: 78
# Total Accepted:    70.4K
# Total Submissions: 155K
# Testcase Example:  "\"aabbccdd\"\n7"
#
#
# Alice is attempting to type a specific string on her computer. However,
# she tends to be clumsy and may press a key for too long, resulting in a
# character being typed multiple times.
#
# You are given a string word, which represents the final output displayed
# on Alice's screen. You are also given a positive integer k.
#
# Return the total number of possible original strings that Alice might
# have intended to type, if she was trying to type a string of size at
# least k.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: word = "aabbccdd", k = 7
#
# Output: 5
#
# Explanation:
#
# The possible strings are: "aabbccdd", "aabbccd", "aabbcdd", "aabccdd",
# and "abbccdd".
#
# Example 2:
#
# Input: word = "aabbccdd", k = 8
#
# Output: 1
#
# Explanation:
#
# The only possible string is "aabbccdd".
#
# Example 3:
#
# Input: word = "aaabbb", k = 3
#
# Output: 8
#
# Constraints:
#
# 1 <= word.length <= 5 * 10^5
#
# word consists only of lowercase English letters.
#
# 1 <= k <= 2000
#

# @lc code=start

class Solution:
    def possibleStringCount(self, word: str, k: int) -> int:
        """
        Interview explanation:
        Each run of length L can shrink to any length in 1..L independently.
        Count assignments whose total length is at least k (mod 1e9+7).

        Algorithm:
        - total = product of run lengths.
        - If #runs >= k, every assignment has length >= k; return total.
        - Else DP ways to form length < k: dp[j] = ways to reach length j;
          update with prefix sums over taking 1..L from the next run.
        - Answer = total - sum(dp[0..k-1]).

        Complexity: O(n + k * #runs) time, O(k) space.
        """
        MOD = 10**9 + 7
        groups: list[int] = []
        i, n = 0, len(word)
        while i < n:
            j = i
            while j < n and word[j] == word[i]:
                j += 1
            groups.append(j - i)
            i = j

        total = 1
        for g in groups:
            total = total * g % MOD
        if len(groups) >= k:
            return total

        dp = [0] * k
        dp[0] = 1
        for g in groups:
            prefix = [0] * (k + 1)
            for j in range(k):
                prefix[j + 1] = (prefix[j] + dp[j]) % MOD
            ndp = [0] * k
            for j in range(1, k):
                # take t in [1, g] with j - t >= 0 => sum dp[j-g .. j-1]
                lo = max(0, j - g)
                ndp[j] = (prefix[j] - prefix[lo]) % MOD
            dp = ndp

        return (total - sum(dp) % MOD) % MOD
# @lc code=end

