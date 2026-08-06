#
# @lc app=leetcode id=2381 lang=python3
#
# [2381] Shifting Letters II
#
# https://leetcode.com/problems/shifting-letters-ii/description/
#
# algorithms
# Medium (53.81%)
# Likes:    1808
# Dislikes: 72
# Total Accepted:    165.9K
# Total Submissions: 308.4K
# Testcase Example:  "\"abc\"\n[[0,1,0],[1,2,1],[0,2,1]]"
#
# You are given a string s of lowercase English letters and a 2D integer array
# shifts where shifts[i] = [start_i, end_i, direction_i]. For every i, shift the
# characters in s from the index start_i to the index end_i (inclusive) forward
# if direction_i = 1, or shift the characters backward if direction_i = 0.
#
# Shifting a character forward means replacing it with the next letter in the
# alphabet (wrapping around so that 'z' becomes 'a'). Similarly, shifting a
# character backward means replacing it with the previous letter in the alphabet
# (wrapping around so that 'a' becomes 'z').
#
# Return the final string after all such shifts to s are applied.
#
#
#
# Example 1:
#
# Input: s = "abc", shifts = [[0,1,0],[1,2,1],[0,2,1]]
# Output: "ace"
# Explanation: Firstly, shift the characters from index 0 to index 1 backward.
# Now s = "zac".
# Secondly, shift the characters from index 1 to index 2 forward. Now s = "zbd".
# Finally, shift the characters from index 0 to index 2 forward. Now s = "ace".
#
# Example 2:
#
# Input: s = "dztz", shifts = [[0,0,0],[1,1,1]]
# Output: "catz"
# Explanation: Firstly, shift the characters from index 0 to index 0 backward.
# Now s = "cztz".
# Finally, shift the characters from index 1 to index 1 forward. Now s = "catz".
#
#
#
# Constraints:
#
#
# 1 <= s.length, shifts.length <= 5 * 10^4
#
#
# shifts[i].length == 3
#
#
# 0 <= start_i <= end_i < s.length
#
#
# 0 <= direction_i <= 1
#
#
# s consists of lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def shiftingLetters(self, s: str, shifts: List[List[int]]) -> str:
        """
        Interview explanation:
        Apply range shifts: direction 1 forward, 0 backward on s[start..end].
        Return final string.

        Algorithm:
        - Difference array of net shifts; prefix sum; map each char mod 26.

        Complexity: O(n + m) time, O(n) space.
        """
        n = len(s)
        diff = [0] * (n + 1)
        for start, end, d in shifts:
            val = 1 if d == 1 else -1
            diff[start] += val
            diff[end + 1] -= val
        cur = 0
        out = []
        for i, ch in enumerate(s):
            cur += diff[i]
            out.append(chr((ord(ch) - 97 + cur) % 26 + 97))
        return ''.join(out)
# @lc code=end
