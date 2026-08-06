#
# @lc app=leetcode id=3763 lang=python3
#
# [3763] Maximum Total Sum with Threshold Constraints
#
# https://leetcode.com/problems/maximum-total-sum-with-threshold-constraints/description/
#
# algorithms
# Medium (82.83%)
# Likes:    9
# Dislikes: 1
# Total Accepted:    791
# Total Submissions: 955
# Testcase Example:  "[1,10,4,2,1,6]\n[5,1,5,5,2,2]"
#
#
# You are given two integer arrays nums and threshold, both of length n.
#
# Starting at step = 1, you perform the following repeatedly:
#
# Choose an unused index i such that threshold[i] <= step.
#
# If no such index exists, the process ends.
#
# Add nums[i] to your running total.
#
# Mark index i as used and increment step by 1.
#
# Return the maximum total sum you can obtain by choosing indices
# optimally.
#
# Example 1:
#
# Input: nums = [1,10,4,2,1,6], threshold = [5,1,5,5,2,2]
#
# Output: 17
#
# Explanation:
#
# At step = 1, choose i = 1 since threshold[1] <= step. The total sum
# becomes 10. Mark index 1.
#
# At step = 2, choose i = 4 since threshold[4] <= step. The total sum
# becomes 11. Mark index 4.
#
# At step = 3, choose i = 5 since threshold[5] <= step. The total sum
# becomes 17. Mark index 5.
#
# At step = 4, we cannot choose indices 0, 2, or 3 because their
# thresholds are > 4, so we end the process.
#
# Example 2:
#
# Input: nums = [4,1,5,2,3], threshold = [3,3,2,3,3]
#
# Output: 0
#
# Explanation:
#
# At step = 1 there is no index i with threshold[i] <= 1, so the process
# ends immediately. Thus, the total sum is 0.
#
# Example 3:
#
# Input: nums = [2,6,10,13], threshold = [2,1,1,1]
#
# Output: 31
#
# Explanation:
#
# At step = 1, choose i = 3 since threshold[3] <= step. The total sum
# becomes 13. Mark index 3.
#
# At step = 2, choose i = 2 since threshold[2] <= step. The total sum
# becomes 23. Mark index 2.
#
# At step = 3, choose i = 1 since threshold[1] <= step. The total sum
# becomes 29. Mark index 1.
#
# At step = 4, choose i = 0 since threshold[0] <= step. The total sum
# becomes 31. Mark index 0.
#
# After step = 4 all indices have been chosen, so the process ends.
#
# Constraints:
#
# n == nums.length == threshold.length
#
# 1 <= n <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= threshold[i] <= n
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def maxSum(self, nums: List[int], threshold: List[int]) -> int:
        """
        Interview explanation:
        At step s only indices with threshold <= s are eligible. Always take the
        largest available value; stop when none remain.

        Algorithm:
        - Bucket indices by threshold.
        - For step = 1..n: push newly unlocked nums into a max-heap; pop one if any.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        buckets = [[] for _ in range(n + 1)]
        for i, t in enumerate(threshold):
            buckets[t].append(nums[i])
        pq: List[int] = []
        total = 0
        for step in range(1, n + 1):
            for x in buckets[step]:
                heapq.heappush(pq, -x)
            if not pq:
                break
            total += -heapq.heappop(pq)
        return total

    def maxSum_threshold_order(self, nums: List[int], threshold: List[int]) -> int:
        """
        Interview explanation:
        Alternate: the achievable set is unique (all items with threshold <= T for
        maximal feasible T), so sum in increasing-threshold order.

        Algorithm:
        - Sort indices by threshold; greedily assign to steps 1,2,... until blocked.

        Complexity: O(n log n) time, O(n) space.
        """
        order = sorted(range(len(nums)), key=lambda i: threshold[i])
        total = 0
        for step, i in enumerate(order, 1):
            if step < threshold[i]:
                break
            total += nums[i]
        return total
# @lc code=end
