#
# @lc app=leetcode id=2263 lang=python3
#
# [2263] Make Array Non-decreasing or Non-increasing
#
# https://leetcode.com/problems/make-array-non-decreasing-or-non-increasing/description/
#
# algorithms
# Hard (65.55%)
# Likes:    94
# Dislikes: 13
# Total Accepted:    4.9K
# Total Submissions: 7.4K
# Testcase Example:  "[3,2,4,5,0]"
#
#
# You are given a 0-indexed integer array nums. In one operation, you can:
#
# Choose an index i in the range 0 <= i < nums.length
#
# Set nums[i] to nums[i] + 1 or nums[i] - 1
#
# Return the minimum number of operations to make nums non-decreasing or
# non-increasing.
#
# Example 1:
#
# Input: nums = [3,2,4,5,0]
# Output: 4
# Explanation:
# One possible way to turn nums into non-increasing order is to:
# - Add 1 to nums[1] once so that it becomes 3.
# - Subtract 1 from nums[2] once so it becomes 3.
# - Subtract 1 from nums[3] twice so it becomes 3.
# After doing the 4 operations, nums becomes [3,3,3,3,0] which is in
# non-increasing order.
# Note that it is also possible to turn nums into [4,4,4,4,0] in 4
# operations.
# It can be proven that 4 is the minimum number of operations needed.
#
# Example 2:
#
# Input: nums = [2,2,3,4]
# Output: 0
# Explanation: nums is already in non-decreasing order, so no operations
# are needed and we return 0.
#
# Example 3:
#
# Input: nums = [0]
# Output: 0
# Explanation: nums is already in non-decreasing order, so no operations
# are needed and we return 0.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 0 <= nums[i] <= 1000
#
# Follow up: Can you solve it in O(n*log(n)) time complexity?
#
# @lc code=start
from typing import List
import heapq


class Solution:
    def convertArray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Min ops (+/-1 on an element) to make nums non-decreasing OR non-increasing.

        Algorithm:
        - Greedy heap: cost to make non-increasing via min-heap; negate for
          non-decreasing; take min of both.

        Complexity: O(n log n) time, O(n) space.
        """
        def cost(arr: List[int]) -> int:
            ans = 0
            hq: List[int] = []
            for num in arr:
                if hq and hq[0] < num:
                    ans += num - heapq.heappushpop(hq, num)
                heapq.heappush(hq, num)
            return ans

        return min(cost(nums), cost([-x for x in nums]))

    def convertArray_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        DP alternate (values in 0..1000): f[i][v] = min cost to set position i to v
        with monotonicity vs previous.

        Algorithm:
        - Prefix-min transitions for non-decreasing; reverse array for increasing
          case via same non-decreasing DP on reversed (equiv non-increasing).

        Complexity: O(n * V) time/space, V=1001.
        """
        def solve(arr: List[int]) -> int:
            V = 1001
            dp = [abs(v - arr[0]) for v in range(V)]
            for x in arr[1:]:
                pref = [0] * V
                pref[0] = dp[0]
                for v in range(1, V):
                    pref[v] = min(pref[v - 1], dp[v])
                dp = [abs(x - v) + pref[v] for v in range(V)]
            return min(dp)

        return min(solve(nums), solve(nums[::-1]))
# @lc code=end
