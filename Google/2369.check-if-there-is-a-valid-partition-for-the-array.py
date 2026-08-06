#
# @lc app=leetcode id=2369 lang=python3
#
# [2369] Check if There is a Valid Partition For The Array
#
# https://leetcode.com/problems/check-if-there-is-a-valid-partition-for-the-array/description/
#
# algorithms
# Medium (52.46%)
# Likes:    2084
# Dislikes: 208
# Total Accepted:    104.3K
# Total Submissions: 198.8K
# Testcase Example:  "[4,4,4,5,6]"
#
# You are given a 0-indexed integer array nums. You have to partition the array
# into one or more contiguous subarrays.
#
# We call a partition of the array valid if each of the obtained subarrays
# satisfies one of the following conditions:
#
#
# The subarray consists of exactly 2, equal elements. For example, the subarray
# [2,2] is good.
#
#
# The subarray consists of exactly 3, equal elements. For example, the subarray
# [4,4,4] is good.
#
#
# The subarray consists of exactly 3 consecutive increasing elements, that is,
# the difference between adjacent elements is 1. For example, the subarray
# [3,4,5] is good, but the subarray [1,3,5] is not.
#
# Return true if the array has at least one valid partition. Otherwise, return
# false.
#
#
#
# Example 1:
#
# Input: nums = [4,4,4,5,6]
# Output: true
# Explanation: The array can be partitioned into the subarrays [4,4] and
# [4,5,6].
# This partition is valid, so we return true.
#
# Example 2:
#
# Input: nums = [1,1,1,2]
# Output: false
# Explanation: There is no valid partition for this array.
#
#
#
# Constraints:
#
#
# 2 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start

from typing import List


class Solution:
    def validPartition(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Valid partition: subarrays of form [x,x], [x,x,x], or [x,x+1,x+2].
        Check if whole array can be partitioned.

        Algorithm:
        - DP: dp[i] = can partition prefix nums[:i]. Transitions of length 2/3.

        Complexity: O(n) time, O(n) space (or O(1) rolling).
        """
        n = len(nums)
        dp = [False] * (n + 1)
        dp[0] = True
        for i in range(2, n + 1):
            if dp[i - 2] and nums[i - 1] == nums[i - 2]:
                dp[i] = True
            if i >= 3 and dp[i - 3]:
                a, b, c = nums[i - 3], nums[i - 2], nums[i - 1]
                if a == b == c or (b == a + 1 and c == a + 2):
                    dp[i] = True
        return dp[n]

    def validPartition_rolling(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: O(1) space rolling DP of last three states.

        Algorithm:
        - Keep dp0,dp1,dp2 for i-3,i-2,i-1.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        # d[j] = valid for prefix length j; need j-2 and j-3
        prev3 = True  # dp[0]
        prev2 = False  # dp[1]
        prev1 = n >= 2 and nums[0] == nums[1]  # dp[2]
        if n == 2:
            return prev1
        for i in range(3, n + 1):
            cur = False
            if prev2 and nums[i - 1] == nums[i - 2]:
                cur = True
            if prev3:
                a, b, c = nums[i - 3], nums[i - 2], nums[i - 1]
                if a == b == c or (b == a + 1 and c == a + 2):
                    cur = True
            prev3, prev2, prev1 = prev2, prev1, cur
        return prev1
# @lc code=end
