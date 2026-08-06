#
# @lc app=leetcode id=1048 lang=python3
#
# [1048] Longest String Chain
#
# https://leetcode.com/problems/longest-string-chain/description/
#
# algorithms
# Medium (63.35%)
# Likes:    7884
# Dislikes: 274
# Total Accepted:    548K
# Total Submissions: 865K
# Testcase Example:  "[\"a\",\"b\",\"ba\",\"bca\",\"bda\",\"bdca\"]"
#
# You are given an array of words where each word consists of lowercase English
# letters.
#
# word_A is a predecessor of word_B if and only if we can insert exactly one
# letter anywhere in word_A without changing the order of the other characters
# to make it equal to word_B.
#
# For example, "abc" is a predecessor of "abac", while "cba" is not a
# predecessor of "bcad".
#
# A word chain is a sequence of words [word_1, word_2, ..., word_k] with k >=
# 1, where word_1 is a predecessor of word_2, word_2 is a predecessor of
# word_3, and so on. A single word is trivially a word chain with k == 1.
#
# Return the length of the longest possible word chain with words chosen from
# the given list of words.
#
# Example 1:
#
# Input: words = ["a","b","ba","bca","bda","bdca"]
# Output: 4
# Explanation: One of the longest word chains is ["a","ba","bda","bdca"].
#
# Example 2:
#
# Input: words = ["xbc","pcxbcf","xb","cxbc","pcxbc"]
# Output: 5
# Explanation: All the words can be put in a word chain ["xb", "xbc", "cxbc",
# "pcxbc", "pcxbcf"].
#
# Example 3:
#
# Input: words = ["abcd","dbqca"]
# Output: 1
# Explanation: The trivial word chain ["abcd"] is one of the longest word
# chains.
# ["abcd","dbqca"] is not a valid word chain because the ordering of the
# letters is changed.
#
# Constraints:
#
# 1 <= words.length <= 1000
#
# 1 <= words[i].length <= 16
#
# words[i] only consists of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def longestStrChain(self, words: List[str]) -> int:
        """
        Interview explanation:
        Word A is predecessor of B if B is A plus one inserted letter. Sort by
        length; DP[word] = 1 + max DP[pred] over all one-letter deletions.

        Algorithm:
        - Sort by len; dp={}
        - For w: best=1; for each delete-one pred in dp: best=max(best,dp[pred]+1)
        - dp[w]=best; track global max

        Complexity: O(N * L^2) time, O(N*L) space.
        """
        words.sort(key=len)
        dp = {}
        best = 1
        for w in words:
            cur = 1
            for i in range(len(w)):
                pred = w[:i] + w[i + 1 :]
                if pred in dp:
                    cur = max(cur, dp[pred] + 1)
            dp[w] = cur
            best = max(best, cur)
        return best

    def longestStrChain_memo(self, words: List[str]) -> int:
        """
        Interview explanation:
        Alternate DFS+memo from each word trying all one-char deletions that
        exist in the word set.

        Algorithm:
        - word set; dfs(w)=1+max dfs(pred) over deletions in set

        Complexity: O(N * L^2) time, O(N) space.
        """
        from functools import lru_cache

        word_set = set(words)

        @lru_cache(None)
        def dfs(w: str) -> int:
            best = 1
            for i in range(len(w)):
                pred = w[:i] + w[i + 1 :]
                if pred in word_set:
                    best = max(best, 1 + dfs(pred))
            return best

        return max(dfs(w) for w in words) if words else 0
# @lc code=end
