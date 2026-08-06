#
# @lc app=leetcode id=3962 lang=python3
#
# [3962] Maximum Subarray Sum After at Most K Swaps
#
# https://leetcode.com/problems/maximum-subarray-sum-after-at-most-k-swaps/description/
#
# algorithms
# Hard (14.28%)
# Likes:    46
# Dislikes: 5
# Total Accepted:    3.3K
# Total Submissions: 23.3K
# Testcase Example:  "[1,-1,0,2]\n1"
#
#
# You are given an integer array nums and an integer k.
#
# You are allowed to perform at most k swap operations on the array.
#
# In one swap operation, you may choose any two indices i and j and swap
# nums[i] and nums[j].
#
# Return an integer denoting the maximum possible subarray sum after
# performing the swaps.
#
# Example 1:
#
# Input: nums = [1,-1,0,2], k = 1
#
# Output: 3
#
# Explanation:
#
# We can swap on indices 1 and 3, resulting in the array [1, 2, 0, -1].
#
# The subarray [1, 2] has a sum of 3, which is the maximum possible
# subarray sum after at most k = 1​​​​​​​ swap.
#
# Example 2:
#
# Input: nums = [4,3,2,4], k = 2
#
# Output: 13
#
# Explanation:
#
# The maximum possible subarray sum after at most k = 2 swaps is the sum
# of the entire array, which is 13.
#
# Example 3:
#
# Input: nums = [-1,-2], k = 0
#
# Output: -1
#
# Explanation:
#
# k = 0 swaps are allowed.
#
# The possible subarrays are [-1], [-2], and [-1, -2], with sums -1, -2,
# and -3 respectively.
#
# Among these sums, the maximum is -1.
#
# Constraints:
#
# 1 <= nums.length <= 1500
#
# -10^5 <= nums[i] <= 10^5
#
# 0 <= k <= nums.length
#

# @lc code=start
import heapq


class Solution:
    def maxSum(self, nums: list[int], k: int) -> int:
        """
        Interview explanation:
        For a fixed window, swap its smallest entries with the largest outside
        values (up to k times). Enumerate left endpoints; maintain heaps of
        negatives inside / positives outside for O(log k) updates.

        Algorithm:
        - If ≤k negatives, answer is sum of all non-negatives (or max if all <0).
        - For each left i: grow right, keep up to k largest |neg| inside; then
          sweep right→left adding outside positives into a size-k min-heap of
          imports; track prefix[j+1]-prefix[i] − inside_neg_penalty + imports.

        Complexity: O(n² log k) time, O(n) space.
        """
        def update(heap, total, x):
            if k == 0:
                return total
            heapq.heappush(heap, x)
            total += x
            if len(heap) == k + 1:
                total -= heapq.heappop(heap)
            return total

        n = len(nums)
        neg_cnt = sum(x < 0 for x in nums)
        if neg_cnt == n:
            return max(nums)
        if neg_cnt <= k:
            return sum(x for x in nums if x >= 0)

        prefix = [0] * (n + 1)
        for i, x in enumerate(nums):
            prefix[i + 1] = prefix[i] + x

        result = 0
        dp = [0] * n
        for i in range(n):
            max_heap = []
            total1 = 0
            for j in range(i, n):
                if nums[j] < 0:
                    total1 = update(max_heap, total1, -nums[j])
                dp[j] = -total1
            min_heap = []
            total2 = 0
            for j in range(i):
                if nums[j] >= 0:
                    total2 = update(min_heap, total2, nums[j])
            for j in range(n - 1, i - 1, -1):
                result = max(result, prefix[j + 1] - prefix[i] - dp[j] + total2)
                if nums[j] >= 0:
                    total2 = update(min_heap, total2, nums[j])
            result = max(result, total2)
        return result
# @lc code=end
