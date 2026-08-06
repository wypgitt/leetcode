#
# @lc app=leetcode id=303 lang=python3
#
# [303] Range Sum Query - Immutable
#
# https://leetcode.com/problems/range-sum-query-immutable/description/
#
# algorithms
# Easy (73.04%)
# Likes:    3949
# Dislikes: 2029
# Total Accepted:    994K
# Total Submissions: 1.4M
# Testcase Example:  "[\"NumArray\",\"sumRange\",\"sumRange\",\"sumRange\"]"
#
# Given an integer array nums, handle multiple queries of the following type:
#
# Calculate the sum of the elements of nums between indices left and right
# inclusive where left <= right.
#
# Implement the NumArray class:
#
# NumArray(int[] nums) Initializes the object with the integer array nums.
#
# int sumRange(int left, int right) Returns the sum of the elements of nums
# between indices left and right inclusive (i.e. nums[left] + nums[left + 1] +
# ... + nums[right]).
#
# Example 1:
#
# Input
# ["NumArray", "sumRange", "sumRange", "sumRange"]
# [[[-2, 0, 3, -5, 2, -1]], [0, 2], [2, 5], [0, 5]]
# Output
# [null, 1, -1, -3]
#
# Explanation
# NumArray numArray = new NumArray([-2, 0, 3, -5, 2, -1]);
# numArray.sumRange(0, 2); // return (-2) + 0 + 3 = 1
# numArray.sumRange(2, 5); // return 3 + (-5) + 2 + (-1) = -1
# numArray.sumRange(0, 5); // return (-2) + 0 + 3 + (-5) + 2 + (-1) = -3
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^5 <= nums[i] <= 10^5
#
# 0 <= left <= right < nums.length
#
# At most 10^4 calls will be made to sumRange.
#

# @lc code=start
from typing import List


class NumArray:
    def __init__(self, nums: List[int]):
        """
        Interview explanation:
        Prefix sums: prefix[i+1] = sum(nums[:i+1]). Range sum [left,right] =
        prefix[right+1] - prefix[left].

        Algorithm:
        - Build prefix with a leading 0; append running totals for each nums[i].

        Complexity: O(n) build, O(1) query, O(n) space.
        """
        self.prefix = [0]
        for x in nums:
            self.prefix.append(self.prefix[-1] + x)

    def sumRange(self, left: int, right: int) -> int:
        """
        Interview explanation:
        Inclusive range sum via two prefix lookups.

        Algorithm:
        - Return prefix[right+1] - prefix[left].

        Complexity: O(1) time, O(1) space.
        """
        return self.prefix[right + 1] - self.prefix[left]


# Your NumArray object will be instantiated and called as such:
# obj = NumArray(nums)
# param_1 = obj.sumRange(left,right)
# @lc code=end

