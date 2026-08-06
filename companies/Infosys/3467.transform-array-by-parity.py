#
# @lc app=leetcode id=3467 lang=python3
#
# [3467] Transform Array by Parity
#
# https://leetcode.com/problems/transform-array-by-parity/description/
#
# algorithms
# Easy (89.88%)
# Likes:    119
# Dislikes: 10
# Total Accepted:    106.6K
# Total Submissions: 118.6K
# Testcase Example:  "[4,3,2,1]"
#
#
# You are given an integer array nums. Transform nums by performing the
# following operations in the exact order specified:
#
# Replace each even number with 0.
#
# Replace each odd numbers with 1.
#
# Sort the modified array in non-decreasing order.
#
# Return the resulting array after performing these operations.
#
# Example 1:
#
# Input: nums = [4,3,2,1]
#
# Output: [0,0,1,1]
#
# Explanation:
#
# Replace the even numbers (4 and 2) with 0 and the odd numbers (3 and 1)
# with 1. Now, nums = [0, 1, 0, 1].
#
# After sorting nums in non-descending order, nums = [0, 0, 1, 1].
#
# Example 2:
#
# Input: nums = [1,5,1,4,2]
#
# Output: [0,0,1,1,1]
#
# Explanation:
#
# Replace the even numbers (4 and 2) with 0 and the odd numbers (1, 5 and
# 1) with 1. Now, nums = [1, 1, 1, 0, 0].
#
# After sorting nums in non-descending order, nums = [0, 0, 1, 1, 1].
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def transformArray(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Map even->0 and odd->1, then sort. Equivalent to counting zeros then ones.

        Algorithm:
        - Count even numbers as zeros; append that many 0s then the rest 1s.

        Complexity: O(n) time, O(n) space for the answer.
        """
        zeros = sum(1 for x in nums if x % 2 == 0)
        return [0] * zeros + [1] * (len(nums) - zeros)

    def transformArray_sort(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: replace by parity then sort explicitly.

        Algorithm:
        - nums[i] = nums[i] % 2; return sorted(nums).

        Complexity: O(n log n) time, O(n) space.
        """
        return sorted(x % 2 for x in nums)
# @lc code=end

