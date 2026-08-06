#
# @lc app=leetcode id=3192 lang=python3
#
# [3192] Minimum Operations to Make Binary Array Elements Equal to One II
#
# https://leetcode.com/problems/minimum-operations-to-make-binary-array-elements-equal-to-one-ii/description/
#
# algorithms
# Medium (65.37%)
# Likes:    160
# Dislikes: 9
# Total Accepted:    44.7K
# Total Submissions: 68.4K
# Testcase Example:  "[0,1,1,0,1]"
#
#
# You are given a binary array nums.
#
# You can do the following operation on the array any number of times
# (possibly zero):
#
# Choose any index i from the array and flip all the elements from index i
# to the end of the array.
#
# Flipping an element means changing its value from 0 to 1, and from 1 to
# 0.
#
# Return the minimum number of operations required to make all elements in
# nums equal to 1.
#
# Example 1:
#
# Input: nums = [0,1,1,0,1]
#
# Output: 4
#
# Explanation:
#
# We can do the following operations:
#
# Choose the index i = 1. The resulting array will be nums = [0,0,0,1,0].
#
# Choose the index i = 0. The resulting array will be nums = [1,1,1,0,1].
#
# Choose the index i = 4. The resulting array will be nums = [1,1,1,0,0].
#
# Choose the index i = 3. The resulting array will be nums = [1,1,1,1,1].
#
# Example 2:
#
# Input: nums = [1,0,0,0]
#
# Output: 1
#
# Explanation:
#
# We can do the following operation:
#
# Choose the index i = 1. The resulting array will be nums = [1,1,1,1].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 1
#

# @lc code=start

from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Flip suffix starting at i any times. Target all 1s. Each time the current
        effective bit is 0, we must flip from here (toggle global flip parity).

        Algorithm:
        - Track flip parity; for each nums[i], effective = nums[i]^parity.
        - If effective is 0, increment ops and toggle parity.

        Complexity: O(n) time, O(1) space.
        """
        ops = 0
        flip = 0
        for x in nums:
            if x ^ flip == 0:
                ops += 1
                flip ^= 1
        return ops

    def minOperations_groups(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Equivalent: count how many times the needed value changes as we scan,
        starting from needing 1 (with initial "previous" as 1).

        Algorithm:
        - ans = 0; prev = 1; for x in nums: if x != prev: ans++; prev = x.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        prev = 1
        for x in nums:
            if x != prev:
                ans += 1
                prev = x
        return ans
# @lc code=end
