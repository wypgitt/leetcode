#
# @lc app=leetcode id=2168 lang=python3
#
# [2168] Unique Substrings With Equal Digit Frequency
#
# https://leetcode.com/problems/unique-substrings-with-equal-digit-frequency/description/
#
# algorithms
# Medium (64.59%)
# Likes:    105
# Dislikes: 14
# Total Accepted:    10.1K
# Total Submissions: 15.6K
# Testcase Example:  "\"1212\""
#
#
# Given a digit string s, return the number of unique substrings of s
# where every digit appears the same number of times.
#
# Example 1:
#
# Input: s = "1212"
# Output: 5
# Explanation: The substrings that meet the requirements are "1", "2",
# "12", "21", "1212".
# Note that although the substring "12" appears twice, it is only counted
# once.
#
# Example 2:
#
# Input: s = "12321"
# Output: 9
# Explanation: The substrings that meet the requirements are "1", "2",
# "3", "12", "23", "32", "21", "123", "321".
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists of digits.
#
# @lc code=start
class Solution:
    def equalDigitFrequency(self, s: str) -> int:
        """
        Interview explanation:
        Premium. Count unique substrings where every digit that appears does so
        with the same frequency.

        Algorithm:
        (prefix counts + hash set)
        - Build prefix frequency of digits 0-9.
        - Enumerate all O(n^2) substrings; check equal positive freqs; insert
          substring into a set (or rolling hash) for uniqueness.

        Complexity: O(n^2 * 10) time, O(n^2) space worst-case for the set.
        """
        n = len(s)
        presum = [[0] * 10 for _ in range(n + 1)]
        for i, c in enumerate(s):
            for d in range(10):
                presum[i + 1][d] = presum[i][d]
            presum[i + 1][ord(c) - 48] += 1

        def ok(i: int, j: int) -> bool:
            freq = None
            for d in range(10):
                cnt = presum[j + 1][d] - presum[i][d]
                if cnt > 0:
                    if freq is None:
                        freq = cnt
                    elif cnt != freq:
                        return False
            return True

        vis = {s[i : j + 1] for i in range(n) for j in range(i, n) if ok(i, j)}
        return len(vis)
# @lc code=end
