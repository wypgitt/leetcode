#
# @lc app=leetcode id=1065 lang=python3
#
# [1065] Index Pairs of a String
#
# https://leetcode.com/problems/index-pairs-of-a-string/description/
#
# algorithms
# Easy (68.72%)
# Likes:    385
# Dislikes: 109
# Total Accepted:    31.6K
# Total Submissions: 46K
# Testcase Example:  "\"thestoryofleetcodeandme\"\n[\"story\",\"fleet\",\"leetcode\"]"
#
#
# Given a string text and an array of strings words, return an array of
# all index pairs [i, j] so that the substring text[i...j] is in words.
#
# Return the pairs [i, j] in sorted order (i.e., sort them by their first
# coordinate, and in case of ties sort them by their second coordinate).
#
# Example 1:
#
# Input: text = "thestoryofleetcodeandme", words =
# ["story","fleet","leetcode"]
# Output: [[3,7],[9,13],[10,17]]
#
# Example 2:
#
# Input: text = "ababa", words = ["aba","ab"]
# Output: [[0,1],[0,2],[2,3],[2,4]]
# Explanation: Notice that matches can overlap, see "aba" is found in
# [0,2] and [2,4].
#
# Constraints:
#
# 1 <= text.length <= 100
#
# 1 <= words.length <= 20
#
# 1 <= words[i].length <= 50
#
# text and words[i] consist of lowercase English letters.
#
# All the strings of words are unique.
#
# @lc code=start
from typing import List


class Solution:
    def indexPairs(self, text: str, words: List[str]) -> List[List[int]]:
        """
        Interview explanation:
        Premium. Find all [i,j] such that text[i:j+1] is in words. Put words in
        a set; for each start i try each word length / each end j.

        Algorithm:
        - word_set; for i: for w in words: if text.startswith(w,i): add [i,i+len-1]
        - Sort pairs by i then j

        Complexity: O(n * W * L) or O(n^2) with all substrings, O(|words|) space.
        """
        word_set = set(words)
        n = len(text)
        ans = []
        # also try by lengths for efficiency
        lengths = sorted({len(w) for w in word_set})
        for i in range(n):
            for L in lengths:
                j = i + L - 1
                if j >= n:
                    break
                if text[i : j + 1] in word_set:
                    ans.append([i, j])
        ans.sort()
        return ans

    def indexPairs_trie(self, text: str, words: List[str]) -> List[List[int]]:
        """
        Interview explanation:
        Alternate trie of words; from each start walk trie and record ends.

        Algorithm:
        - Build trie; for each i walk until miss; record end markers

        Complexity: O(total word chars + n * maxLen) time.
        """
        trie = {}
        for w in words:
            node = trie
            for ch in w:
                node = node.setdefault(ch, {})
            node["#"] = True
        n = len(text)
        ans = []
        for i in range(n):
            node = trie
            for j in range(i, n):
                if text[j] not in node:
                    break
                node = node[text[j]]
                if "#" in node:
                    ans.append([i, j])
        return ans
# @lc code=end
