#
# @lc app=leetcode id=3349 lang=python3
#
# [3349] Adjacent Increasing Subarrays Detection I
#
# https://leetcode.com/problems/adjacent-increasing-subarrays-detection-i/description/
#
# algorithms
# Easy (47.99%)
# Likes:    493
# Dislikes: 59
# Total Accepted:    162.3K
# Total Submissions: 338.2K
# Testcase Example:  "[2,5,7,8,9,2,3,4,3,1]\n3"
#
#
# Given an array nums of n integers and an integer k, determine whether
# there exist two adjacent subarrays of length k such that both subarrays
# are strictly increasing. Specifically, check if there are two subarrays
# starting at indices a and b (a < b), where:
#
# Both subarrays nums[a..a + k - 1] and nums[b..b + k - 1] are strictly
# increasing.
#
# The subarrays must be adjacent, meaning b = a + k.
#
# Return true if it is possible to find two such subarrays, and false
# otherwise.
#
# Example 1:
#
# Input: nums = [2,5,7,8,9,2,3,4,3,1], k = 3
#
# Output: true
#
# Explanation:
#
# The subarray starting at index 2 is [7, 8, 9], which is strictly
# increasing.
#
# The subarray starting at index 5 is [2, 3, 4], which is also strictly
# increasing.
#
# These two subarrays are adjacent, so the result is true.
#
# Example 2:
#
# Input: nums = [1,2,3,4,4,4,4,5,6,7], k = 5
#
# Output: false
#
# Constraints:
#
# 2 <= nums.length <= 100
#
# 1 < 2 * k <= nums.length
#
# -1000 <= nums[i] <= 1000
#

# @lc code=start

from typing import List


class Solution:
    def hasIncreasingSubarrays(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        Check for two adjacent strictly increasing length-k windows:
        nums[a..a+k) and nums[a+k..a+2k).

        Algorithm:
        - For each a in [0, n-2k], test both windows are strictly increasing.

        Complexity: O(n * k) time, O(1) space (n ≤ 100).
        """
        n = len(nums)

        def increasing(start: int) -> bool:
            for i in range(start, start + k - 1):
                if nums[i] >= nums[i + 1]:
                    return False
            return True

        for a in range(n - 2 * k + 1):
            if increasing(a) and increasing(a + k):
                return True
        return False

    def hasIncreasingSubarrays_streak(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        Alternate: track increasing streak lengths; accept if two consecutive
        streaks (or one long streak) cover 2k.

        Algorithm:
        - Maintain prev/cur run lengths; true if min(prev,cur)≥k or cur≥2k.

        Complexity: O(n) time, O(1) space.
        """
        prev = cur = 0
        for i, x in enumerate(nums):
            if i and x > nums[i - 1]:
                cur += 1
            else:
                prev, cur = cur, 1
            if min(prev, cur) >= k or cur >= 2 * k:
                return True
        return False
# @lc code=end
