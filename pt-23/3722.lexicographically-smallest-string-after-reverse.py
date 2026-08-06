#
# @lc app=leetcode id=3722 lang=python3
#
# [3722] Lexicographically Smallest String After Reverse
#
# https://leetcode.com/problems/lexicographically-smallest-string-after-reverse/description/
#
# algorithms
# Medium (54.94%)
# Likes:    43
# Dislikes: 7
# Total Accepted:    25.9K
# Total Submissions: 47.1K
# Testcase Example:  "\"dcab\""
#
#
# You are given a string s of length n consisting of lowercase English
# letters.
#
# You must perform exactly one operation by choosing any integer k such
# that 1 <= k <= n and either:
#
# reverse the first k characters of s, or
#
# reverse the last k characters of s.
#
# Return the lexicographically smallest string that can be obtained after
# exactly one such operation.
#
# Example 1:
#
# Input: s = "dcab"
#
# Output: "acdb"
#
# Explanation:
#
# Choose k = 3, reverse the first 3 characters.
#
# Reverse "dca" to "acd", resulting string s = "acdb", which is the
# lexicographically smallest string achievable.
#
# Example 2:
#
# Input: s = "abba"
#
# Output: "aabb"
#
# Explanation:
#
# Choose k = 3, reverse the last 3 characters.
#
# Reverse "bba" to "abb", so the resulting string is "aabb", which is the
# lexicographically smallest string achievable.
#
# Example 3:
#
# Input: s = "zxy"
#
# Output: "xzy"
#
# Explanation:
#
# Choose k = 2, reverse the first 2 characters.
#
# Reverse "zx" to "xz", so the resulting string is "xzy", which is the
# lexicographically smallest string achievable.
#
# Constraints:
#
# 1 <= n == s.length <= 1000
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def lexSmallest(self, s: str) -> str:
        """
        Interview explanation:
        Exactly one prefix or suffix reverse of length k. With n <= 1000,
        try every k and keep the lexicographically smallest result.

        Algorithm:
        - For each k in 1..n, form reverse(prefix k) and reverse(suffix k).
        - Track the global minimum string (including k = 1, which is a no-op).

        Complexity: O(n^2) time, O(n) space.
        """
        ans = s
        n = len(s)
        for k in range(1, n + 1):
            ans = min(ans, s[:k][::-1] + s[k:], s[: n - k] + s[n - k :][::-1])
        return ans

    def lexSmallest_prefix_focus(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: only compare candidates that start with the global minimum
        character (any better answer must).

        Algorithm:
        - mn = min(s); consider prefix reverses with s[k-1] == mn.
        - Also consider all suffix reverses; take the min string.

        Complexity: O(n * occ(mn) + n^2) worst case, O(n) space.
        """
        n = len(s)
        mn = min(s)
        ans = s
        for k in range(1, n + 1):
            if s[k - 1] == mn:
                ans = min(ans, s[:k][::-1] + s[k:])
            ans = min(ans, s[: n - k] + s[n - k :][::-1])
        return ans
# @lc code=end

