#
# @lc app=leetcode id=4 lang=python3
#
# [4] Median of Two Sorted Arrays
#
# https://leetcode.com/problems/median-of-two-sorted-arrays/description/
#
# algorithms
# Hard (47.27%)
# Likes:    32545
# Dislikes: 3598
# Total Accepted:    4.5M
# Total Submissions: 9.5M
# Testcase Example:  "[1,3]"
#
# Given two sorted arrays nums1 and nums2 of size m and n respectively, return
# the median of the two sorted arrays.
#
# The overall run time complexity should be O(log (m+n)).
#
# Example 1:
#
# Input: nums1 = [1,3], nums2 = [2]
# Output: 2.00000
# Explanation: merged array = [1,2,3] and median is 2.
#
# Example 2:
#
# Input: nums1 = [1,2], nums2 = [3,4]
# Output: 2.50000
# Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.
#
# Constraints:
#
# nums1.length == m
#
# nums2.length == n
#
# 0 <= m <= 1000
#
# 0 <= n <= 1000
#
# 1 <= m + n <= 2000
#
# -10^6 <= nums1[i], nums2[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        """
        Interview explanation:
        Binary search the partition on the shorter array so left halves of both
        arrays together contain half the elements. A valid cut has every left
        value <= every right value across the cut.

        Algorithm:
        - Always binary-search on the shorter array A.
        - For mid cut i in A, take j = half - i from B.
        - If A[i-1] > B[j], cut is too far right; shrink high.
        - If B[j-1] > A[i], cut is too far left; raise low.
        - Otherwise the partition is correct; median is max(left) or average of
          max(left) and min(right) depending on total length parity.

        Complexity: O(log(min(m, n))) time, O(1) space.
        """
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1

        m, n = len(nums1), len(nums2)
        low, high = 0, m
        half = (m + n + 1) // 2

        while low <= high:
            i = (low + high) // 2
            j = half - i

            a_left = nums1[i - 1] if i > 0 else float("-inf")
            a_right = nums1[i] if i < m else float("inf")
            b_left = nums2[j - 1] if j > 0 else float("-inf")
            b_right = nums2[j] if j < n else float("inf")

            if a_left > b_right:
                high = i - 1
            elif b_left > a_right:
                low = i + 1
            else:
                left_max = max(a_left, b_left)
                if (m + n) % 2 == 1:
                    return float(left_max)
                return (left_max + min(a_right, b_right)) / 2.0

        raise ValueError("unreachable")
# @lc code=end
