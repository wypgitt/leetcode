#
# @lc app=leetcode id=140 lang=python3
#
# [140] Word Break II
#
# https://leetcode.com/problems/word-break-ii/description/
#
# algorithms
# Hard (55.96%)
# Likes:    7614
# Dislikes: 551
# Total Accepted:    838K
# Total Submissions: 1.5M
# Testcase Example:  "\"catsanddog\""
#
# Given a string s and a dictionary of strings wordDict, add spaces in s to
# construct a sentence where each word is a valid dictionary word. Return all
# such possible sentences in any order.
#
# Note that the same word in the dictionary may be reused multiple times in the
# segmentation.
#
# Example 1:
#
# Input: s = "catsanddog", wordDict = ["cat","cats","and","sand","dog"]
# Output: ["cats and dog","cat sand dog"]
#
# Example 2:
#
# Input: s = "pineapplepenapple", wordDict =
# ["apple","pen","applepen","pine","pineapple"]
# Output: ["pine apple pen apple","pineapple pen apple","pine applepen apple"]
# Explanation: Note that you are allowed to reuse a dictionary word.
#
# Example 3:
#
# Input: s = "catsandog", wordDict = ["cats","dog","sand","and","cat"]
# Output: []
#
# Constraints:
#
# 1 <= s.length <= 20
#
# 1 <= wordDict.length <= 1000
#
# 1 <= wordDict[i].length <= 10
#
# s and wordDict[i] consist of only lowercase English letters.
#
# All the strings of wordDict are unique.
#
# Input is generated in a way that the length of the answer doesn't exceed
# 10^5.
#

# @lc code=start
from typing import Dict, List, Set


class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> List[str]:
        """
        Interview explanation:
        Backtracking with memoization over start index: from each position try
        every dictionary word that matches the prefix, and cache the list of
        sentence suffixes that can complete the rest of the string.

        Algorithm:
        - Store wordDict in a set; optionally bound by max word length.
        - dfs(i) returns all ways to break s[i:].
        - For each word w, if s.startswith(w, i), prepend w to each dfs(i+|w|).
        - Memoize dfs(i); base case i == n yields [""] then join with spaces.

        Complexity: O(n * W * L + R) where W is dict size, L max word length,
        R total output size; O(n + R) memo/output space.
        """
        words: Set[str] = set(wordDict)
        max_len = max((len(w) for w in words), default=0)
        n = len(s)
        memo: Dict[int, List[str]] = {}

        def dfs(i: int) -> List[str]:
            if i == n:
                return [""]
            if i in memo:
                return memo[i]
            sentences: List[str] = []
            for j in range(i + 1, min(n, i + max_len) + 1):
                word = s[i:j]
                if word in words:
                    for suffix in dfs(j):
                        sentences.append(word if not suffix else f"{word} {suffix}")
            memo[i] = sentences
            return sentences

        return dfs(0)

    def wordBreak_dp(self, s: str, wordDict: List[str]) -> List[str]:
        """
        Interview explanation:
        Alternate: bottom-up DP where dp[i] stores all sentences for s[:i].

        Algorithm:
        - dp[0] = [""].
        - For each end j, for each start i < j, if s[i:j] in dict, append
          combinations from dp[i].
        - Return dp[n].

        Complexity: O(n^2 + R) time dominated by concatenations / output; O(R) space.
        """
        words: Set[str] = set(wordDict)
        n = len(s)
        dp: List[List[str]] = [[] for _ in range(n + 1)]
        dp[0] = [""]
        for j in range(1, n + 1):
            for i in range(j):
                word = s[i:j]
                if word in words and dp[i]:
                    for prev in dp[i]:
                        dp[j].append(word if not prev else f"{prev} {word}")
        return dp[n]
# @lc code=end
