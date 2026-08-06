#
# @lc app=leetcode id=1664 lang=python3
#
# [1664] Ways to Make a Fair Array
#
# https://leetcode.com/problems/ways-to-make-a-fair-array/description/
#
# algorithms
# Medium (67.32%)
# Likes:    1423
# Dislikes: 51
# Total Accepted:    62.8K
# Total Submissions: 93.2K
# Testcase Example:  "[2,1,6,4]"
#
# You are given an integer array nums. You can choose exactly one index
# (0-indexed) and remove the element. Notice that the index of the elements may
# change after the removal.
#
# For example, if nums = [6,1,7,4,1]:
#
# Choosing to remove index 1 results in nums = [6,7,4,1].
#
# Choosing to remove index 2 results in nums = [6,1,4,1].
#
# Choosing to remove index 4 results in nums = [6,1,7,4].
#
# An array is fair if the sum of the odd-indexed values equals the sum of the
# even-indexed values.
#
# Return the number of indices that you could choose such that after the
# removal, nums is fair.
#
# Example 1:
#
# Input: nums = [2,1,6,4]
# Output: 1
# Explanation:
# Remove index 0: [1,6,4] -> Even sum: 1 + 4 = 5. Odd sum: 6. Not fair.
# Remove index 1: [2,6,4] -> Even sum: 2 + 4 = 6. Odd sum: 6. Fair.
# Remove index 2: [2,1,4] -> Even sum: 2 + 4 = 6. Odd sum: 1. Not fair.
# Remove index 3: [2,1,6] -> Even sum: 2 + 6 = 8. Odd sum: 1. Not fair.
# There is 1 index that you can remove to make nums fair.
#
# Example 2:
#
# Input: nums = [1,1,1]
# Output: 3
# Explanation: You can remove any index and the remaining array is fair.
#
# Example 3:
#
# Input: nums = [1,2,3]
# Output: 0
# Explanation: You cannot make a fair array after removing any index.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def waysToMakeFair(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Fair array: even-index sum == odd-index sum after deleting exactly one
        index. After deleting i, indices >i flip parity. Track right even/odd
        sums; scan left→right updating left and right.

        Algorithm:
        - Compute right even/odd; left=0; for each i, test left_even+right_odd
          == left_odd+right_even (post-delete), then move nums[i] into left.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        right_even = sum(nums[i] for i in range(0, n, 2))
        right_odd = sum(nums[i] for i in range(1, n, 2))
        left_even = left_odd = 0
        ans = 0
        for i, v in enumerate(nums):
            if i % 2 == 0:
                right_even -= v
            else:
                right_odd -= v
            if left_even + right_odd == left_odd + right_even:
                ans += 1
            if i % 2 == 0:
                left_even += v
            else:
                left_odd += v
        return ans
# @lc code=end
