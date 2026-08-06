#
# @lc app=leetcode id=1745 lang=python3
#
# [1745] Palindrome Partitioning IV
#
# https://leetcode.com/problems/palindrome-partitioning-iv/description/
#
# algorithms
# Hard (45.52%)
# Likes:    973
# Dislikes: 31
# Total Accepted:    35.0K
# Total Submissions: 77.0K
# Testcase Example:  "\"abcbdd\""
#
# Given a string s, return true if it is possible to split the string s into
# three non-empty palindromic substrings. Otherwise, return false.
#
# A string is said to be palindrome if it the same string when reversed.
#
# Example 1:
#
# Input: s = "abcbdd"
# Output: true
# Explanation: "abcbdd" = "a" + "bcb" + "dd", and all three substrings are
# palindromes.
#
# Example 2:
#
# Input: s = "bcbddxy"
# Output: false
# Explanation: s cannot be split into 3 palindromes.
#
# Constraints:
#
# 3 <= s.length <= 2000
#
# s consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def checkPartitioning(self, s: str) -> bool:
        """
        Interview explanation:
        Check whether s splits into exactly three non-empty palindromes.
        Precompute isPal[i][j]; try all cut points.

        Algorithm:
        - DP isPal; for i,j with 0<=i<j<n-1 check three segments palindromes.

        Complexity: O(n^2) time, O(n^2) space.
        """
        n = len(s)
        isPal = [[False] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j] and (j - i < 2 or isPal[i + 1][j - 1]):
                    isPal[i][j] = True
        for i in range(n - 2):
            if not isPal[0][i]:
                continue
            for j in range(i + 1, n - 1):
                if isPal[i + 1][j] and isPal[j + 1][n - 1]:
                    return True
        return False
# @lc code=end
