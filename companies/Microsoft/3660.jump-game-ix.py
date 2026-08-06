#
# @lc app=leetcode id=3660 lang=python3
#
# [3660] Jump Game IX
#
# https://leetcode.com/problems/jump-game-ix/description/
#
# algorithms
# Medium (46.32%)
# Likes:    458
# Dislikes: 39
# Total Accepted:    85.8K
# Total Submissions: 185.1K
# Testcase Example:  "[2,1,3]"
#
#
# You are given an integer array nums.
#
# From any index i, you can jump to another index j under the following
# rules:
#
# Jump to index j where j > i is allowed only if nums[j] < nums[i].
#
# Jump to index j where j < i is allowed only if nums[j] > nums[i].
#
# For each index i, find the maximum value in nums that can be reached by
# following any sequence of valid jumps starting at i.
#
# Return an array ans where ans[i] is the maximum value reachable starting
# from index i.
#
# Example 1:
#
# Input: nums = [2,1,3]
#
# Output: [2,2,3]
#
# Explanation:
#
# For i = 0: No jump increases the value.
#
# For i = 1: Jump to j = 0 as nums[j] = 2 is greater than nums[i].
#
# For i = 2: Since nums[2] = 3 is the maximum value in nums, no jump
# increases the value.
#
# Thus, ans = [2, 2, 3].
#
# Example 2:
#
# Input: nums = [2,3,1]
#
# Output: [3,3,3]
#
# Explanation:
#
# For i = 0: Jump forward to j = 2 as nums[j] = 1 is less than nums[i] =
# 2, then from i = 2 jump to j = 1 as nums[j] = 3 is greater than nums[2].
#
# For i = 1: Since nums[1] = 3 is the maximum value in nums, no jump
# increases the value.
#
# For i = 2: Jump to j = 1 as nums[j] = 3 is greater than nums[2] = 1.
#
# Thus, ans = [3, 3, 3].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9​​​​​​​
#

# @lc code=start
from typing import List


class Solution:
    def maxValue(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Right jumps need a smaller value; left jumps need a larger one —
        connected segments share the same reachable prefix maximum.

        Algorithm:
        - Build prefix maxima.
        - From the right, grow a segment while pref_max[j] > segment_min;
          assign the segment max to every index in it.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        pref_max = nums[:]
        for i in range(1, n):
            pref_max[i] = max(pref_max[i - 1], nums[i])
        ans = [0] * n
        i = n - 1
        while i >= 0:
            j = i
            min_val = nums[i]
            max_val = pref_max[i]
            j -= 1
            while j >= 0 and pref_max[j] > min_val:
                min_val = min(min_val, nums[j])
                max_val = max(max_val, pref_max[j])
                j -= 1
            for k in range(j + 1, i + 1):
                ans[k] = max_val
            i = j
        return ans
# @lc code=end

