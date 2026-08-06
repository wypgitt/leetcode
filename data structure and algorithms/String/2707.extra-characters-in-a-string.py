#
# @lc app=leetcode id=2707 lang=python3
#
# [2707] Extra Characters in a String
#
# https://leetcode.com/problems/extra-characters-in-a-string/description/
#
# algorithms
# Medium (57.20%)
# Likes:    2655
# Dislikes: 139
# Total Accepted:    202.7K
# Total Submissions: 354.3K
# Testcase Example:  "\"leetscode\"\n[\"leet\",\"code\",\"leetcode\"]"
#
# You are given a 0-indexed string s and a dictionary of words dictionary. You
# have to break s into one or more non-overlapping substrings such that each
# substring is present in dictionary. There may be some extra characters in s
# which are not present in any of the substrings.
#
# Return the minimum number of extra characters left over if you break up s
# optimally.
#
#
#
# Example 1:
#
# Input: s = "leetscode", dictionary = ["leet","code","leetcode"]
# Output: 1
# Explanation: We can break s in two substrings: "leet" from index 0 to 3 and
# "code" from index 5 to 8. There is only 1 unused character (at index 4), so we
# return 1.
#
# Example 2:
#
# Input: s = "sayhelloworld", dictionary = ["hello","world"]
# Output: 3
# Explanation: We can break s in two substrings: "hello" from index 3 to 7 and
# "world" from index 8 to 12. The characters at indices 0, 1, 2 are not used in
# any substring and thus are considered as extra characters. Hence, we return 3.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 50
#
#
# 1 <= dictionary.length <= 50
#
#
# 1 <= dictionary[i].length <= 50
#
#
# dictionary[i] and s consists of only lowercase English letters
#
#
# dictionary contains distinct words
#

# @lc code=start
from functools import cache
from typing import List


class Solution:
    def minExtraChar(self, s: str, dictionary: List[str]) -> int:
        """
        Interview explanation:
        Partition s into dictionary words (non-overlapping); minimize leftover unmatched chars.

        Algorithm:
        - DP: dp(i) = min leftover for s[i:]. Try skip s[i] (+1) or match any dict word at i.

        Complexity: O(n^2 * |dict|) worst / O(n * Σ|w|) with trie; O(n) space.
        """
        words = set(dictionary)
        n = len(s)

        @cache
        def dp(i: int) -> int:
            if i == n:
                return 0
            best = 1 + dp(i + 1)
            for j in range(i + 1, n + 1):
                if s[i:j] in words:
                    best = min(best, dp(j))
            return best

        return dp(0)

    def minExtraChar_dp(self, s: str, dictionary: List[str]) -> int:
        """
        Interview explanation:
        Bottom-up DP alternate: process suffixes left-to-right.

        Algorithm:
        - dp[i] min leftover for s[i:]; same transitions as memoized DFS.

        Complexity: O(n^2 * |dict| check via set) time, O(n) space.
        """
        words = set(dictionary)
        n = len(s)
        dp = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            dp[i] = 1 + dp[i + 1]
            for j in range(i + 1, n + 1):
                if s[i:j] in words:
                    dp[i] = min(dp[i], dp[j])
        return dp[0]
# @lc code=end
