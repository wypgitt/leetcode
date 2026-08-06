#
# @lc app=leetcode id=3674 lang=python3
#
# [3674] Minimum Operations to Equalize Array
#
# https://leetcode.com/problems/minimum-operations-to-equalize-array/description/
#
# algorithms
# Easy (60.84%)
# Likes:    62
# Dislikes: 13
# Total Accepted:    57.1K
# Total Submissions: 93.8K
# Testcase Example:  "[1,2]"
#
#
# You are given an integer array nums of length n.
#
# In one operation, choose any subarray nums[l...r] (0 <= l <= r < n) and
# replace each element in that subarray with the bitwise AND of all
# elements.
#
# Return the minimum number of operations required to make all elements of
# nums equal.
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# Example 1:
#
# Input: nums = [1,2]
#
# Output: 1
#
# Explanation:
#
# Choose nums[0...1]: (1 AND 2) = 0, so the array becomes [0, 0] and all
# elements are equal in 1 operation.
#
# Example 2:
#
# Input: nums = [5,5,5]
#
# Output: 0
#
# Explanation:
#
# nums is [5, 5, 5] which already has all elements equal, so 0 operations
# are required.
#
# Constraints:
#
# 1 <= n == nums.length <= 100
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        AND-replacing a subarray can only clear bits. One operation on the whole
        array makes every entry equal to AND(nums). If already equal, need 0.

        Algorithm:
        - If all elements equal return 0 else return 1.

        Complexity: O(n) time, O(1) space.
        """
        return 0 if all(x == nums[0] for x in nums) else 1

    def minOperations_set(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: uniqueness via a set.

        Algorithm:
        - Return 0 if len(set(nums)) == 1 else 1.

        Complexity: O(n) time, O(U) space.
        """
        return 0 if len(set(nums)) == 1 else 1
# @lc code=end
