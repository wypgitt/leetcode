#
# @lc app=leetcode id=3229 lang=python3
#
# [3229] Minimum Operations to Make Array Equal to Target
#
# https://leetcode.com/problems/minimum-operations-to-make-array-equal-to-target/description/
#
# algorithms
# Hard (41.63%)
# Likes:    306
# Dislikes: 12
# Total Accepted:    25.2K
# Total Submissions: 60.5K
# Testcase Example:  "[3,5,1,2]\n[4,6,2,4]"
#
#
# You are given two positive integer arrays nums and target, of the same
# length.
#
# In a single operation, you can select any subarray of nums and increment
# each element within that subarray by 1 or decrement each element within
# that subarray by 1.
#
# Return the minimum number of operations required to make nums equal to
# the array target.
#
# Example 1:
#
# Input: nums = [3,5,1,2], target = [4,6,2,4]
#
# Output: 2
#
# Explanation:
#
# We will perform the following operations to make nums equal to target:
#
# - Increment nums[0..3] by 1, nums = [4,6,2,3].
#
# - Increment nums[3..3] by 1, nums = [4,6,2,4].
#
# Example 2:
#
# Input: nums = [1,3,2], target = [2,1,4]
#
# Output: 5
#
# Explanation:
#
# We will perform the following operations to make nums equal to target:
#
# - Increment nums[0..0] by 1, nums = [2,3,2].
#
# - Decrement nums[1..1] by 1, nums = [2,2,2].
#
# - Decrement nums[1..1] by 1, nums = [2,1,2].
#
# - Increment nums[2..2] by 1, nums = [2,1,3].
#
# - Increment nums[2..2] by 1, nums = [2,1,4].
#
# Constraints:
#
# 1 <= nums.length == target.length <= 10^5
#
# 1 <= nums[i], target[i] <= 10^8
#

# @lc code=start
from typing import List


class Solution:
    def minimumOperations(self, nums: List[int], target: List[int]) -> int:
        """
        Interview explanation:
        Range +1/-1 ops on nums to reach target equal building the difference
        array d = target - nums with range updates. New positive jumps in d each
        need a fresh increment operation.

        Algorithm:
        - d[i] = target[i] - nums[i].
        - ans = sum of max(d[i] - d[i-1], 0) with d[-1] = 0.

        Complexity: O(n) time, O(1) space.
        Alternate: sum |d[i]-d[i-1]| / 2 with sentinels 0 (same result).
        """
        prev = 0
        ans = 0
        for a, b in zip(nums, target):
            cur = b - a
            if cur > prev:
                ans += cur - prev
            prev = cur
        return ans

# @lc code=end
