#
# @lc app=leetcode id=246 lang=python3
#
# [246] Strobogrammatic Number
#
# https://leetcode.com/problems/strobogrammatic-number/description/
#
# algorithms
# Easy (47.50%)
# Likes:    638
# Dislikes: 1053
# Total Accepted:    213.3K
# Total Submissions: 449K
# Testcase Example:  "\"69\""
#
#
# Given a string num which represents an integer, return true if num is a
# strobogrammatic number.
#
# A strobogrammatic number is a number that looks the same when rotated
# 180 degrees (looked at upside down).
#
# Example 1:
#
# Input: num = "69"
# Output: true
#
# Example 2:
#
# Input: num = "88"
# Output: true
#
# Example 3:
#
# Input: num = "962"
# Output: false
#
# Constraints:
#
# 1 <= num.length <= 50
#
# num consists of only digits.
#
# num does not contain any leading zeros except for zero itself.
#
# @lc code=start
class Solution:
    def isStrobogrammatic(self, num: str) -> bool:
        """
        Interview explanation:
        A strobogrammatic number looks the same upside down. Valid digit pairs:
        0-0, 1-1, 6-9, 8-8, 9-6. Two pointers from both ends verify the mapping.

        Algorithm:
        - Map rotatable digits; left/right pointers.
        - Check map[num[l]] == num[r]; advance inward.

        Complexity: O(n) time, O(1) space.
        """
        rotate = {"0": "0", "1": "1", "6": "9", "8": "8", "9": "6"}
        left, right = 0, len(num) - 1
        while left <= right:
            a, b = num[left], num[right]
            if a not in rotate or rotate[a] != b:
                return False
            left += 1
            right -= 1
        return True
# @lc code=end
