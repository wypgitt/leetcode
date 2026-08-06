#
# @lc app=leetcode id=3826 lang=python3
#
# [3826] Minimum Partition Score
#
# https://leetcode.com/problems/minimum-partition-score/description/
#
# algorithms
# Hard (33.89%)
# Likes:    56
# Dislikes: 4
# Total Accepted:    7.2K
# Total Submissions: 21.2K
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
# The first subarray has sumArr = 5 and value = 5 × 6 / 2 = 15.
#
# The second subarray has sumArr = 1 + 2 + 1 = 4 and value = 4 × 5 / 2 =
# 10.
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
# This subarray has sumArr = 1 + 2 + 3 + 4 = 10 and value = 10 × 11 / 2 =
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
# Each subarray has sumArr = 1 and value = 1 × 2 / 2 = 1.
#
# The score of this partition is 1 + 1 + 1 = 3, which is the minimum
# possible score.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^4
#
# 1 <= k <= nums.length
#

# @lc code=start
from typing import List, Tuple


class Solution:
    def minPartitionScore(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Partition into exactly k contiguous parts minimizing sum of
        s*(s+1)/2 over each part sum s. Equivalent to minimizing sum of s^2
        (plus a constant).

        Algorithm:
        - DP: dp[parts][i] = min cost to cover prefix i with `parts` segments.
        - Transition is convex: use Li Chao / convex hull of lines
          y = -2*pref[cut]*x + (dp[cut] + pref[cut]^2), evaluate at x = pref[i].
        - Convert final quadratic sum back via (dp + total_sum) // 2.

        Complexity: O(k n) time, O(n) space.
        """
        n = len(nums)
        prefix = [0] * (n + 1)
        for i, value in enumerate(nums, 1):
            prefix[i] = prefix[i - 1] + value

        inf = 10**60
        prev = [inf] * (n + 1)
        prev[0] = 0

        for parts in range(1, k + 1):
            cur = [inf] * (n + 1)
            hull: List[Tuple[int, int]] = []
            head = 0

            for i in range(parts, n + 1):
                cut = i - 1
                self._add_line(
                    hull,
                    -2 * prefix[cut],
                    prev[cut] + prefix[cut] * prefix[cut],
                )

                x = prefix[i]
                while head + 1 < len(hull) and self._value(hull[head + 1], x) <= self._value(hull[head], x):
                    head += 1

                cur[i] = x * x + self._value(hull[head], x)

            prev = cur

        return (prev[n] + prefix[n]) // 2

    def _add_line(self, hull: List[Tuple[int, int]], slope: int, intercept: int) -> None:
        line = (slope, intercept)
        while len(hull) >= 2 and self._is_bad(hull[-2], hull[-1], line):
            hull.pop()
        hull.append(line)

    def _is_bad(
        self,
        first: Tuple[int, int],
        second: Tuple[int, int],
        third: Tuple[int, int],
    ) -> bool:
        m1, b1 = first
        m2, b2 = second
        m3, b3 = third
        return (b2 - b1) * (m2 - m3) >= (b3 - b2) * (m1 - m2)

    def _value(self, line: Tuple[int, int], x: int) -> int:
        slope, intercept = line
        return slope * x + intercept
# @lc code=end
