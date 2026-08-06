#
# @lc app=leetcode id=3685 lang=python3
#
# [3685] Subsequence Sum After Capping Elements
#
# https://leetcode.com/problems/subsequence-sum-after-capping-elements/description/
#
# algorithms
# Medium (25.54%)
# Likes:    167
# Dislikes: 16
# Total Accepted:    20.8K
# Total Submissions: 81.6K
# Testcase Example:  "[4,3,2,4]\n5"
#
#
# You are given an integer array nums of size n and a positive integer k.
#
# An array capped by value x is obtained by replacing every element
# nums[i] with min(nums[i], x).
#
# For each integer x from 1 to n, determine whether it is possible to
# choose a subsequence from the array capped by x such that the sum of the
# chosen elements is exactly k.
#
# Return a 0-indexed boolean array answer of size n, where answer[i] is
# true if it is possible when using x = i + 1, and false otherwise.
#
# Example 1:
#
# Input: nums = [4,3,2,4], k = 5
#
# Output: [false,false,true,true]
#
# Explanation:
#
# For x = 1, the capped array is [1, 1, 1, 1]. Possible sums are 1, 2, 3,
# 4, so it is impossible to form a sum of 5.
#
# For x = 2, the capped array is [2, 2, 2, 2]. Possible sums are 2, 4, 6,
# 8, so it is impossible to form a sum of 5.
#
# For x = 3, the capped array is [3, 3, 2, 3]. A subsequence [2, 3] sums
# to 5, so it is possible.
#
# For x = 4, the capped array is [4, 3, 2, 4]. A subsequence [3, 2] sums
# to 5, so it is possible.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5], k = 3
#
# Output: [true,true,true,true,true]
#
# Explanation:
#
# For every value of x, it is always possible to select a subsequence from
# the capped array that sums exactly to 3.
#
# Constraints:
#
# 1 <= n == nums.length <= 4000
#
# 1 <= nums[i] <= n
#
# 1 <= k <= 4000
#

# @lc code=start

from typing import List


class Solution:
    def subsequenceSumAfterCapping(self, nums: List[int], k: int) -> List[bool]:
        """
        Interview explanation:
        Cap by x turns values >= x into x. Process x ascending: keep a 0-1
        knapsack of uncapped values (< x), and treat the rest as up to cnt
        copies of x.

        Algorithm:
        - Sort nums; maintain bool DP reachable sums from values already < x.
        - For each x = 1..n: add newly uncapped values (== x-1 boundary via
          nums[j] < x), then check whether some reachable s has
          (k - s) = q*x with 0 <= q <= count(nums >= x).

        Complexity: O(n * k) time and space.
        """
        n = len(nums)
        a = sorted(nums)
        dp = [False] * (k + 1)
        dp[0] = True
        ans = [False] * n
        j = 0
        for x in range(1, n + 1):
            while j < n and a[j] < x:
                v = a[j]
                for s in range(k, v - 1, -1):
                    if dp[s - v]:
                        dp[s] = True
                j += 1
            cnt = n - j
            ok = False
            for q in range(min(cnt, k // x) + 1):
                if dp[k - q * x]:
                    ok = True
                    break
            ans[x - 1] = ok
        return ans
# @lc code=end
