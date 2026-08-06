#
# @lc app=leetcode id=2161 lang=python3
#
# [2161] Partition Array According to Given Pivot
#
# https://leetcode.com/problems/partition-array-according-to-given-pivot/description/
#
# algorithms
# Medium (90.75%)
# Likes:    1991
# Dislikes: 134
# Total Accepted:    459.4K
# Total Submissions: 506.2K
# Testcase Example:  "[9,12,5,10,14,3,10]\n10"
#
# You are given a 0-indexed integer array nums and an integer pivot. Rearrange
# nums such that the following conditions are satisfied:
#
#
# Every element less than pivot appears before every element greater than pivot.
#
#
# Every element equal to pivot appears in between the elements less than and
# greater than pivot.
#
#
# The relative order of the elements less than pivot and the elements greater
# than pivot is maintained.
#
#
#
# More formally, consider every p_i, p_j where p_i is the new position of the
# i^th element and p_j is the new position of the j^th element. If i < j and
# both elements are smaller (or larger) than pivot, then p_i < p_j.
#
#
#
#
#
# Return nums after the rearrangement.
#
#
#
# Example 1:
#
# Input: nums = [9,12,5,10,14,3,10], pivot = 10
# Output: [9,5,3,10,10,12,14]
# Explanation:
# The elements 9, 5, and 3 are less than the pivot so they are on the left side
# of the array.
# The elements 12 and 14 are greater than the pivot so they are on the right
# side of the array.
# The relative ordering of the elements less than and greater than pivot is also
# maintained. [9, 5, 3] and [12, 14] are the respective orderings.
#
# Example 2:
#
# Input: nums = [-3,4,3,2], pivot = 2
# Output: [-3,2,4,3]
# Explanation:
# The element -3 is less than the pivot so it is on the left side of the array.
# The elements 4 and 3 are greater than the pivot so they are on the right side
# of the array.
# The relative ordering of the elements less than and greater than pivot is also
# maintained. [-3] and [4, 3] are the respective orderings.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# -10^6 <= nums[i] <= 10^6
#
#
# pivot equals to an element of nums.
#

# @lc code=start
from typing import List


class Solution:
    def pivotArray(self, nums: List[int], pivot: int) -> List[int]:
        """
        Interview explanation:
        Rearrange so every element < pivot comes first, then == pivot, then >
        pivot, preserving relative order within each group (stable partition).

        Algorithm:
        (three passes / lists)
        - Collect less, equal, greater in order; concatenate.

        Complexity: O(n) time, O(n) space.
        """
        less, equal, greater = [], [], []
        for x in nums:
            if x < pivot:
                less.append(x)
            elif x == pivot:
                equal.append(x)
            else:
                greater.append(x)
        return less + equal + greater

    def pivotArray_two_pointers(self, nums: List[int], pivot: int) -> List[int]:
        """
        Interview explanation:
        Alternate: fill result from both ends after counting equals, or single
        pass writing less from left and greater from right then fill equals.

        Algorithm:
        - First write all < pivot left-to-right; count equals; write > pivot
          right-to-left into a buffer; fill middle with pivot.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        ans = [0] * n
        left, right = 0, n - 1
        for x in nums:
            if x < pivot:
                ans[left] = x
                left += 1
        for x in reversed(nums):
            if x > pivot:
                ans[right] = x
                right -= 1
        for i in range(left, right + 1):
            ans[i] = pivot
        return ans
# @lc code=end
