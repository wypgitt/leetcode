#
# @lc app=leetcode id=3555 lang=python3
#
# [3555] Smallest Subarray to Sort in Every Sliding Window
#
# https://leetcode.com/problems/smallest-subarray-to-sort-in-every-sliding-window/description/
#
# algorithms
# Medium (58.59%)
# Likes:    7
# Dislikes: 1
# Total Accepted:    849
# Total Submissions: 1.4K
# Testcase Example:  "[1,3,2,4,5]\n3"
#
#
# You are given an integer array nums and an integer k.
#
# For each contiguous subarray of length k, determine the minimum length
# of a continuous segment that must be sorted so that the entire window
# becomes non‑decreasing; if the window is already sorted, its required
# length is zero.
#
# Return an array of length n − k + 1 where each element corresponds to
# the answer for its window.
#
# Example 1:
#
# Input: nums = [1,3,2,4,5], k = 3
#
# Output: [2,2,0]
#
# Explanation:
#
# nums[0...2] = [1, 3, 2]. Sort [3, 2] to get [1, 2, 3], the answer is 2.
#
# nums[1...3] = [3, 2, 4]. Sort [3, 2] to get [2, 3, 4], the answer is 2.
#
# nums[2...4] = [2, 4, 5] is already sorted, so the answer is 0.
#
# Example 2:
#
# Input: nums = [5,4,3,2,1], k = 4
#
# Output: [4,4]
#
# Explanation:
#
# nums[0...3] = [5, 4, 3, 2]. The whole subarray must be sorted, so the
# answer is 4.
#
# nums[1...4] = [4, 3, 2, 1]. The whole subarray must be sorted, so the
# answer is 4.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= k <= nums.length
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def minSubarraySort(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        For a window, the shortest segment that must be sorted is the span of
        positions that differ from the sorted window (classic "shortest unsorted
        continuous subarray" on each window).

        Algorithm:
        - For each window of length k, compare with its sorted copy.
        - Find leftmost/rightmost mismatch; length is 0 if already sorted.

        Alternate: two monotonic stacks per window for O(k) without full sort.
        Complexity: O((n - k + 1) * k log k) time, O(k) space.
        """
        n = len(nums)
        ans = []
        for i in range(n - k + 1):
            w = nums[i : i + k]
            s = sorted(w)
            if w == s:
                ans.append(0)
                continue
            left = 0
            while w[left] == s[left]:
                left += 1
            right = k - 1
            while w[right] == s[right]:
                right -= 1
            ans.append(right - left + 1)
        return ans
# @lc code=end
