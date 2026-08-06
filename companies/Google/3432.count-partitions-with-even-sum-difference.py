#
# @lc app=leetcode id=3432 lang=python3
#
# [3432] Count Partitions with Even Sum Difference
#
# https://leetcode.com/problems/count-partitions-with-even-sum-difference/description/
#
# algorithms
# Easy (85.10%)
# Likes:    417
# Dislikes: 14
# Total Accepted:    180K
# Total Submissions: 211.5K
# Testcase Example:  "[10,10,3,7,6]"
#
#
# You are given an integer array nums of length n.
#
# A partition is defined as an index i where 0 <= i < n - 1, splitting the
# array into two non-empty subarrays such that:
#
# Left subarray contains indices [0, i].
#
# Right subarray contains indices [i + 1, n - 1].
#
# Return the number of partitions where the difference between the sum of
# the left and right subarrays is even.
#
# Example 1:
#
# Input: nums = [10,10,3,7,6]
#
# Output: 4
#
# Explanation:
#
# The 4 partitions are:
#
# [10], [10, 3, 7, 6] with a sum difference of 10 - 26 = -16, which is
# even.
#
# [10, 10], [3, 7, 6] with a sum difference of 20 - 16 = 4, which is even.
#
# [10, 10, 3], [7, 6] with a sum difference of 23 - 13 = 10, which is
# even.
#
# [10, 10, 3, 7], [6] with a sum difference of 30 - 6 = 24, which is even.
#
# Example 2:
#
# Input: nums = [1,2,2]
#
# Output: 0
#
# Explanation:
#
# No partition results in an even sum difference.
#
# Example 3:
#
# Input: nums = [2,4,6,8]
#
# Output: 3
#
# Explanation:
#
# All partitions result in an even sum difference.
#
# Constraints:
#
# 2 <= n == nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def countPartitions(self, nums: List[int]) -> int:
        """
        Interview explanation:
        left - right is even iff left and right have the same parity, iff total
        sum is even (since left+right = total). Every split works when total is
        even; none when odd.

        Algorithm:
        - Alternate: scan prefix left; count splits where (2*left - total) is even
          (same as total even for all n-1 splits).

        Complexity: O(n) time, O(1) space.
        """
        total = sum(nums)
        if total % 2:
            return 0
        return len(nums) - 1
# @lc code=end
