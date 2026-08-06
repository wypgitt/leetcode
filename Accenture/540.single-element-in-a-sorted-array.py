#
# @lc app=leetcode id=540 lang=python3
#
# [540] Single Element in a Sorted Array
#
# https://leetcode.com/problems/single-element-in-a-sorted-array/description/
#
# algorithms
# Medium (59.38%)
# Likes:    13229
# Dislikes: 253
# Total Accepted:    1.3M
# Total Submissions: 2.2M
# Testcase Example:  "[1,1,2,3,3,4,4,8,8]"
#
# You are given a sorted array consisting of only integers where every element
# appears exactly twice, except for one element which appears exactly once.
#
# Return the single element that appears only once.
#
# Your solution must run in O(log n) time and O(1) space.
#
# Example 1:
#
# Input: nums = [1,1,2,3,3,4,4,8,8]
# Output: 2
#
# Example 2:
#
# Input: nums = [3,3,7,7,10,11,11]
# Output: 10
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List
class Solution:
    def singleNonDuplicate(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Paired duplicates occupy even-odd index pairs until the single element
        shifts pairing. Binary search on even indices: if nums[m] == nums[m+1],
        single is to the right; else to the left (including m).

        Algorithm:
        - lo, hi on even indices; mid forced even; compare mid with mid+1.

        Complexity: O(log n) time, O(1) space.
        """
        lo, hi = 0, len(nums) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if mid % 2:
                mid -= 1
            if nums[mid] == nums[mid + 1]:
                lo = mid + 2
            else:
                hi = mid
        return nums[lo]
# @lc code=end

