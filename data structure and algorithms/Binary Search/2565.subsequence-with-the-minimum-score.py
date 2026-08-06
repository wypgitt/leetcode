#
# @lc app=leetcode id=2565 lang=python3
#
# [2565] Subsequence With the Minimum Score
#
# https://leetcode.com/problems/subsequence-with-the-minimum-score/description/
#
# algorithms
# Hard (33.60%)
# Likes:    412
# Dislikes: 7
# Total Accepted:    11K
# Total Submissions: 32.7K
# Testcase Example:  "\"abacaba\"\n\"bzaa\""
#
# You are given two strings s and t.
#
# You are allowed to remove any number of characters from the string t.
#
# The score of the string is 0 if no characters are removed from the string t,
# otherwise:
#
#
# Let left be the minimum index among all removed characters.
#
#
# Let right be the maximum index among all removed characters.
#
# Then the score of the string is right - left + 1.
#
# Return the minimum possible score to make t a subsequence of s.
#
# A subsequence of a string is a new string that is formed from the original
# string by deleting some (can be none) of the characters without disturbing the
# relative positions of the remaining characters. (i.e., "ace" is a subsequence
# of "abcde" while "aec" is not).
#
#
#
# Example 1:
#
# Input: s = "abacaba", t = "bzaa"
# Output: 1
# Explanation: In this example, we remove the character "z" at index 1
# (0-indexed).
# The string t becomes "baa" which is a subsequence of the string "abacaba" and
# the score is 1 - 1 + 1 = 1.
# It can be proven that 1 is the minimum score that we can achieve.
#
# Example 2:
#
# Input: s = "cde", t = "xyz"
# Output: 3
# Explanation: In this example, we remove characters "x", "y" and "z" at indices
# 0, 1, and 2 (0-indexed).
# The string t becomes "" which is a subsequence of the string "cde" and the
# score is 2 - 0 + 1 = 3.
# It can be proven that 3 is the minimum score that we can achieve.
#
#
#
# Constraints:
#
#
# 1 <= s.length, t.length <= 10^5
#
#
# s and t consist of only lowercase English letters.
#

# @lc code=start
class Solution:
    def minimumScore(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Remove one contiguous substring from t so the remaining characters form a
        subsequence of s; minimize the removed length.

        Algorithm:
        - left[i]: earliest position in s matching t[0..i] as subsequence.
        - right[i]: latest position in s matching t[i..m-1].
        - Two pointers over prefix/suffix boundaries; ans = min j-i-1 with left[i]<right[j].

        Complexity: O(n+m) time, O(m) space.
        """
        n, m = len(s), len(t)
        left = [-1] * m
        p = 0
        for i in range(m):
            while p < n and s[p] != t[i]:
                p += 1
            if p == n:
                break
            left[i] = p
            p += 1
        right = [-1] * m
        p = n - 1
        for i in range(m - 1, -1, -1):
            while p >= 0 and s[p] != t[i]:
                p -= 1
            if p < 0:
                break
            right[i] = p
            p -= 1
        ans = m
        j = 0
        # empty prefix: remove t[0..j-1], keep suffix from j
        while j < m and right[j] != -1:
            ans = min(ans, j)
            j += 1
        # empty suffix handled inside loop; also full match
        if left[-1] != -1:
            return 0
        j = 0
        for i in range(m):
            if left[i] == -1:
                break
            # keep prefix t[0..i], remove until j where right[j] > left[i]
            if j <= i:
                j = i + 1
            while j < m and right[j] <= left[i]:
                j += 1
            ans = min(ans, j - i - 1 if j < m else m - i - 1)
        return ans
# @lc code=end
