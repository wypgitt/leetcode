#
# @lc app=leetcode id=3505 lang=python3
#
# [3505] Minimum Operations to Make Elements Within K Subarrays Equal
#
# https://leetcode.com/problems/minimum-operations-to-make-elements-within-k-subarrays-equal/description/
#
# algorithms
# Hard (28.96%)
# Likes:    68
# Dislikes: 3
# Total Accepted:    4.6K
# Total Submissions: 16K
# Testcase Example:  "[5,-2,1,3,7,3,6,4,-1]\n3\n2"
#
#
# You are given an integer array nums and two integers, x and k. You can
# perform the following operation any number of times (including zero):
#
# Increase or decrease any element of nums by 1.
#
# Return the minimum number of operations needed to have at least k
# non-overlapping subarrays of size exactly x in nums, where all elements
# within each subarray are equal.
#
# Example 1:
#
# Input: nums = [5,-2,1,3,7,3,6,4,-1], x = 3, k = 2
#
# Output: 8
#
# Explanation:
#
# Use 3 operations to add 3 to nums[1] and use 2 operations to subtract 2
# from nums[3]. The resulting array is [5, 1, 1, 1, 7, 3, 6, 4, -1].
#
# Use 1 operation to add 1 to nums[5] and use 2 operations to subtract 2
# from nums[6]. The resulting array is [5, 1, 1, 1, 7, 4, 4, 4, -1].
#
# Now, all elements within each subarray [1, 1, 1] (from indices 1 to 3)
# and [4, 4, 4] (from indices 5 to 7) are equal. Since 8 total operations
# were used, 8 is the output.
#
# Example 2:
#
# Input: nums = [9,-2,-2,-2,1,5], x = 2, k = 2
#
# Output: 3
#
# Explanation:
#
# Use 3 operations to subtract 3 from nums[4]. The resulting array is [9,
# -2, -2, -2, -2, 5].
#
# Now, all elements within each subarray [-2, -2] (from indices 1 to 2)
# and [-2, -2] (from indices 3 to 4) are equal. Since 3 operations were
# used, 3 is the output.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# -10^6 <= nums[i] <= 10^6
#
# 2 <= x <= nums.length
#
# 1 <= k <= 15
#
# 2 <= k * x <= nums.length
#

# @lc code=start
from typing import List
from sortedcontainers import SortedList


class Solution:
    def minOperations(self, nums: List[int], x: int, k: int) -> int:
        """
        Interview explanation:
        Cost to equalize a length-x window is sum |a_i - median|. Precompute that
        cost for every window, then pick k non-overlapping windows with DP.

        Algorithm:
        - Sliding window with two SortedLists (lower/upper halves) + sums for
          O(log x) median cost updates.
        - dp[i][j] = min cost using prefix i with j windows; skip or take
          window starting at i.

        Complexity: O(n log x + n k) time, O(n k) space.
        """
        n = len(nums)
        costs = [0] * (n - x + 1)
        low = SortedList()
        high = SortedList()
        sum_low = sum_high = 0

        def balance() -> None:
            nonlocal sum_low, sum_high
            while len(low) < len(high):
                v = high.pop(0)
                sum_high -= v
                low.add(v)
                sum_low += v
            while len(low) > len(high) + 1:
                v = low.pop(-1)
                sum_low -= v
                high.add(v)
                sum_high += v

        def add(v: int) -> None:
            nonlocal sum_low, sum_high
            if not low or v <= low[-1]:
                low.add(v)
                sum_low += v
            else:
                high.add(v)
                sum_high += v
            balance()

        def remove(v: int) -> None:
            nonlocal sum_low, sum_high
            if low and v <= low[-1]:
                low.remove(v)
                sum_low -= v
            else:
                high.remove(v)
                sum_high -= v
            balance()

        def cost() -> int:
            med = low[-1]
            return med * len(low) - sum_low + sum_high - med * len(high)

        for i in range(n):
            add(nums[i])
            if i >= x:
                remove(nums[i - x])
            if i >= x - 1:
                costs[i - x + 1] = cost()

        INF = 10**18
        dp = [[INF] * (k + 1) for _ in range(n + 1)]
        dp[0][0] = 0
        for i in range(n + 1):
            for j in range(k + 1):
                if dp[i][j] >= INF:
                    continue
                if i < n:
                    dp[i + 1][j] = min(dp[i + 1][j], dp[i][j])
                if j < k and i + x <= n:
                    dp[i + x][j + 1] = min(dp[i + x][j + 1], dp[i][j] + costs[i])
        return min(dp[i][k] for i in range(n + 1))
# @lc code=end
