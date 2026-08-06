#
# @lc app=leetcode id=857 lang=python3
#
# [857] Minimum Cost to Hire K Workers
#
# https://leetcode.com/problems/minimum-cost-to-hire-k-workers/description/
#
# algorithms
# Hard (63.73%)
# Likes:    3092
# Dislikes: 407
# Total Accepted:    164K
# Total Submissions: 257K
# Testcase Example:  "[10,20,5]"
#
# There are n workers. You are given two integer arrays quality and wage where
# quality[i] is the quality of the i^th worker and wage[i] is the minimum wage
# expectation for the i^th worker.
#
# We want to hire exactly k workers to form a paid group. To hire a group of k
# workers, we must pay them according to the following rules:
#
# Every worker in the paid group must be paid at least their minimum wage
# expectation.
#
# In the group, each worker's pay must be directly proportional to their
# quality. This means if a worker’s quality is double that of another worker in
# the group, then they must be paid twice as much as the other worker.
#
# Given the integer k, return the least amount of money needed to form a paid
# group satisfying the above conditions. Answers within 10^-5 of the actual
# answer will be accepted.
#
# Example 1:
#
# Input: quality = [10,20,5], wage = [70,50,30], k = 2
# Output: 105.00000
# Explanation: We pay 70 to 0^th worker and 35 to 2^nd worker.
#
# Example 2:
#
# Input: quality = [3,1,10,10,1], wage = [4,8,2,2,7], k = 3
# Output: 30.66667
# Explanation: We pay 4 to 0^th worker, 13.33333 to 2^nd and 3^rd workers
# separately.
#
# Constraints:
#
# n == quality.length == wage.length
#
# 1 <= k <= n <= 10^4
#
# 1 <= quality[i], wage[i] <= 10^4
#

# @lc code=start

from typing import List
import heapq


class Solution:
    def mincostToHireWorkers(
        self, quality: List[int], wage: List[int], k: int
    ) -> float:
        """
        Interview explanation:
        Paid proportional to quality; each gets ≥ wage. Group by wage/quality
        ratio: sort workers by ratio ascending; for a captain with ratio r,
        cost = r * sum(qualities of k workers with ratio ≤ r). Maintain a max
        heap of qualities to keep the k smallest quality sum.

        Algorithm (heap):
        - Sort by wage/quality; scan; push quality to max-heap; if >k pop largest
          quality; when size==k update ans = ratio * sumq.

        Complexity: O(n log n) time, O(n) space.
        """
        workers = sorted((w / q, q) for q, w in zip(quality, wage))
        ans = float("inf")
        sumq = 0
        heap = []  # max-heap of qualities via negation
        for ratio, q in workers:
            heapq.heappush(heap, -q)
            sumq += q
            if len(heap) > k:
                sumq += heapq.heappop(heap)  # pops most negative = largest q
            if len(heap) == k:
                ans = min(ans, ratio * sumq)
        return ans
# @lc code=end
