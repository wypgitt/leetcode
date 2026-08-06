#
# @lc app=leetcode id=3640 lang=python3
#
# [3640] Trionic Array II
#
# https://leetcode.com/problems/trionic-array-ii/description/
#
# algorithms
# Hard (47.35%)
# Likes:    394
# Dislikes: 39
# Total Accepted:    86.1K
# Total Submissions: 181.9K
# Testcase Example:  "[0,-2,-1,-3,0,2,-1]"
#
#
# You are given an integer array nums of length n.
#
# A trionic subarray is a contiguous subarray nums[l...r] (with 0 <= l < r
# < n) for which there exist indices l < p < q < r such that:
#
# nums[l...p] is strictly increasing,
#
# nums[p...q] is strictly decreasing,
#
# nums[q...r] is strictly increasing.
#
# Return the maximum sum of any trionic subarray in nums.
#
# Example 1:
#
# Input: nums = [0,-2,-1,-3,0,2,-1]
#
# Output: -4
#
# Explanation:
#
# Pick l = 1, p = 2, q = 3, r = 5:
#
# nums[l...p] = nums[1...2] = [-2, -1] is strictly increasing (-2 < -1).
#
# nums[p...q] = nums[2...3] = [-1, -3] is strictly decreasing (-1 > -3)
#
# nums[q...r] = nums[3...5] = [-3, 0, 2] is strictly increasing (-3 < 0 <
# 2).
#
# Sum = (-2) + (-1) + (-3) + 0 + 2 = -4.
#
# Example 2:
#
# Input: nums = [1,4,2,7]
#
# Output: 14
#
# Explanation:
#
# Pick l = 0, p = 1, q = 2, r = 3:
#
# nums[l...p] = nums[0...1] = [1, 4] is strictly increasing (1 < 4).
#
# nums[p...q] = nums[1...2] = [4, 2] is strictly decreasing (4 > 2).
#
# nums[q...r] = nums[2...3] = [2, 7] is strictly increasing (2 < 7).
#
# Sum = 1 + 4 + 2 + 7 = 14.
#
# Constraints:
#
# 4 <= n = nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#
# It is guaranteed that at least one trionic subarray exists.
#

# @lc code=start

from typing import List


class Solution:
    def maxSumTrionic(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Maximize sum of a trionic subarray (up, down, up). Expand a candidate
        window while tracking peak p and valley q; shrink from the left past
        the valley and drop leading negatives before the peak.

        Algorithm:
        - Maintain prefix sum of [left, right].
        - On a descent after an ascent, set peak p; shrink left while left<q
          or leading nums[left]<0 with room before p.
        - On an ascent after a descent, set valley q; if left!=p update answer.
        - Equal adjacent values reset the window.

        Complexity: O(n) time, O(1) space.
        """
        ans = float("-inf")
        left = p = q = 0
        prefix = nums[0]
        for right in range(1, len(nums)):
            prefix += nums[right]
            if nums[right - 1] > nums[right]:
                if right >= 2 and nums[right - 2] < nums[right - 1]:
                    p = right - 1
                while left < q or (nums[left] < 0 and left + 1 < p):
                    prefix -= nums[left]
                    left += 1
            elif nums[right - 1] < nums[right]:
                if right >= 2 and nums[right - 2] > nums[right - 1]:
                    q = right - 1
                if left != p:
                    ans = max(ans, prefix)
            else:
                left = p = q = right
                prefix = nums[right]
        return int(ans)
# @lc code=end

