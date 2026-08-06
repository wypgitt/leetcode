#
# @lc app=leetcode id=291 lang=python3
#
# [291] Word Pattern II
#
# https://leetcode.com/problems/word-pattern-ii/description/
#
# algorithms
# Medium (49.13%)
# Likes:    951
# Dislikes: 78
# Total Accepted:    85.9K
# Total Submissions: 174.9K
# Testcase Example:  "\"abab\"\n\"redblueredblue\""
#
#
# Given a pattern and a string s, return true if s matches the pattern.
#
# A string s matches a pattern if there is some bijective mapping of
# single characters to non-empty strings such that if each character in
# pattern is replaced by the string it maps to, then the resulting string
# is s. A bijective mapping means that no two characters map to the same
# string, and no character maps to two different strings.
#
# Example 1:
#
# Input: pattern = "abab", s = "redblueredblue"
# Output: true
# Explanation: One possible mapping is as follows:
# 'a' -> "red"
# 'b' -> "blue"
#
# Example 2:
#
# Input: pattern = "aaaa", s = "asdasdasdasd"
# Output: true
# Explanation: One possible mapping is as follows:
# 'a' -> "asd"
#
# Example 3:
#
# Input: pattern = "aabb", s = "xyzabcxzyabc"
# Output: false
#
# Constraints:
#
# 1 <= pattern.length, s.length <= 20
#
# pattern and s consist of only lowercase English letters.
#
# @lc code=start
class Solution:
    def wordPatternMatch(self, pattern: str, s: str) -> bool:
        """
        Interview explanation:
        Bijection between pattern chars and non-empty substrings of s.
        Backtrack: for pattern[i], try every unused substring starting at j,
        or reuse an existing mapping if it matches the prefix.

        Algorithm:
        - Maps char→str and used strings set for injectivity.
        - DFS(i, j); success when both exhausted together.

        Complexity: exponential in worst case; O(|pattern| + |s|) space.
        """
        p2s, used = {}, set()

        def dfs(i: int, j: int) -> bool:
            if i == len(pattern) and j == len(s):
                return True
            if i == len(pattern) or j == len(s):
                return False
            c = pattern[i]
            if c in p2s:
                word = p2s[c]
                if s.startswith(word, j):
                    return dfs(i + 1, j + len(word))
                return False
            for k in range(j + 1, len(s) + 1):
                word = s[j:k]
                if word in used:
                    continue
                p2s[c] = word
                used.add(word)
                if dfs(i + 1, k):
                    return True
                del p2s[c]
                used.remove(word)
            return False

        return dfs(0, 0)
# @lc code=end

