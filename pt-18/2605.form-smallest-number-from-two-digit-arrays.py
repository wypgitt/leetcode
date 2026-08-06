#
# @lc app=leetcode id=2605 lang=python3
#
# [2605] Form Smallest Number From Two Digit Arrays
#
# https://leetcode.com/problems/form-smallest-number-from-two-digit-arrays/description/
#
# algorithms
# Easy (55.33%)
# Likes:    331
# Dislikes: 29
# Total Accepted:    53.7K
# Total Submissions: 97K
# Testcase Example:  "[4,1,3]\n[5,7]"
#
# Given two arrays of unique digits nums1 and nums2, return the smallest number
# that contains at least one digit from each array.
#
#
#
# Example 1:
#
# Input: nums1 = [4,1,3], nums2 = [5,7]
# Output: 15
# Explanation: The number 15 contains the digit 1 from nums1 and the digit 5
# from nums2. It can be proven that 15 is the smallest number we can have.
#
# Example 2:
#
# Input: nums1 = [3,5,2,6], nums2 = [3,1,7]
# Output: 3
# Explanation: The number 3 contains the digit 3 which exists in both arrays.
#
#
#
# Constraints:
#
#
# 1 <= nums1.length, nums2.length <= 9
#
#
# 1 <= nums1[i], nums2[i] <= 9
#
#
# All digits in each array are unique.
#

# @lc code=start
from typing import List


class Solution:
    def minNumber(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Form the smallest number that uses at least one digit from each array.

        Algorithm:
        - If any shared digit exists, return the minimum shared digit.
        - Else return 10 * min(min(nums1), min(nums2)) + max(min(nums1), min(nums2)).

        Complexity: O(1) time (digits 1–9), O(1) space.
        """
        s1, s2 = set(nums1), set(nums2)
        shared = s1 & s2
        if shared:
            return min(shared)
        a, b = min(nums1), min(nums2)
        return 10 * min(a, b) + max(a, b)
# @lc code=end
