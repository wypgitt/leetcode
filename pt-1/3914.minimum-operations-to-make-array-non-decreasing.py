#
# @lc app=leetcode id=3914 lang=python3
#
# [3914] Minimum Operations to Make Array Non Decreasing
#
# https://leetcode.com/problems/minimum-operations-to-make-array-non-decreasing/description/
#
# algorithms
# Medium (55.66%)
# Likes:    59
# Dislikes: 3
# Total Accepted:    25.1K
# Total Submissions: 45.2K
# Testcase Example:  "[3,3,2,1]"
#
#
# You are given an integer array nums of length n.
#
# In one operation, you may choose any subarray nums[l..r] and increase
# each element in that subarray by x, where x is any positive integer.
#
# Return the minimum possible sum of the values of x across all operations
# required to make the array non-decreasing.
#
# An array is non-decreasing if nums[i] <= nums[i + 1] for all 0 <= i < n
# - 1.
#
# Example 1:
#
# Input: nums = [3,3,2,1]
#
# Output: 2
#
# Explanation:
#
# One optimal set of operations:
#
# Choose subarray [2..3] and add x = 1 resulting in [3, 3, 3, 2]
#
# Choose subarray [3..3] and add x = 1 resulting in [3, 3, 3, 3]
#
# The array becomes non-decreasing, and the total sum of chosen x values
# is 1 + 1 = 2.
#
# Example 2:
#
# Input: nums = [5,1,2,3]
#
# Output: 4
#
# Explanation:
#
# One optimal set of operations:
#
# Choose subarray [1..3] and add x = 4 resulting in [5, 5, 6, 7]
#
# The array becomes non-decreasing, and the total sum of chosen x values
# is 4.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Make the array non-decreasing by adding positive x to subarrays; minimize
        the total sum of chosen x values.

        Algorithm:
        - Each descent nums[i] > nums[i+1] forces at least nums[i]-nums[i+1]
          extra increment covering i+1 (and possibly further).
        - Summing positive adjacent drops is necessary and sufficient.

        Complexity: O(n) time, O(1) space.
        """
        answer = 0

        for left, right in zip(nums, nums[1:]):
            if left > right:
                answer += left - right

        return answer
# @lc code=end
