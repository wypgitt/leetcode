#
# @lc app=leetcode id=2626 lang=python3
#
# [2626] Array Reduce Transformation
#
# https://leetcode.com/problems/array-reduce-transformation/description/
#
# algorithms
# Easy (85.50%)
# Likes:    781
# Dislikes: 51
# Total Accepted:    304.8K
# Total Submissions: 356.5K
# Testcase Example:  "[1,2,3,4]\nfunction sum(accum, curr) { return accum + curr; }\n0"
#
# Given an integer array nums, a reducer function fn, and an initial value init,
# return the final result obtained by executing the fn function on each element
# of the array, sequentially, passing in the return value from the calculation
# on the preceding element.
#
# This result is achieved through the following operations: val = fn(init,
# nums[0]), val = fn(val, nums[1]), val = fn(val, nums[2]), ... until every
# element in the array has been processed. The ultimate value of val is then
# returned.
#
# If the length of the array is 0, the function should return init.
#
# Please solve it without using the built-in Array.reduce method.
#
#
#
# Example 1:
#
# Input:
# nums = [1,2,3,4]
# fn = function sum(accum, curr) { return accum + curr; }
# init = 0
# Output: 10
# Explanation:
# initially, the value is init=0.
# (0) + nums[0] = 1
# (1) + nums[1] = 3
# (3) + nums[2] = 6
# (6) + nums[3] = 10
# The final answer is 10.
#
# Example 2:
#
# Input:
# nums = [1,2,3,4]
# fn = function sum(accum, curr) { return accum + curr * curr; }
# init = 100
# Output: 130
# Explanation:
# initially, the value is init=100.
# (100) + nums[0] * nums[0] = 101
# (101) + nums[1] * nums[1] = 105
# (105) + nums[2] * nums[2] = 114
# (114) + nums[3] * nums[3] = 130
# The final answer is 130.
#
# Example 3:
#
# Input:
# nums = []
# fn = function sum(accum, curr) { return 0; }
# init = 25
# Output: 25
# Explanation: For empty arrays, the answer is always init.
#
#
#
# Constraints:
#
#
# 0 <= nums.length <= 1000
#
#
# 0 <= nums[i] <= 1000
#
#
# 0 <= init <= 1000
#

# @lc code=start
from typing import Any, Callable, List


def reduce(nums: List[int], fn: Callable[[Any, int], Any], init: Any) -> Any:
    """
    Interview explanation:
    Left-fold nums with fn starting from init (Array.reduce port without
    using built-in reduce).

    Algorithm:
    - Start val = init; for each x in nums set val = fn(val, x); return val.

    Complexity: O(n) time, O(1) extra space besides fn.
    """
    val = init
    for x in nums:
        val = fn(val, x)
    return val


class Solution:
    def reduce(self, nums: List[int], fn: Callable[[Any, int], Any], init: Any) -> Any:
        """
        Interview explanation:
        Thin Solution wrapper for reduce.

        Algorithm:
        - Delegate to reduce(nums, fn, init).

        Complexity: O(n) time, O(1) extra space.
        """
        return reduce(nums, fn, init)
# @lc code=end
