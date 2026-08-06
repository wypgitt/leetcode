#
# @lc app=leetcode id=3956 lang=python3
#
# [3956] Maximum Sum of M Non-Overlapping Subarrays I
#
# https://leetcode.com/problems/maximum-sum-of-m-non-overlapping-subarrays-i/description/
#
# algorithms
# Hard (26.81%)
# Likes:    84
# Dislikes: 6
# Total Accepted:    8.5K
# Total Submissions: 31.6K
# Testcase Example:  "[4,1,-5,2]\n2\n1\n3"
#
#
# You are given an integer array nums of length n, and three integers m,
# l, and r.
#
# Your task is to select at least one and at most m non-overlapping
# subarrays from nums such that:
#
# Each selected subarray has a length between [l, r] (inclusive).
#
# The total sum of all selected subarrays is maximized.
#
# Return the maximum total sum you can achieve.
#
# Example 1:
#
# Input: nums = [4,1,-5,2], m = 2, l = 1, r = 3
#
# Output: 7
#
# Explanation:
#
# One optimal strategy is to:
#
# Select the subarray [4, 1] with sum 4 + 1 = 5 and the subarray [2] with
# sum 2. Both subarrays have length between [l, r].
#
# The total sum of these subarrays is 5 + 2 = 7, which is the maximum
# achievable sum with at most m = 2 subarrays.
#
# Example 2:
#
# Input: nums = [1,0,3,4], m = 2, l = 1, r = 2
#
# Output: 8
#
# Explanation:
#
# One optimal strategy is to:
#
# Select the subarray [1] with sum 1 and the subarray [3, 4] with sum 3 +
# 4 = 7. Both subarrays have length between [l, r].
#
# The total sum of these subarrays is 1 + 7 = 8, which is the maximum
# achievable sum with at most m = 2 subarrays.
#
# Example 3:
#
# Input: nums = [-1,7,-4], m = 1, l = 2, r = 3
#
# Output: 6
#
# Explanation:
#
# Select the subarray [-1, 7] from nums which has length between [l, r].
#
# The total sum of this subarray is -1 + 7 = 6, which is the maximum
# achievable sum with at most m = 1 subarray.
#
# Example 4:
#
# Input: nums = [-3,-4,-1], m = 2, l = 1, r = 2
#
# Output: -1
#
# Explanation:
#
# All subarrays of nums have negative sums. The optimal strategy is to
# select the subarray [-1], which has length between [l, r].
#
# The total sum of this subarray is -1, which is the maximum achievable
# sum with at most m = 2 subarrays.
#
# Constraints:
#
# 1 <= n == nums.length <= 1000
#
# -10^9 <= nums[i] <= 10^9​​​​​​​
#
# 1 <= m <= n
#
# 1 <= l <= r <= n
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def maximumSum(self, nums: List[int], m: int, l: int, r: int) -> int:
        """
        Interview explanation:
        Pick 1..m non-overlapping subarrays of length in [l,r] maximizing sum.
        DP over suffix with sliding-window maximum transitions.

        Algorithm:
        - psum prefix sums; dp[t][i] = best using t segments on suffix i..n-1.
        - Transition: skip i, or take a segment starting at i of length ∈[l,r]
          via a monoqueue over psum[j]-psum[i]+dp[t-1][j].
        - If all-negative (best stays 0), fall back to the best single segment.

        Complexity: O(n·m) time, O(n·m) space.
        """
        n = len(nums)
        psum = [0] * (n + 1)
        for i in range(n):
            psum[i + 1] = psum[i] + nums[i]

        dp = [[0] * (n + 1) for _ in range(m + 1)]
        result = -10**30

        for t in range(1, m + 1):
            dq = deque()
            for i in range(n - 1, -1, -1):
                if i + l <= n:
                    curr = psum[i + l] - psum[i] + dp[t - 1][i + l]
                    while dq and dq[0] > i + r:
                        dq.popleft()
                    while dq:
                        idx = dq[-1]
                        top = psum[idx] - psum[i] + dp[t - 1][idx]
                        if top > curr:
                            break
                        dq.pop()
                    dq.append(i + l)
                dp[t][i] = dp[t][i + 1]
                if dq:
                    idx = dq[0]
                    dp[t][i] = max(dp[t][i], psum[idx] - psum[i] + dp[t - 1][idx])
            result = max(result, dp[t][0])

        if result == 0:
            ans = -10**30
            for i in range(n):
                for size in range(l, r + 1):
                    if i + size <= n:
                        ans = max(ans, psum[i + size] - psum[i])
            return ans
        return result
# @lc code=end
