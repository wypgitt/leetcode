#
# @lc app=leetcode id=3578 lang=python3
#
# [3578] Count Partitions With Max-Min Difference at Most K
#
# https://leetcode.com/problems/count-partitions-with-max-min-difference-at-most-k/description/
#
# algorithms
# Medium (58.40%)
# Likes:    538
# Dislikes: 138
# Total Accepted:    66.9K
# Total Submissions: 114.6K
# Testcase Example:  "[9,4,1,3,7]\n4"
#
#
# You are given an integer array nums and an integer k. Your task is to
# partition nums into one or more non-empty contiguous segments such that
# in each segment, the difference between its maximum and minimum elements
# is at most k.
#
# Return the total number of ways to partition nums under this condition.
#
# Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [9,4,1,3,7], k = 4
#
# Output: 6
#
# Explanation:
#
# There are 6 valid partitions where the difference between the maximum
# and minimum elements in each segment is at most k = 4:
#
# [[9], [4], [1], [3], [7]]
#
# [[9], [4], [1], [3, 7]]
#
# [[9], [4], [1, 3], [7]]
#
# [[9], [4, 1], [3], [7]]
#
# [[9], [4, 1], [3, 7]]
#
# [[9], [4, 1, 3], [7]]
#
# Example 2:
#
# Input: nums = [3,3,4], k = 0
#
# Output: 2
#
# Explanation:
#
# There are 2 valid partitions that satisfy the given conditions:
#
# [[3], [3], [4]]
#
# [[3, 3], [4]]
#
# Constraints:
#
# 2 <= nums.length <= 5 * 10^4
#
# 1 <= nums[i] <= 10^9
#
# 0 <= k <= 10^9
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def countPartitions(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        dp[i] = ways to partition the prefix nums[0:i]. A last segment
        nums[j:i] is valid iff max-min ≤ k. Sum dp[j] over the largest window
        of valid left endpoints j, maintained with mono deques + prefix sums.

        Algorithm:
        - dp[0]=1; sliding left L so nums[L:i] always has max-min ≤ k.
        - Mono deques track max/min indices; pref cumulative dp.
        - dp[i] = pref[i-1] - pref[L-1].

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        dp = [0] * (n + 1)
        dp[0] = 1
        pref = [0] * (n + 1)
        pref[0] = 1
        max_dq: deque[int] = deque()
        min_dq: deque[int] = deque()
        left = 0
        for i in range(n):
            while max_dq and nums[max_dq[-1]] <= nums[i]:
                max_dq.pop()
            max_dq.append(i)
            while min_dq and nums[min_dq[-1]] >= nums[i]:
                min_dq.pop()
            min_dq.append(i)
            while nums[max_dq[0]] - nums[min_dq[0]] > k:
                if max_dq[0] == left:
                    max_dq.popleft()
                if min_dq[0] == left:
                    min_dq.popleft()
                left += 1
            # valid last segment starts at indices in [left, i]
            # dp[i+1] = sum(dp[left] .. dp[i])
            total = pref[i] - (pref[left - 1] if left > 0 else 0)
            dp[i + 1] = total % MOD
            pref[i + 1] = (pref[i] + dp[i + 1]) % MOD
        return dp[n]
# @lc code=end
