#
# @lc app=leetcode id=2767 lang=python3
#
# [2767] Partition String Into Minimum Beautiful Substrings
#
# https://leetcode.com/problems/partition-string-into-minimum-beautiful-substrings/description/
#
# algorithms
# Medium (53.92%)
# Likes:    387
# Dislikes: 19
# Total Accepted:    23.3K
# Total Submissions: 43.2K
# Testcase Example:  "\"1011\""
#
# Given a binary string s, partition the string into one or more substrings such
# that each substring is beautiful.
#
# A string is beautiful if:
#
#
# It doesn't contain leading zeros.
#
#
# It's the binary representation of a number that is a power of 5.
#
# Return the minimum number of substrings in such partition. If it is impossible
# to partition the string s into beautiful substrings, return -1.
#
# A substring is a contiguous sequence of characters in a string.
#
#
#
# Example 1:
#
# Input: s = "1011"
# Output: 2
# Explanation: We can paritition the given string into ["101", "1"].
# - The string "101" does not contain leading zeros and is the binary
# representation of integer 5^1 = 5.
# - The string "1" does not contain leading zeros and is the binary
# representation of integer 5^0 = 1.
# It can be shown that 2 is the minimum number of beautiful substrings that s
# can be partitioned into.
#
# Example 2:
#
# Input: s = "111"
# Output: 3
# Explanation: We can paritition the given string into ["1", "1", "1"].
# - The string "1" does not contain leading zeros and is the binary
# representation of integer 5^0 = 1.
# It can be shown that 3 is the minimum number of beautiful substrings that s
# can be partitioned into.
#
# Example 3:
#
# Input: s = "0"
# Output: -1
# Explanation: We can not partition the given string into beautiful substrings.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 15
#
#
# s[i] is either '0' or '1'.
#

# @lc code=start
from functools import cache
from math import inf
from typing import List


class Solution:
    def minimumBeautifulSubstrings(self, s: str) -> int:
        """
        Interview explanation:
        Partition binary string into minimum substrings that are binary of 5^k
        without leading zeros. Return -1 if impossible.

        Algorithm:
        - Precompute powers of 5 fitting in s; DP/DFS over start index.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(s)
        x = 1
        ss = {x}
        for _ in range(n):
            x *= 5
            ss.add(x)

        @cache
        def dfs(i: int) -> int:
            if i >= n:
                return 0
            if s[i] == "0":
                return inf
            val = 0
            ans = inf
            for j in range(i, n):
                val = (val << 1) | (ord(s[j]) - 48)
                if val in ss:
                    ans = min(ans, 1 + dfs(j + 1))
            return ans

        ans = dfs(0)
        return -1 if ans == inf else ans

    def minimumBeautifulSubstrings_dp(self, s: str) -> int:
        """
        Interview explanation:
        Alternate bottom-up DP for beautiful partition count.

        Algorithm:
        - dp[i] = min pieces for s[i:]; try ends j with s[i:j+1] a power of 5.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(s)
        powers = set()
        x = 1
        while x.bit_length() <= n:
            powers.add(x)
            x *= 5
        dp = [inf] * (n + 1)
        dp[n] = 0
        for i in range(n - 1, -1, -1):
            if s[i] == "0":
                continue
            val = 0
            for j in range(i, n):
                val = (val << 1) | (ord(s[j]) - 48)
                if val in powers:
                    dp[i] = min(dp[i], 1 + dp[j + 1])
        return -1 if dp[0] == inf else dp[0]
# @lc code=end
