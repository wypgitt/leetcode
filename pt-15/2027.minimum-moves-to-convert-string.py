#
# @lc app=leetcode id=2027 lang=python3
#
# [2027] Minimum Moves to Convert String
#
# https://leetcode.com/problems/minimum-moves-to-convert-string/description/
#
# algorithms
# Easy (58.22%)
# Likes:    546
# Dislikes: 82
# Total Accepted:    62.7K
# Total Submissions: 107.7K
# Testcase Example:  "\"XXX\""
#
# You are given a string s consisting of n characters which are either 'X' or
# 'O'.
#
# A move is defined as selecting three consecutive characters of s and
# converting them to 'O'. Note that if a move is applied to the character 'O',
# it will stay the same.
#
# Return the minimum number of moves required so that all the characters of s
# are converted to 'O'.
#
#
#
# Example 1:
#
# Input: s = "XXX"
# Output: 1
# Explanation: XXX -> OOO
# We select all the 3 characters and convert them in one move.
#
# Example 2:
#
# Input: s = "XXOX"
# Output: 2
# Explanation: XXOX -> OOOX -> OOOO
# We select the first 3 characters in the first move, and convert them to 'O'.
# Then we select the last 3 characters and convert them so that the final string
# contains all 'O's.
#
# Example 3:
#
# Input: s = "OOOO"
# Output: 0
# Explanation: There are no 'X's in s to convert.
#
#
#
# Constraints:
#
#
# 3 <= s.length <= 1000
#
#
# s[i] is either 'X' or 'O'.
#

# @lc code=start
class Solution:
    def minimumMoves(self, s: str) -> int:
        """
        Interview explanation:
        Convert string of X/O to all O; a move flips any 3 consecutive chars.
        Minimize moves (greedy cover each X).

        Algorithm:
        - Scan left to right; on X, take a move covering i..i+2 and jump i+=3.

        Complexity: O(n) time, O(1) space.
        """
        i = ans = 0
        n = len(s)
        while i < n:
            if s[i] == 'X':
                ans += 1
                i += 3
            else:
                i += 1
        return ans
# @lc code=end
