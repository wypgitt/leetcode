#
# @lc app=leetcode id=3929 lang=python3
#
# [3929] Minimum Partition Score II
#
# https://leetcode.com/problems/minimum-partition-score-ii/description/
#
# algorithms
# Hard (44.88%)
# Likes:    0
# Dislikes: 0
# Total Accepted:    127
# Total Submissions: 283
# Testcase Example:  "[5,1,2,1]\n2"
#
#
# You are given an integer array nums and an integer k.
#
# Your task is to partition nums into exactly k subarrays and return an
# integer denoting the minimum possible score among all valid partitions.
#
# The score of a partition is the sum of the values of all its subarrays.
#
# The value of a subarray is defined as sumArr * (sumArr + 1) / 2, where
# sumArr is the sum of its elements.
#
# Example 1:
#
# Input: nums = [5,1,2,1], k = 2
#
# Output: 25
#
# Explanation:
#
# We must partition the array into k = 2 subarrays. One optimal partition
# is [5] and [1, 2, 1].
#
# The first subarray has sum = 5 and value = 5 * 6 / 2 = 15.
#
# The second subarray has sum = 1 + 2 + 1 = 4 and value = 4 * 5 / 2 = 10.
#
# The score of this partition is 15 + 10 = 25, which is the minimum
# possible score.
#
# Example 2:
#
# Input: nums = [1,2,3,4], k = 1
#
# Output: 55
#
# Explanation:
#
# Since we must partition the array into k = 1 subarray, all elements
# belong to the same subarray: [1, 2, 3, 4].
#
# This subarray has sum = 1 + 2 + 3 + 4 = 10 and value = 10 * 11 / 2 =
# 55.​​​​​​​
#
# The score of this partition is 55, which is the minimum possible score.
#
# Example 3:
#
# Input: nums = [1,1,1], k = 3
#
# Output: 3
#
# Explanation:
#
# We must partition the array into k = 3 subarrays. The only valid
# partition is [1], [1], [1].
#
# Each subarray has sum = 1 and value = 1 * 2 / 2 = 1.
#
# The score of this partition is 1 + 1 + 1 = 3, which is the minimum
# possible score.
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# 1 <= nums[i] <= 10^3
#
# 1 <= k <= nums.length
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def minPartitionScore(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Score = sum S*(S+1)/2 over contiguous parts. With fixed total sum this
        equals minimizing sum of squared part sums. Use WQS (Aliens) binary
        search on a per-part penalty plus Convex Hull Trick for the DP.

        Algorithm:
        - prefix sums; cost of [j..i) is S*(S+1)/2.
        - For penalty λ, CHT-DP computes min (score + λ * parts) and part count.
        - Binary search smallest λ with parts <= k; answer is f(λ) - k*λ.

        Complexity: O(n log (n * maxA)) time, O(n) space.
        """
        def cross_bad(l1, l2, l3) -> bool:
            return (l2[1] - l1[1]) * (l2[0] - l3[0]) < (l3[1] - l2[1]) * (l1[0] - l2[0])

        n = len(nums)
        prefix = [0] * (n + 1)
        for i, x in enumerate(nums):
            prefix[i + 1] = prefix[i] + x

        def max_lambda() -> int:
            total = prefix[-1] * (prefix[-1] + 1) // 2
            mx = 0
            for i in range(1, n):
                c1, c2 = prefix[i], prefix[-1] - prefix[i]
                mx = max(mx, total - (c1 * (c1 + 1) // 2 + c2 * (c2 + 1) // 2))
            return mx

        def f(lam: int):
            dp = cnt = 0
            hull = deque([(0, 0, 0)])
            for i in range(n):
                x = prefix[i + 1]
                while len(hull) >= 2 and hull[0][0] * x + hull[0][1] > hull[1][0] * x + hull[1][1]:
                    hull.popleft()
                dp = hull[0][0] * x + hull[0][1] + (x * x + x) // 2 + lam
                cnt = hull[0][2] + 1
                line = (-x, dp + (x * x - x) // 2, cnt)
                while len(hull) >= 2 and not cross_bad(hull[-2], hull[-1], line):
                    hull.pop()
                hull.append(line)
            return dp, cnt

        mx = max_lambda()
        lo, hi = 0, mx
        while lo <= hi:
            mid = (lo + hi) // 2
            if f(mid)[1] <= k:
                hi = mid - 1
            else:
                lo = mid + 1
        return f(lo)[0] - k * lo
# @lc code=end
