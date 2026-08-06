#
# @lc app=leetcode id=3583 lang=python3
#
# [3583] Count Special Triplets
#
# https://leetcode.com/problems/count-special-triplets/description/
#
# algorithms
# Medium (47.10%)
# Likes:    563
# Dislikes: 23
# Total Accepted:    120K
# Total Submissions: 254.9K
# Testcase Example:  "[6,3,6]"
#
#
# You are given an integer array nums.
#
# A special triplet is defined as a triplet of indices (i, j, k) such
# that:
#
# 0 <= i < j < k < n, where n = nums.length
#
# nums[i] == nums[j] * 2
#
# nums[k] == nums[j] * 2
#
# Return the total number of special triplets in the array.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [6,3,6]
#
# Output: 1
#
# Explanation:
#
# The only special triplet is (i, j, k) = (0, 1, 2), where:
#
# nums[0] = 6, nums[1] = 3, nums[2] = 6
#
# nums[0] = nums[1] * 2 = 3 * 2 = 6
#
# nums[2] = nums[1] * 2 = 3 * 2 = 6
#
# Example 2:
#
# Input: nums = [0,1,0,0]
#
# Output: 1
#
# Explanation:
#
# The only special triplet is (i, j, k) = (0, 2, 3), where:
#
# nums[0] = 0, nums[2] = 0, nums[3] = 0
#
# nums[0] = nums[2] * 2 = 0 * 2 = 0
#
# nums[3] = nums[2] * 2 = 0 * 2 = 0
#
# Example 3:
#
# Input: nums = [8,4,2,8,4]
#
# Output: 2
#
# Explanation:
#
# There are exactly two special triplets:
#
# (i, j, k) = (0, 1, 3)
#
# nums[0] = 8, nums[1] = 4, nums[3] = 8
#
# nums[0] = nums[1] * 2 = 4 * 2 = 8
#
# nums[3] = nums[1] * 2 = 4 * 2 = 8
#
# (i, j, k) = (1, 2, 4)
#
# nums[1] = 4, nums[2] = 2, nums[4] = 4
#
# nums[1] = nums[2] * 2 = 2 * 2 = 4
#
# nums[4] = nums[2] * 2 = 2 * 2 = 4
#
# Constraints:
#
# 3 <= n == nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def specialTriplets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count i < j < k with nums[i] = nums[k] = 2 * nums[j]. Fix j and multiply
        left/right frequencies of 2*nums[j].

        Algorithm:
        - Build right frequency map; scan j left-to-right moving counts.
        - For each j add left[2x] * right[2x] (mod 1e9+7), then move j into left.

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        right: dict[int, int] = defaultdict(int)
        for x in nums:
            right[x] += 1
        left: dict[int, int] = defaultdict(int)
        ans = 0
        for x in nums:
            right[x] -= 1
            target = x * 2
            ans = (ans + left[target] * right[target]) % MOD
            left[x] += 1
        return ans

    def specialTriplets_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: online DP — count of values seen, then count of middles that
        already have a matching left double.

        Algorithm:
        - dp0[x]: count of x so far; dp1[x]: ways to form (i,j) ending at x as j.
        - When seeing x, add dp1[x/2] if even; update dp1[x] from dp0[2x].

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        dp0: dict[int, int] = defaultdict(int)
        dp1: dict[int, int] = defaultdict(int)
        ans = 0
        for x in nums:
            if x % 2 == 0:
                ans = (ans + dp1[x // 2]) % MOD
            dp1[x] = (dp1[x] + dp0[2 * x]) % MOD
            dp0[x] = (dp0[x] + 1) % MOD
        return ans
# @lc code=end
