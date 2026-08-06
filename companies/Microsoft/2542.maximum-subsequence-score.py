#
# @lc app=leetcode id=2542 lang=python3
#
# [2542] Maximum Subsequence Score
#
# https://leetcode.com/problems/maximum-subsequence-score/description/
#
# algorithms
# Medium (54.90%)
# Likes:    3211
# Dislikes: 213
# Total Accepted:    161K
# Total Submissions: 293.3K
# Testcase Example:  "[1,3,3,2]\n[2,1,3,4]\n3"
#
# You are given two 0-indexed integer arrays nums1 and nums2 of equal length n
# and a positive integer k. You must choose a subsequence of indices from nums1
# of length k.
#
# For chosen indices i_0, i_1, ..., i_k - 1, your score is defined as:
#
#
# The sum of the selected elements from nums1 multiplied with the minimum of the
# selected elements from nums2.
#
#
# It can defined simply as: (nums1[i_0] + nums1[i_1] +...+ nums1[i_k - 1]) *
# min(nums2[i_0] , nums2[i_1], ... ,nums2[i_k - 1]).
#
# Return the maximum possible score.
#
# A subsequence of indices of an array is a set that can be derived from the set
# {0, 1, ..., n-1} by deleting some or no elements.
#
#
#
# Example 1:
#
# Input: nums1 = [1,3,3,2], nums2 = [2,1,3,4], k = 3
# Output: 12
# Explanation:
# The four possible subsequence scores are:
# - We choose the indices 0, 1, and 2 with score = (1+3+3) * min(2,1,3) = 7.
# - We choose the indices 0, 1, and 3 with score = (1+3+2) * min(2,1,4) = 6.
# - We choose the indices 0, 2, and 3 with score = (1+3+2) * min(2,3,4) = 12.
# - We choose the indices 1, 2, and 3 with score = (3+3+2) * min(1,3,4) = 8.
# Therefore, we return the max score, which is 12.
#
# Example 2:
#
# Input: nums1 = [4,2,3,1,1], nums2 = [7,5,10,9,6], k = 1
# Output: 30
# Explanation:
# Choosing index 2 is optimal: nums1[2] * nums2[2] = 3 * 10 = 30 is the maximum
# possible score.
#
#
#
# Constraints:
#
#
# n == nums1.length == nums2.length
#
#
# 1 <= n <= 10^5
#
#
# 0 <= nums1[i], nums2[j] <= 10^5
#
#
# 1 <= k <= n
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def maxScore(self, nums1: List[int], nums2: List[int], k: int) -> int:
        """
        Interview explanation:
        Pick k indices; score = (sum of nums1) * (min of nums2). Maximize.

        Algorithm:
        - Sort pairs by nums2 descending so current nums2 is the min for the
          prefix of chosen pairs that include it as bottleneck.
        - Keep a size-k min-heap of nums1 values and their running sum; drop
          smallest nums1 when size exceeds k. Track max sum*nums2.

        Complexity: O(n log n) time, O(n) space.
        """
        pairs = sorted(zip(nums2, nums1), reverse=True)
        heap: List[int] = []
        s = 0
        ans = 0
        for n2, n1 in pairs:
            heapq.heappush(heap, n1)
            s += n1
            if len(heap) > k:
                s -= heapq.heappop(heap)
            if len(heap) == k:
                ans = max(ans, s * n2)
        return ans
# @lc code=end
