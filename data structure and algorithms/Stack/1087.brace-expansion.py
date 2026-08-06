#
# @lc app=leetcode id=1087 lang=python3
#
# [1087] Brace Expansion
#
# https://leetcode.com/problems/brace-expansion/description/
#
# algorithms
# Medium (66.90%)
# Likes:    667
# Dislikes: 57
# Total Accepted:    68K
# Total Submissions: 101.6K
# Testcase Example:  "\"{a,b}c{d,e}f\""
#
#
# You are given a string s representing a list of words. Each letter in
# the word has one or more options.
#
# If there is one option, the letter is represented as is.
#
# If there is more than one option, then curly braces delimit the options.
# For example, "{a,b,c}" represents options ["a", "b", "c"].
#
# For example, if s = "a{b,c}", the first character is always 'a', but the
# second character can be 'b' or 'c'. The original list is ["ab", "ac"].
#
# Return all words that can be formed in this manner, sorted in
# lexicographical order.
#
# Example 1:
#
# Input: s = "{a,b}c{d,e}f"
# Output: ["acdf","acef","bcdf","bcef"]
#
# Example 2:
#
# Input: s = "abcd"
# Output: ["abcd"]
#
# Constraints:
#
# 1 <= s.length <= 50
#
# s consists of curly brackets '{}', commas ',', and lowercase English
# letters.
#
# s is guaranteed to be a valid input.
#
# There are no nested curly brackets.
#
# All characters inside a pair of consecutive opening and ending curly
# brackets are different.
#
# @lc code=start
from typing import List


class Solution:
    def expand(self, s: str) -> List[str]:
        """
        Interview explanation:
        Premium. Expand brace groups like "{a,b}c{d,e}" into all concatenations
        in lexicographic order. Parse into options lists, then backtrack.

        Algorithm (parse + backtrack):
        - Parse: if '{...}', split comma options (sorted); else singleton char.
        - dfs(i, path): append each option at group i; at end collect string.

        Complexity: O(P · L) where P = product of option sizes, L = result length.
        """
        groups = []
        i, n = 0, len(s)
        while i < n:
            if s[i] == "{":
                j = s.index("}", i)
                opts = sorted(s[i + 1 : j].split(","))
                groups.append(opts)
                i = j + 1
            else:
                groups.append([s[i]])
                i += 1

        ans = []

        def dfs(idx: int, path: List[str]) -> None:
            if idx == len(groups):
                ans.append("".join(path))
                return
            for ch in groups[idx]:
                path.append(ch)
                dfs(idx + 1, path)
                path.pop()

        dfs(0, [])
        return ans
# @lc code=end
