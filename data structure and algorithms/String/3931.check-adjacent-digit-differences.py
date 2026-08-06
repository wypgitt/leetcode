#
# @lc app=leetcode id=3931 lang=python3
#
# [3931] Check Adjacent Digit Differences
#
# https://leetcode.com/problems/check-adjacent-digit-differences/description/
#
# algorithms
# Easy (78.04%)
# Likes:    18
# Dislikes: 1
# Total Accepted:    48.8K
# Total Submissions: 62.6K
# Testcase Example:  "\"132\""
#
#
# You are given a string s consisting of digits.
#
# Return true if the absolute difference between every pair of adjacent
# digits is at most 2, otherwise return false.
#
# The absolute difference between a and b is defined as abs(a - b).
#
# Example 1:
#
# Input: s = "132"
#
# Output: true
#
# Explanation:
#
# The absolute difference between digits at s[0] and s[1] is abs(1 - 3) =
# 2.
#
# The absolute difference between digits at s[1] and s[2] is abs(3 - 2) =
# 1.
#
# Since both differences are at most 2, the answer is true.
#
# Example 2:
#
# Input: s = "129"
#
# Output: false
#
# Explanation:
#
# The absolute difference between digits at s[0] and s[1] is abs(1 - 2) =
# 1.
#
# The absolute difference between digits at s[1] and s[2] is abs(2 - 9) =
# 7, which is greater than 2.
#
# Therefore, the answer is false.
#
# Constraints:
#
# 2 <= s.length <= 100
#
# s consists only of digits.
#

# @lc code=start

class Solution:
    def isAdjacentDiffAtMostTwo(self, s: str) -> bool:
        """
        Interview explanation:
        Check that every pair of neighboring digits differs by at most 2.

        Algorithm:
        - Scan adjacent characters; fail if abs(int difference) > 2.

        Complexity: O(n) time, O(1) space.
        """
        for i in range(1, len(s)):
            if abs(ord(s[i]) - ord(s[i - 1])) > 2:
                return False
        return True

    def isAdjacentDiffAtMostTwo_all(self, s: str) -> bool:
        """
        Interview explanation:
        Alternate: all() over adjacent pairs.

        Algorithm:
        - Return all(abs(int(s[i]) - int(s[i-1])) <= 2 for i in range(1, n)).

        Complexity: O(n) time, O(1) space.
        """
        return all(abs(ord(s[i]) - ord(s[i - 1])) <= 2 for i in range(1, len(s)))
# @lc code=end
