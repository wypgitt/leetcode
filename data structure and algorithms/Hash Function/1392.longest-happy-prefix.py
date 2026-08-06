#
# @lc app=leetcode id=1392 lang=python3
#
# [1392] Longest Happy Prefix
#
# https://leetcode.com/problems/longest-happy-prefix/description/
#
# algorithms
# Hard (53.7%)
# Likes:    1618
# Dislikes: 49
# Total Accepted:    112K
# Total Submissions: 209K
# Testcase Example:  "\"level\""
#
# A string is called a happy prefix if it is a non-empty prefix which is also a
# suffix (excluding itself).
#
# Given a string s, return the longest happy prefix of s. Return an empty
# string "" if no such prefix exists.
#
# Example 1:
#
# Input: s = "level"
# Output: "l"
# Explanation: s contains 4 prefix excluding itself ("l", "le", "lev", "leve"),
# and suffix ("l", "el", "vel", "evel"). The largest prefix which is also
# suffix is given by "l".
#
# Example 2:
#
# Input: s = "ababab"
# Output: "abab"
# Explanation: "abab" is the largest prefix which is also suffix. They can
# overlap in the original string.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s contains only lowercase English letters.
#

# @lc code=start

class Solution:
    def longestPrefix(self, s: str) -> str:
        """
        Interview explanation:
        Longest proper prefix that is also a suffix = LPS[n-1] from KMP prefix
        function (pi array).

        Algorithm:
        - Build pi (KMP LPS) for s; return s[:pi[-1]]

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        pi = [0] * n
        j = 0
        for i in range(1, n):
            while j and s[i] != s[j]:
                j = pi[j - 1]
            if s[i] == s[j]:
                j += 1
                pi[i] = j
        return s[: pi[-1]]

    def longestPrefix_z(self, s: str) -> str:
        """
        Interview explanation:
        Alternate Z-algorithm: Z[i] is longest substring from i matching prefix.
        Happy prefix length is max i where Z[i]==n-i.

        Algorithm:
        - Compute Z-array; scan i where Z[i]==n-i; take largest such n-i

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        z = [0] * n
        l = r = 0
        for i in range(1, n):
            if i < r:
                z[i] = min(r - i, z[i - l])
            while i + z[i] < n and s[z[i]] == s[i + z[i]]:
                z[i] += 1
            if i + z[i] > r:
                l, r = i, i + z[i]
        best = 0
        for i in range(1, n):
            if z[i] == n - i:
                best = max(best, z[i])
        return s[:best]
# @lc code=end
