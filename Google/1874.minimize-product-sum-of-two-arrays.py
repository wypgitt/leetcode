#
# @lc app=leetcode id=1874 lang=python3
#
# [1874] Minimize Product Sum of Two Arrays
#
# https://leetcode.com/problems/minimize-product-sum-of-two-arrays/description/
#
# algorithms
# Medium (89.88%)
# Likes:    257
# Dislikes: 28
# Total Accepted:    25.7K
# Total Submissions: 28.6K
# Testcase Example:  "[5,3,4,2]\n[4,2,2,5]"
#
#
# The product sum of two equal-length arrays a and b is equal to the sum
# of a[i] * b[i] for all 0 <= i < a.length (0-indexed).
#
#
#
#
#
# For example, if a = [1,2,3,4] and b = [5,2,3,1], the product sum would
# be 1*5 + 2*2 + 3*3 + 4*1 = 22.
#
#
#
#
#
# Given two arrays nums1 and nums2 of length n, return the minimum product
# sum if you are allowed to rearrange the order of the elements in nums1.
#
#
#
#
#
# Example 1:
#
#
#
#
# Input: nums1 = [5,3,4,2], nums2 = [4,2,2,5]
# Output: 40
# Explanation: We can rearrange nums1 to become [3,5,4,2]. The product sum
# of [3,5,4,2] and [4,2,2,5] is 3*4 + 5*2 + 4*2 + 2*5 = 40.
#
#
#
#
# Example 2:
#
#
#
#
# Input: nums1 = [2,1,4,5,7], nums2 = [3,2,4,8,6]
# Output: 65
# Explanation: We can rearrange nums1 to become [5,7,4,1,2]. The product
# sum of [5,7,4,1,2] and [3,2,4,8,6] is 5*3 + 7*2 + 4*4 + 1*8 + 2*6 = 65.
#
#
#
#
#
#
# Constraints:
#
#
#
#
#
# n == nums1.length == nums2.length
#
#
# 1 <= n <= 10^5
#
#
# 1 <= nums1[i], nums2[i] <= 100
#
# @lc code=start
from typing import List


class Solution:
    def minProductSum(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Premium: rearrange nums1 to minimize sum nums1[i]*nums2[i]. Pair
        smallest with largest (rearrangement inequality).

        Algorithm:
        - Sort nums1 ascending, nums2 descending; sum products.

        Complexity: O(n log n) time, O(n) or O(1) extra if sort in place.
        """
        nums1.sort()
        nums2.sort(reverse=True)
        return sum(a * b for a, b in zip(nums1, nums2))

    def minProductSum_two_sorts(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Alternate: sort both ascending; pair nums1[i] with nums2[n-1-i].

        Algorithm:
        - a=sorted(nums1); b=sorted(nums2); sum(a[i]*b[n-1-i]).

        Complexity: O(n log n) time.
        """
        a = sorted(nums1)
        b = sorted(nums2)
        n = len(a)
        return sum(a[i] * b[n - 1 - i] for i in range(n))
# @lc code=end
