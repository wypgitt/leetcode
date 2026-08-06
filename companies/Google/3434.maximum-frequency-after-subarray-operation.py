#
# @lc app=leetcode id=3434 lang=python3
#
# [3434] Maximum Frequency After Subarray Operation
#
# https://leetcode.com/problems/maximum-frequency-after-subarray-operation/description/
#
# algorithms
# Medium (31.51%)
# Likes:    280
# Dislikes: 36
# Total Accepted:    26.4K
# Total Submissions: 83.9K
# Testcase Example:  "[1,2,3,4,5,6]\n1"
#
#
# You are given an array nums of length n. You are also given an integer
# k.
#
# You perform the following operation on nums once:
#
# Select a subarray nums[i..j] where 0 <= i <= j <= n - 1.
#
# Select an integer x and add x to all the elements in nums[i..j].
#
# Find the maximum frequency of the value k after the operation.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5,6], k = 1
#
# Output: 2
#
# Explanation:
#
# After adding -5 to nums[2..5], 1 has a frequency of 2 in [1, 2, -2, -1,
# 0, 1].
#
# Example 2:
#
# Input: nums = [10,2,3,4,5,5,4,3,2,2], k = 10
#
# Output: 4
#
# Explanation:
#
# After adding 8 to nums[1..9], 10 has a frequency of 4 in [10, 10, 11,
# 12, 13, 13, 12, 11, 10, 10].
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 50
#
# 1 <= k <= 50
#

# @lc code=start
from typing import List


class Solution:
    def maxFrequency(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        One subarray add turns some values into k. Existing k's outside the
        subarray stay; inside, converting target->k gains a k but may "lose" an
        existing k covered by the same window. Maximize gain via Kadane over each
        possible target != k.

        Algorithm:
        - Base = count of k.
        - For each target in 1..50, target != k: treat +1 for target, -1 for k,
          reset on negative (Kadane); take max gain.
        - Answer = base + max gain (0 if no conversion helps).

        Complexity: O(50 n) = O(n) time, O(1) space.
        """
        return nums.count(k) + max(
            (self._kadane(nums, target, k) for target in range(1, 51) if target != k),
            default=0,
        )

    def _kadane(self, nums: List[int], target: int, k: int) -> int:
        max_sum = cur = 0
        for num in nums:
            if num == target:
                cur += 1
            elif num == k:
                cur -= 1
            if cur < 0:
                cur = 0
            max_sum = max(max_sum, cur)
        return max_sum
# @lc code=end
