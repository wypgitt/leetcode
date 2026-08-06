#
# @lc app=leetcode id=2769 lang=python3
#
# [2769] Find the Maximum Achievable Number
#
# https://leetcode.com/problems/find-the-maximum-achievable-number/description/
#
# algorithms
# Easy (91.61%)
# Likes:    545
# Dislikes: 784
# Total Accepted:    229.5K
# Total Submissions: 250.5K
# Testcase Example:  "4\n1"
#
# Given two integers, num and t. A number x is achievable if it can become equal
# to num after applying the following operation at most t times:
#
#
# Increase or decrease x by 1, and simultaneously increase or decrease num by 1.
#
# Return the maximum possible value of x.
#
#
#
# Example 1:
#
# Input: num = 4, t = 1
#
# Output: 6
#
# Explanation:
#
# Apply the following operation once to make the maximum achievable number equal
# to num:
#
#
# Decrease the maximum achievable number by 1, and increase num by 1.
#
# Example 2:
#
# Input: num = 3, t = 2
#
# Output: 7
#
# Explanation:
#
# Apply the following operation twice to make the maximum achievable number
# equal to num:
#
#
# Decrease the maximum achievable number by 1, and increase num by 1.
#
#
#
# Constraints:
#
#
# 1 <= num, t <= 50
#

# @lc code=start
class Solution:
    def theMaximumAchievableX(self, num: int, t: int) -> int:
        """
        Interview explanation:
        In one op, num += 1 or -1 and x does the opposite. Max achievable x after
        at most t ops equals num + 2t (always push them apart).

        Algorithm:
        - Return num + 2 * t.

        Complexity: O(1).
        """
        return num + t * 2
# @lc code=end
