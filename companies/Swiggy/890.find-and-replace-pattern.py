#
# @lc app=leetcode id=890 lang=python3
#
# [890] Find and Replace Pattern
#
# https://leetcode.com/problems/find-and-replace-pattern/description/
#
# algorithms
# Medium (77.09%)
# Likes:    4045
# Dislikes: 175
# Total Accepted:    219K
# Total Submissions: 284K
# Testcase Example:  "[\"abc\",\"deq\",\"mee\",\"aqq\",\"dkd\",\"ccc\"]"
#
# Given a list of strings words and a string pattern, return a list of words[i]
# that match pattern. You may return the answer in any order.
#
# A word matches the pattern if there exists a permutation of letters p so that
# after replacing every letter x in the pattern with p(x), we get the desired
# word.
#
# Recall that a permutation of letters is a bijection from letters to letters:
# every letter maps to another letter, and no two letters map to the same
# letter.
#
# Example 1:
#
# Input: words = ["abc","deq","mee","aqq","dkd","ccc"], pattern = "abb"
# Output: ["mee","aqq"]
# Explanation: "mee" matches the pattern because there is a permutation {a ->
# m, b -> e, ...}.
# "ccc" does not match the pattern because {a -> c, b -> c, ...} is not a
# permutation, since a and b map to the same letter.
#
# Example 2:
#
# Input: words = ["a","b","c"], pattern = "a"
# Output: ["a","b","c"]
#
# Constraints:
#
# 1 <= pattern.length <= 20
#
# 1 <= words.length <= 50
#
# words[i].length == pattern.length
#
# pattern and words[i] are lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def findAndReplacePattern(self, words: List[str], pattern: str) -> List[str]:
        """
        Interview explanation:
        Word matches pattern iff there is a bijection letter→letter (isomorphic
        strings). Normalize both by first-occurrence mapping or dual maps.

        Algorithm:
        - normalize(s): map each char to first index order string.
        - Filter words where normalize(w)==normalize(pattern).

        Complexity: O(total chars) time, O(1) alphabet maps.
        """
        def norm(s: str) -> tuple:
            mp = {}
            out = []
            for ch in s:
                if ch not in mp:
                    mp[ch] = len(mp)
                out.append(mp[ch])
            return tuple(out)

        p = norm(pattern)
        return [w for w in words if norm(w) == p]

    def findAndReplacePattern_maps(self, words: List[str], pattern: str) -> List[str]:
        """
        Interview explanation:
        Alternate: maintain bijection maps word↔pattern; reject conflicts.

        Algorithm:
        - For each word zip with pattern; enforce w2p and p2w consistency.

        Complexity: O(total chars) time.
        """
        def match(word: str) -> bool:
            w2p, p2w = {}, {}
            for a, b in zip(word, pattern):
                if a in w2p and w2p[a] != b:
                    return False
                if b in p2w and p2w[b] != a:
                    return False
                w2p[a] = b
                p2w[b] = a
            return True

        return [w for w in words if match(w)]
# @lc code=end

