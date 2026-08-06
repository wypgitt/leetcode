#
# @lc app=leetcode id=3676 lang=python3
#
# [3676] Count Bowl Subarrays
#
# https://leetcode.com/problems/count-bowl-subarrays/description/
#
# algorithms
# Medium (48.69%)
# Likes:    198
# Dislikes: 5
# Total Accepted:    31.5K
# Total Submissions: 64.6K
# Testcase Example:  "[2,5,3,1,4]"
#
#
# You are given an integer array nums with distinct elements.
#
# A subarray nums[l...r] of nums is called a bowl if:
#
# The subarray has length at least 3. That is, r - l + 1 >= 3.
#
# The minimum of its two ends is strictly greater than the maximum of all
# elements in between. That is, min(nums[l], nums[r]) > max(nums[l + 1],
# ..., nums[r - 1]).
#
# Return the number of bowl subarrays in nums.
#
# Example 1:
#
# Input: nums = [2,5,3,1,4]
#
# Output: 2
#
# Explanation:
#
# The bowl subarrays are [3, 1, 4] and [5, 3, 1, 4].
#
# [3, 1, 4] is a bowl because min(3, 4) = 3 > max(1) = 1.
#
# [5, 3, 1, 4] is a bowl because min(5, 4) = 4 > max(3, 1) = 3.
#
# Example 2:
#
# Input: nums = [5,1,2,3,4]
#
# Output: 3
#
# Explanation:
#
# The bowl subarrays are [5, 1, 2], [5, 1, 2, 3] and [5, 1, 2, 3, 4].
#
# Example 3:
#
# Input: nums = [1000000000,999999999,999999998]
#
# Output: 0
#
# Explanation:
#
# No subarray is a bowl.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# nums consists of distinct elements.
#

# @lc code=start
from typing import List


class Solution:
    def bowlSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A bowl is determined by a pair of ends taller than everything between.
        A decreasing monotonic stack discovers each such pair exactly once:
        when a new right end pops an interior maximum, the new stack top and
        current index form a bowl (length ≥ 3).

        Algorithm:
        - Maintain indices with decreasing values.
        - For each i, while top < nums[i], pop; if stack still nonempty, count++.
        - Push i.

        Complexity: O(n) time, O(n) space.
        """
        ans = 0
        stk: List[int] = []
        for i, v in enumerate(nums):
            while stk and nums[stk[-1]] < v:
                stk.pop()
                if stk:
                    ans += 1
            stk.append(i)
        return ans
# @lc code=end
