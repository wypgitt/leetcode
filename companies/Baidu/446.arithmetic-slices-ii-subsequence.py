#
# @lc app=leetcode id=446 lang=python3
#
# [446] Arithmetic Slices II - Subsequence
#
# https://leetcode.com/problems/arithmetic-slices-ii-subsequence/description/
#
# algorithms
# Hard (55.18%)
# Likes:    3535
# Dislikes: 165
# Total Accepted:    173K
# Total Submissions: 313K
# Testcase Example:  "[2,4,6,8,10]"
#
# Given an integer array nums, return the number of all the arithmetic
# subsequences of nums.
#
# A sequence of numbers is called arithmetic if it consists of at least three
# elements and if the difference between any two consecutive elements is the
# same.
#
# For example, [1, 3, 5, 7, 9], [7, 7, 7, 7], and [3, -1, -5, -9] are
# arithmetic sequences.
#
# For example, [1, 1, 2, 5, 7] is not an arithmetic sequence.
#
# A subsequence of an array is a sequence that can be formed by removing some
# elements (possibly none) of the array.
#
# For example, [2,5,10] is a subsequence of [1,2,1,2,4,1,5,10].
#
# The test cases are generated so that the answer fits in 32-bit integer.
#
# Example 1:
#
# Input: nums = [2,4,6,8,10]
# Output: 7
# Explanation: All arithmetic subsequence slices are:
# [2,4,6]
# [4,6,8]
# [6,8,10]
# [2,4,6,8]
# [4,6,8,10]
# [2,4,6,8,10]
# [2,6,10]
#
# Example 2:
#
# Input: nums = [7,7,7,7,7]
# Output: 16
# Explanation: Any subsequence of this array is arithmetic.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# -2^31 <= nums[i] <= 2^31 - 1
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def numberOfArithmeticSlices(self, nums: List[int]) -> int:
        """
        Interview explanation:
        DP on subsequences: dp[i][d] = number of arithmetic subsequences of
        length ≥2 ending at i with difference d. When we extend from j to i
        with d=nums[i]-nums[j], we add dp[j][d] new weak subsequences and
        contribute dp[j][d] to the answer (those become length ≥3).

        Algorithm:
        - dp = list of dicts; for i, for j<i: d=nums[i]-nums[j];
          cnt=dp[j][d]; ans+=cnt; dp[i][d]+=cnt+1.

        Complexity: O(n^2) time, O(n^2) space.
        """
        n = len(nums)
        dp = [defaultdict(int) for _ in range(n)]
        ans = 0
        for i in range(n):
            for j in range(i):
                d = nums[i] - nums[j]
                cnt = dp[j][d]
                ans += cnt
                dp[i][d] += cnt + 1
        return ans
# @lc code=end
