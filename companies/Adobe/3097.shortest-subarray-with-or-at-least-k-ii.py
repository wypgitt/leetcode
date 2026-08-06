#
# @lc app=leetcode id=3097 lang=python3
#
# [3097] Shortest Subarray With OR at Least K II
#
# https://leetcode.com/problems/shortest-subarray-with-or-at-least-k-ii/description/
#
# algorithms
# Medium (50.27%)
# Likes:    768
# Dislikes: 73
# Total Accepted:    100.6K
# Total Submissions: 200.1K
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
# 1 <= nums.length <= 2 * 10^5
#
# 0 <= nums[i] <= 10^9
#
# 0 <= k <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minimumSubarrayLength(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Shortest subarray with bitwise OR >= k (n up to 2e5). OR only grows when
        expanding, so a two-pointer window works with bit multiplicity counts.

        Algorithm:
        - Maintain bit frequencies for the window OR; expand right, shrink left
          while OR >= k; track min length.

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
