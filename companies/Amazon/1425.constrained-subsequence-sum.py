#
# @lc app=leetcode id=1425 lang=python3
#
# [1425] Constrained Subsequence Sum
#
# https://leetcode.com/problems/constrained-subsequence-sum/description/
#
# algorithms
# Hard (56.47%)
# Likes:    2277
# Dislikes: 109
# Total Accepted:    95.2K
# Total Submissions: 169K
# Testcase Example:  "[10,2,-10,5,20]"
#
# Given an integer array nums and an integer k, return the maximum sum of a
# non-empty subsequence of that array such that for every two consecutive
# integers in the subsequence, nums[i] and nums[j], where i < j, the condition
# j - i <= k is satisfied.
#
# A subsequence of an array is obtained by deleting some number of elements
# (can be zero) from the array, leaving the remaining elements in their
# original order.
#
# Example 1:
#
# Input: nums = [10,2,-10,5,20], k = 2
# Output: 37
# Explanation: The subsequence is [10, 2, 5, 20].
#
# Example 2:
#
# Input: nums = [-1,-2,-3], k = 1
# Output: -1
# Explanation: The subsequence must be non-empty, so we choose the largest
# number.
#
# Example 3:
#
# Input: nums = [10,-2,-10,-5,20], k = 2
# Output: 23
# Explanation: The subsequence is [10, -2, -5, 20].
#
# Constraints:
#
# 1 <= k <= nums.length <= 10^5
#
# -10^4 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List
from collections import deque
import heapq


class Solution:
    def constrainedSubsetSum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Max subsequence sum with adjacent chosen indices differ by at most k
        (non-empty). DP: dp[i]=nums[i]+max(0, max dp in [i-k,i-1]); mono deque
        maintains sliding window maximum of dp.

        Algorithm:
        (deque DP)
        - dq stores indices of dp decreasing; pop out of window; update ans.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        dp = nums[:]
        dq = deque()  # indices, decreasing dp
        ans = nums[0]
        for i in range(n):
            while dq and dq[0] < i - k:
                dq.popleft()
            if dq:
                dp[i] = max(dp[i], nums[i] + dp[dq[0]])
            ans = max(ans, dp[i])
            while dq and dp[dq[-1]] <= dp[i]:
                dq.pop()
            dq.append(i)
        return ans

    def constrainedSubsetSum_heap(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: max-heap of (dp, index); lazy discard out-of-window entries.

        Algorithm:
        - Heap (-dp,i); for each i take best valid; push new dp.

        Complexity: O(n log n) time, O(n) space.
        """
        heap = []  # (-dp, index)
        ans = float("-inf")
        dp_at = [0] * len(nums)
        for i, x in enumerate(nums):
            while heap and heap[0][1] < i - k:
                heapq.heappop(heap)
            best = -heap[0][0] if heap else 0
            dp_at[i] = x + max(0, best)
            ans = max(ans, dp_at[i])
            heapq.heappush(heap, (-dp_at[i], i))
        return ans
# @lc code=end
