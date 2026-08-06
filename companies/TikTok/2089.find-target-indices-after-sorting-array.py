#
# @lc app=leetcode id=2089 lang=python3
#
# [2089] Find Target Indices After Sorting Array
#
# https://leetcode.com/problems/find-target-indices-after-sorting-array/description/
#
# algorithms
# Easy (78.26%)
# Likes:    1985
# Dislikes: 107
# Total Accepted:    291.7K
# Total Submissions: 372.7K
# Testcase Example:  "[1,2,5,2,3]\n2"
#
# You are given a 0-indexed integer array nums and a target element target.
#
# A target index is an index i such that nums[i] == target.
#
# Return a list of the target indices of nums after sorting nums in
# non-decreasing order. If there are no target indices, return an empty list.
# The returned list must be sorted in increasing order.
#
#
#
# Example 1:
#
# Input: nums = [1,2,5,2,3], target = 2
# Output: [1,2]
# Explanation: After sorting, nums is [1,2,2,3,5].
# The indices where nums[i] == 2 are 1 and 2.
#
# Example 2:
#
# Input: nums = [1,2,5,2,3], target = 3
# Output: [3]
# Explanation: After sorting, nums is [1,2,2,3,5].
# The index where nums[i] == 3 is 3.
#
# Example 3:
#
# Input: nums = [1,2,5,2,3], target = 5
# Output: [4]
# Explanation: After sorting, nums is [1,2,2,3,5].
# The index where nums[i] == 5 is 4.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 100
#
#
# 1 <= nums[i], target <= 100
#

# @lc code=start
from typing import List


class Solution:
    def targetIndices(self, nums: List[int], target: int) -> List[int]:
        """
        Interview explanation:
        After sorting nums ascending, return all indices where value == target.

        Algorithm:
        - less = count of values < target; eq = count == target;
          indices = less .. less+eq-1.

        Complexity: O(n) time, O(1) extra space (aside from output).
        """
        less = eq = 0
        for x in nums:
            if x < target:
                less += 1
            elif x == target:
                eq += 1
        return list(range(less, less + eq))

    def targetIndices_sort(self, nums: List[int], target: int) -> List[int]:
        """
        Interview explanation:
        Alternate: sort then collect matching indices.

        Algorithm:
        - Sort; scan for target.

        Complexity: O(n log n) time, O(n) space depending on sort.
        """
        nums = sorted(nums)
        return [i for i, x in enumerate(nums) if x == target]
# @lc code=end
