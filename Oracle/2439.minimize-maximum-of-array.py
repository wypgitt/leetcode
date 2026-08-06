#
# @lc app=leetcode id=2439 lang=python3
#
# [2439] Minimize Maximum of Array
#
# https://leetcode.com/problems/minimize-maximum-of-array/description/
#
# algorithms
# Medium (46.58%)
# Likes:    2613
# Dislikes: 647
# Total Accepted:    102.5K
# Total Submissions: 220K
# Testcase Example:  "[3,7,1,6]"
#
# You are given a 0-indexed array nums comprising of n non-negative integers.
#
# In one operation, you must:
#
#
# Choose an integer i such that 1 <= i < n and nums[i] > 0.
#
#
# Decrease nums[i] by 1.
#
#
# Increase nums[i - 1] by 1.
#
# Return the minimum possible value of the maximum integer of nums after
# performing any number of operations.
#
#
#
# Example 1:
#
# Input: nums = [3,7,1,6]
# Output: 5
# Explanation:
# One set of optimal operations is as follows:
# 1. Choose i = 1, and nums becomes [4,6,1,6].
# 2. Choose i = 3, and nums becomes [4,6,2,5].
# 3. Choose i = 1, and nums becomes [5,5,2,5].
# The maximum integer of nums is 5. It can be shown that the maximum number
# cannot be less than 5.
# Therefore, we return 5.
#
# Example 2:
#
# Input: nums = [10,1]
# Output: 10
# Explanation:
# It is optimal to leave nums as is, and since 10 is the maximum value, we
# return 10.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 2 <= n <= 10^5
#
#
# 0 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List
import math


class Solution:
    def minimizeArrayValue(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Op: decrement nums[i], increment nums[i-1] (i>0). Minimize the final max.

        Algorithm:
        - Answer is max over i of ceil(prefix_sum[i]/(i+1)).

        Complexity: O(n) time, O(1) space.
        """
        ans = s = 0
        for i, x in enumerate(nums):
            s += x
            ans = max(ans, math.ceil(s / (i + 1)))
        return ans

    def minimizeArrayValue_binary_search(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate binary search on the maximum M.

        Algorithm:
        - Check prefix sums never exceed M*(i+1).

        Complexity: O(n log A) time, O(1) space.
        """
        lo, hi = 0, max(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            s = 0
            ok = True
            for i, x in enumerate(nums):
                s += x
                if s > mid * (i + 1):
                    ok = False
                    break
            if ok:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
