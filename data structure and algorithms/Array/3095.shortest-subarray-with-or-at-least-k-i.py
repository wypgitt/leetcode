#
# @lc app=leetcode id=3095 lang=python3
#
# [3095] Shortest Subarray With OR at Least K I
#
# https://leetcode.com/problems/shortest-subarray-with-or-at-least-k-i/description/
#
# algorithms
# Easy (44.95%)
# Likes:    145
# Dislikes: 24
# Total Accepted:    41.1K
# Total Submissions: 91.5K
# Testcase Example:  "[1,2,3]\n2"
#
#
# You are given an array nums of non-negative integers and an integer k.
#
# An array is called special if the bitwise OR of all of its elements is
# at least k.
#
# Return the length of the shortest special non-empty subarray of nums, or
# return -1 if no special subarray exists.
#
# Example 1:
#
# Input: nums = [1,2,3], k = 2
#
# Output: 1
#
# Explanation:
#
# The subarray [3] has OR value of 3. Hence, we return 1.
#
# Note that [2] is also a special subarray.
#
# Example 2:
#
# Input: nums = [2,1,8], k = 10
#
# Output: 3
#
# Explanation:
#
# The subarray [2,1,8] has OR value of 11. Hence, we return 3.
#
# Example 3:
#
# Input: nums = [1,2], k = 0
#
# Output: 1
#
# Explanation:
#
# The subarray [1] has OR value of 1. Hence, we return 1.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 0 <= nums[i] <= 50
#
# 0 <= k < 64
#

# @lc code=start
from typing import List


class Solution:
    def minimumSubarrayLength(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Shortest subarray whose bitwise OR is >= k (n <= 50).

        Algorithm:
        - Brute-force all subarrays; track running OR and min length.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(nums)
        ans = n + 1
        for i in range(n):
            cur = 0
            for j in range(i, n):
                cur |= nums[j]
                if cur >= k:
                    ans = min(ans, j - i + 1)
                    break
        return ans if ans <= n else -1

    def minimumSubarrayLength_window(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Same problem via bit-count sliding window (pattern used in the hard twin).

        Algorithm:
        - Expand OR with bit frequency counts; shrink while OR >= k.

        Complexity: O(n * 32) time, O(1) space.
        """
        n = len(nums)
        ans = n + 1
        bits = [0] * 32
        left = 0
        cur = 0
        for right, x in enumerate(nums):
            for b in range(32):
                if x >> b & 1:
                    if bits[b] == 0:
                        cur |= 1 << b
                    bits[b] += 1
            while left <= right and cur >= k:
                ans = min(ans, right - left + 1)
                y = nums[left]
                for b in range(32):
                    if y >> b & 1:
                        bits[b] -= 1
                        if bits[b] == 0:
                            cur ^= 1 << b
                left += 1
        return ans if ans <= n else -1
# @lc code=end
