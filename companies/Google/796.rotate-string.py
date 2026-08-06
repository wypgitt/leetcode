#
# @lc app=leetcode id=796 lang=python3
#
# [796] Rotate String
#
# https://leetcode.com/problems/rotate-string/description/
#
# algorithms
# Easy (66.72%)
# Likes:    5064
# Dislikes: 467
# Total Accepted:    991K
# Total Submissions: 1.5M
# Testcase Example:  "\"m\""
#
# Given two strings s and goal, return true if and only if s can become goal
# after some number of shifts on s.
#
# A shift on s consists of moving the leftmost character of s to the rightmost
# position.
#
# For example, if s = "abcde", then it will be "bcdea" after one shift.
#
# Example 1:
#
# Input: s = "abcde", goal = "cdeab"
# Output: true
#
# Example 2:
#
# Input: s = "abcde", goal = "abced"
# Output: false
#
# Constraints:
#
# 1 <= s.length, goal.length <= 100
#
# s and goal consist of lowercase English letters.
#

# @lc code=start
class Solution:
    def rotateString(self, s: str, goal: str) -> bool:
        """
        Interview explanation:
        s can become goal by rotations iff same length and goal is a substring
        of s+s (all rotations appear there).

        Algorithm:
        - return len(s)==len(goal) and goal in s+s

        Complexity: O(n) time typical, O(n) space.
        """
        return len(s) == len(goal) and goal in s + s
# @lc code=end

