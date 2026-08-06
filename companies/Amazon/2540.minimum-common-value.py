#
# @lc app=leetcode id=2540 lang=python3
#
# [2540] Minimum Common Value
#
# https://leetcode.com/problems/minimum-common-value/description/
#
# algorithms
# Easy (60.74%)
# Likes:    1412
# Dislikes: 45
# Total Accepted:    455K
# Total Submissions: 749.1K
# Testcase Example:  "[1,2,3]\n[2,4]"
#
# Given two integer arrays nums1 and nums2, sorted in non-decreasing order,
# return the minimum integer common to both arrays. If there is no common
# integer amongst nums1 and nums2, return -1.
#
# Note that an integer is said to be common to nums1 and nums2 if both arrays
# have at least one occurrence of that integer.
#
#
#
# Example 1:
#
# Input: nums1 = [1,2,3], nums2 = [2,4]
# Output: 2
# Explanation: The smallest element common to both arrays is 2, so we return 2.
#
# Example 2:
#
# Input: nums1 = [1,2,3,6], nums2 = [2,3,4,5]
# Output: 2
# Explanation: There are two common elements in the array 2 and 3 out of which 2
# is the smallest, so 2 is returned.
#
#
#
# Constraints:
#
#
# 1 <= nums1.length, nums2.length <= 10^5
#
#
# 1 <= nums1[i], nums2[j] <= 10^9
#
#
# Both nums1 and nums2 are sorted in non-decreasing order.
#

# @lc code=start
from typing import List


class Solution:
    def getCommon(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Both arrays sorted nondecreasing; return the minimum common value, or -1.

        Algorithm:
        (Two pointers)
        - Advance the pointer at the smaller value; on equal return that value.

        Complexity: O(n + m) time, O(1) space.
        """
        i = j = 0
        n, m = len(nums1), len(nums2)
        while i < n and j < m:
            if nums1[i] == nums2[j]:
                return nums1[i]
            if nums1[i] < nums2[j]:
                i += 1
            else:
                j += 1
        return -1

    def getCommon_set(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Alternate: put one array in a set; scan the other (sorted) for first hit.

        Algorithm:
        - Build set(nums2); iterate nums1 in order; return first membership.

        Complexity: O(n + m) time, O(m) space.
        """
        seen = set(nums2)
        for x in nums1:
            if x in seen:
                return x
        return -1
# @lc code=end
