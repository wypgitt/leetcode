#
# @lc app=leetcode id=1785 lang=python3
#
# [1785] Minimum Elements to Add to Form a Given Sum
#
# https://leetcode.com/problems/minimum-elements-to-add-to-form-a-given-sum/description/
#
# algorithms
# Medium (45.31%)
# Likes:    290
# Dislikes: 196
# Total Accepted:    28.5K
# Total Submissions: 62.8K
# Testcase Example:  "[1,-1,1]"
#
# You are given an integer array nums and two integers limit and goal. The
# array nums has an interesting property that abs(nums[i]) <= limit.
#
# Return the minimum number of elements you need to add to make the sum of the
# array equal to goal. The array must maintain its property that abs(nums[i])
# <= limit.
#
# Note that abs(x) equals x if x >= 0, and -x otherwise.
#
# Example 1:
#
# Input: nums = [1,-1,1], limit = 3, goal = -4
# Output: 2
# Explanation: You can add -2 and -3, then the sum of the array will be 1 - 1 +
# 1 - 2 - 3 = -4.
#
# Example 2:
#
# Input: nums = [1,-10,9,1], limit = 100, goal = 0
# Output: 1
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= limit <= 10^6
#
# -limit <= nums[i] <= limit
#
# -10^9 <= goal <= 10^9
#

# @lc code=start
from typing import List
import math


class Solution:
    def minElements(self, nums: List[int], limit: int, goal: int) -> int:
        """
        Interview explanation:
        Add the fewest integers in [-limit, limit] so array sum becomes goal.
        Need to cover diff = |goal − sum(nums)|; each element covers at most
        `limit` → ceil(diff / limit).

        Algorithm:
        - return ceil(abs(goal - sum(nums)) / limit)

        Complexity: O(n) time, O(1) space.
        """
        diff = abs(goal - sum(nums))
        return (diff + limit - 1) // limit

    def minElements_math(self, nums: List[int], limit: int, goal: int) -> int:
        """
        Interview explanation:
        Alternate using math.ceil on the absolute difference ratio.

        Algorithm:
        - math.ceil(abs(goal-sum)/limit) with zero-diff guard.

        Complexity: O(n).
        """
        diff = abs(goal - sum(nums))
        return 0 if diff == 0 else math.ceil(diff / limit)
# @lc code=end
