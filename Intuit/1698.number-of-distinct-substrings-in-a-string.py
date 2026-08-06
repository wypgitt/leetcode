#
# @lc app=leetcode id=1698 lang=python3
#
# [1698] Number of Distinct Substrings in a String
#
# https://leetcode.com/problems/number-of-distinct-substrings-in-a-string/description/
#
# algorithms
# Medium (64.73%)
# Likes:    208
# Dislikes: 44
# Total Accepted:    14.6K
# Total Submissions: 22.5K
# Testcase Example:  "\"aabbaba\""
#
#
# Given a string s, return the number of distinct substrings of s.
#
# A substring of a string is obtained by deleting any number of characters
# (possibly zero) from the front of the string and any number (possibly
# zero) from the back of the string.
#
# Example 1:
#
# Input: s = "aabbaba"
# Output: 21
# Explanation: The set of distinct strings is
# ["a","b","aa","bb","ab","ba","aab","abb","bab","bba","aba","aabb","abba","bbab","baba","aabba","abbab","bbaba","aabbab","abbaba","aabbaba"]
#
# Example 2:
#
# Input: s = "abcdefg"
# Output: 28
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of lowercase English letters.
#
# Follow up: Can you solve this problem in O(n) time complexity?
#
# @lc code=start
class Solution:
    def countDistinct(self, s: str) -> int:
        """
        Interview explanation:
        Premium. Count distinct substrings of s. Trie of all suffixes (or set of
        all substrings). Trie: for each start i, insert s[i..] counting new nodes.

        Algorithm (suffix trie):
        - root={}; ans=0; for i in range(n): walk/create nodes from root along s[i:].

        Complexity: O(n^2) time/space worst-case.
        """
        root = {}
        ans = 0
        for i in range(len(s)):
            node = root
            for j in range(i, len(s)):
                c = s[j]
                if c not in node:
                    node[c] = {}
                    ans += 1
                node = node[c]
        return ans

    def countDistinct_set(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: put every substring s[i:j] into a hash set; size is answer.

        Algorithm:
        - set(s[i:j] for i in range(n) for j in range(i+1,n+1))

        Complexity: O(n^3) time typical string hashing, O(n^2) space.
        """
        n = len(s)
        return len({s[i:j] for i in range(n) for j in range(i + 1, n + 1)})
# @lc code=end
