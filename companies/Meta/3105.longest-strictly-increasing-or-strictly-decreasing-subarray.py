#
# @lc app=leetcode id=3105 lang=python3
#
# [3105] Longest Strictly Increasing or Strictly Decreasing Subarray
#
# https://leetcode.com/problems/longest-strictly-increasing-or-strictly-decreasing-subarray/description/
#
# algorithms
# Easy (64.93%)
# Likes:    669
# Dislikes: 35
# Total Accepted:    221.2K
# Total Submissions: 340.7K
# Testcase Example:  "[1,4,3,3,2]"
#
#
# You are given an array of integers nums. Return the length of the
# longest subarray of nums which is either strictly increasing or strictly
# decreasing.
#
# Example 1:
#
# Input: nums = [1,4,3,3,2]
#
# Output: 2
#
# Explanation:
#
# The strictly increasing subarrays of nums are [1], [2], [3], [3], [4],
# and [1,4].
#
# The strictly decreasing subarrays of nums are [1], [2], [3], [3], [4],
# [3,2], and [4,3].
#
# Hence, we return 2.
#
# Example 2:
#
# Input: nums = [3,3,3,3]
#
# Output: 1
#
# Explanation:
#
# The strictly increasing subarrays of nums are [3], [3], [3], and [3].
#
# The strictly decreasing subarrays of nums are [3], [3], [3], and [3].
#
# Hence, we return 1.
#
# Example 3:
#
# Input: nums = [3,2,1]
#
# Output: 3
#
# Explanation:
#
# The strictly increasing subarrays of nums are [3], [2], and [1].
#
# The strictly decreasing subarrays of nums are [3], [2], [1], [3,2],
# [2,1], and [3,2,1].
#
# Hence, we return 3.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 1 <= nums[i] <= 50
#

# @lc code=start
from typing import List


class Solution:
    def longestMonotonicSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Longest contiguous run that is strictly increasing or strictly decreasing.

        Algorithm:
        - Track current increasing / decreasing streak lengths in one pass.
        - Equal neighbors reset both streaks to 1.

        Complexity: O(n) time, O(1) space.
        """
        ans = inc = dec = 1
        for i in range(1, len(nums)):
            if nums[i] > nums[i - 1]:
                inc += 1
                dec = 1
            elif nums[i] < nums[i - 1]:
                dec += 1
                inc = 1
            else:
                inc = dec = 1
            ans = max(ans, inc, dec)
        return ans

    def longestMonotonicSubarray_two_passes(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same answer via separate increasing and decreasing scans.

        Algorithm:
        - Scan once for max strict-inc run; once for max strict-dec run; take max.

        Complexity: O(n) time, O(1) space.
        """
        def longest(cmp) -> int:
            best = cur = 1
            for i in range(1, len(nums)):
                if cmp(nums[i], nums[i - 1]):
                    cur += 1
                    best = max(best, cur)
                else:
                    cur = 1
            return best

        return max(longest(lambda a, b: a > b), longest(lambda a, b: a < b))
# @lc code=end
