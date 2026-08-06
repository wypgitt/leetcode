#
# @lc app=leetcode id=3830 lang=python3
#
# [3830] Longest Alternating Subarray After Removing At Most One Element
#
# https://leetcode.com/problems/longest-alternating-subarray-after-removing-at-most-one-element/description/
#
# algorithms
# Hard (31.59%)
# Likes:    77
# Dislikes: 1
# Total Accepted:    8.5K
# Total Submissions: 27K
# Testcase Example:  "[2,1,3,2]"
#
#
# You are given an integer array nums.
#
# A subarray nums[l..r] is alternating if one of the following holds:
#
# nums[l] < nums[l + 1] > nums[l + 2] < nums[l + 3] > ...
#
# nums[l] > nums[l + 1] < nums[l + 2] > nums[l + 3] < ...
#
# In other words, if we compare adjacent elements in the subarray, then
# the comparisons alternate between strictly greater and strictly smaller.
#
# You can remove at most one element from nums. Then, you select an
# alternating subarray from nums.
#
# Return an integer denoting the maximum length of the alternating
# subarray you can select.
#
# A subarray of length 1 is considered alternating.
#
# Example 1:
#
# Input: nums = [2,1,3,2]
#
# Output: 4
#
# Explanation:
#
# Choose not to remove elements.
#
# Select the entire array [2, 1, 3, 2], which is alternating because 2 > 1
# < 3 > 2.
#
# Example 2:
#
# Input: nums = [3,2,1,2,3,2,1]
#
# Output: 4
#
# Explanation:
#
# Choose to remove nums[3] i.e., [3, 2, 1, 2, 3, 2, 1]. The array becomes
# [3, 2, 1, 3, 2, 1].
#
# Select the subarray [3, 2, 1, 3, 2, 1].
#
# Example 3:
#
# Input: nums = [100000,100000]
#
# Output: 1
#
# Explanation:
#
# Choose not to remove elements.
#
# Select the subarray [100000, 100000].
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def longestAlternating(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Maximize length of an alternating (<>< or ><>) subarray after deleting
        at most one element from the array.

        Algorithm:
        - Precompute adjacent comparison signs and longest alternating lengths
          ending at / starting at each index with no deletion.
        - Answer is at least the no-deletion max.
        - For each removable middle index, bridge neighbors and join left/right
          alternating runs when signs continue to alternate.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)

        sign = [self._cmp(nums[i], nums[i + 1]) for i in range(n - 1)]

        end_len = [1] * n
        for i in range(1, n):
            if sign[i - 1] == 0:
                end_len[i] = 1
            elif i >= 2 and sign[i - 2] == -sign[i - 1]:
                end_len[i] = end_len[i - 1] + 1
            else:
                end_len[i] = 2

        start_len = [1] * n
        for i in range(n - 2, -1, -1):
            if sign[i] == 0:
                start_len[i] = 1
            elif i + 2 < n and sign[i] == -sign[i + 1]:
                start_len[i] = start_len[i + 1] + 1
            else:
                start_len[i] = 2

        ans = max(end_len)

        for removed in range(1, n - 1):
            bridge = self._cmp(nums[removed - 1], nums[removed + 1])
            if bridge == 0:
                continue

            if removed >= 2 and sign[removed - 2] == -bridge:
                left = end_len[removed - 1]
            else:
                left = 1

            if removed + 1 <= n - 2 and sign[removed + 1] == -bridge:
                right = start_len[removed + 1]
            else:
                right = 1

            ans = max(ans, left + right)

        return ans

    def _cmp(self, a: int, b: int) -> int:
        if a < b:
            return 1
        if a > b:
            return -1
        return 0
# @lc code=end
