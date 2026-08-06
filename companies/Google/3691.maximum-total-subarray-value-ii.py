#
# @lc app=leetcode id=3691 lang=python3
#
# [3691] Maximum Total Subarray Value II
#
# https://leetcode.com/problems/maximum-total-subarray-value-ii/description/
#
# algorithms
# Hard (41.76%)
# Likes:    348
# Dislikes: 11
# Total Accepted:    74.5K
# Total Submissions: 178.4K
# Testcase Example:  "[1,3,2]\n2"
#
#
# You are given an integer array nums of length n and an integer k.
#
# You must select exactly k distinct subarrays nums[l..r] of nums.
# Subarrays may overlap, but the exact same subarray (same l and r) cannot
# be chosen more than once.
#
# The value of a subarray nums[l..r] is defined as: max(nums[l..r]) -
# min(nums[l..r]).
#
# The total value is the sum of the values of all chosen subarrays.
#
# Return the maximum possible total value you can achieve.
#
# Example 1:
#
# Input: nums = [1,3,2], k = 2
#
# Output: 4
#
# Explanation:
#
# One optimal approach is:
#
# Choose nums[0..1] = [1, 3]. The maximum is 3 and the minimum is 1,
# giving a value of 3 - 1 = 2.
#
# Choose nums[0..2] = [1, 3, 2]. The maximum is still 3 and the minimum is
# still 1, so the value is also 3 - 1 = 2.
#
# Adding these gives 2 + 2 = 4.
#
# Example 2:
#
# Input: nums = [4,2,5,1], k = 3
#
# Output: 12
#
# Explanation:
#
# One optimal approach is:
#
# Choose nums[0..3] = [4, 2, 5, 1]. The maximum is 5 and the minimum is 1,
# giving a value of 5 - 1 = 4.
#
# Choose nums[1..3] = [2, 5, 1]. The maximum is 5 and the minimum is 1, so
# the value is also 4.
#
# Choose nums[2..3] = [5, 1]. The maximum is 5 and the minimum is 1, so
# the value is again 4.
#
# Adding these gives 4 + 4 + 4 = 12.
#
# Constraints:
#
# 1 <= n == nums.length <= 5 * 10^​​​​​​​4
#
# 0 <= nums[i] <= 10^9
#
# 1 <= k <= min(10^5, n * (n + 1) / 2)
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def maxTotalValue(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        For fixed left L, value(L,R) is non-increasing as R shrinks. Merge the
        n such chains with a max-heap, always taking the next best distinct
        subarray. Sparse table gives O(1) range max/min.

        Algorithm:
        - Build sparse tables for range max and min.
        - Push (value(L, n-1), L, n-1) for every L.
        - k times: pop best, add to answer; if R > L push (L, R-1).

        Complexity: O((n + k) log n) time, O(n log n) space.
        """
        n = len(nums)
        logn = n.bit_length()
        mx = [nums[:]]
        mn = [nums[:]]
        for j in range(1, logn):
            prev_mx, prev_mn = mx[j - 1], mn[j - 1]
            step = 1 << (j - 1)
            cur_mx = [0] * (n - (1 << j) + 1)
            cur_mn = [0] * (n - (1 << j) + 1)
            for i in range(len(cur_mx)):
                cur_mx[i] = max(prev_mx[i], prev_mx[i + step])
                cur_mn[i] = min(prev_mn[i], prev_mn[i + step])
            mx.append(cur_mx)
            mn.append(cur_mn)

        def value(l: int, r: int) -> int:
            j = (r - l + 1).bit_length() - 1
            return max(mx[j][l], mx[j][r - (1 << j) + 1]) - min(
                mn[j][l], mn[j][r - (1 << j) + 1]
            )

        heap = [(-value(l, n - 1), l, n - 1) for l in range(n)]
        heapq.heapify(heap)
        ans = 0
        for _ in range(k):
            neg, l, r = heapq.heappop(heap)
            ans += -neg
            if r > l:
                heapq.heappush(heap, (-value(l, r - 1), l, r - 1))
        return ans
# @lc code=end
