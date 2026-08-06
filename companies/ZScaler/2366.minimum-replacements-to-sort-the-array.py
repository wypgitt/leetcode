#
# @lc app=leetcode id=2366 lang=python3
#
# [2366] Minimum Replacements to Sort the Array
#
# https://leetcode.com/problems/minimum-replacements-to-sort-the-array/description/
#
# algorithms
# Hard (53.10%)
# Likes:    2109
# Dislikes: 69
# Total Accepted:    76.8K
# Total Submissions: 144.7K
# Testcase Example:  "[3,9,3]"
#
# You are given a 0-indexed integer array nums. In one operation you can replace
# any element of the array with any two elements that sum to it.
#
#
# For example, consider nums = [5,6,7]. In one operation, we can replace nums[1]
# with 2 and 4 and convert nums to [5,2,4,7].
#
# Return the minimum number of operations to make an array that is sorted in
# non-decreasing order.
#
#
#
# Example 1:
#
# Input: nums = [3,9,3]
# Output: 2
# Explanation: Here are the steps to sort the array in non-decreasing order:
# - From [3,9,3], replace the 9 with 3 and 6 so the array becomes [3,3,6,3]
# - From [3,3,6,3], replace the 6 with 3 and 3 so the array becomes [3,3,3,3,3]
# There are 2 steps to sort the array in non-decreasing order. Therefore, we
# return 2.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5]
# Output: 0
# Explanation: The array is already in non-decreasing order. Therefore, we
# return 0.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def minimumReplacement(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Replace any element with any positive ints summing to it (one op per
        split into k parts costs k-1). Make array non-decreasing; min ops.

        Algorithm:
        - Greedy right-to-left: bound = nums[-1]; for each x, if x>bound split
          into parts <= bound; parts = ceil(x/bound); ops += parts-1;
          new bound = x // parts.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        ops = 0
        bound = nums[-1]
        for i in range(n - 2, -1, -1):
            x = nums[i]
            if x <= bound:
                bound = x
                continue
            parts = (x + bound - 1) // bound
            ops += parts - 1
            bound = x // parts
        return ops
# @lc code=end
