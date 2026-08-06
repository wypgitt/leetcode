#
# @lc app=leetcode id=826 lang=python3
#
# [826] Most Profit Assigning Work
#
# https://leetcode.com/problems/most-profit-assigning-work/description/
#
# algorithms
# Medium (56.3%)
# Likes:    2564
# Dislikes: 174
# Total Accepted:    249K
# Total Submissions: 442K
# Testcase Example:  "[2,4,6,8,10]"
#
# You have n jobs and m workers. You are given three arrays: difficulty,
# profit, and worker where:
#
# difficulty[i] and profit[i] are the difficulty and the profit of the i^th
# job, and
#
# worker[j] is the ability of j^th worker (i.e., the j^th worker can only
# complete a job with difficulty at most worker[j]).
#
# Every worker can be assigned at most one job, but one job can be completed
# multiple times.
#
# For example, if three workers attempt the same job that pays $1, then the
# total profit will be $3. If a worker cannot complete any job, their profit is
# $0.
#
# Return the maximum profit we can achieve after assigning the workers to the
# jobs.
#
# Example 1:
#
# Input: difficulty = [2,4,6,8,10], profit = [10,20,30,40,50], worker =
# [4,5,6,7]
# Output: 100
# Explanation: Workers are assigned jobs of difficulty [4,4,6,6] and they get a
# profit of [20,20,30,30] separately.
#
# Example 2:
#
# Input: difficulty = [85,47,57], profit = [24,66,99], worker = [40,25,25]
# Output: 0
#
# Constraints:
#
# n == difficulty.length
#
# n == profit.length
#
# m == worker.length
#
# 1 <= n, m <= 10^4
#
# 1 <= difficulty[i], profit[i], worker[i] <= 10^5
#

# @lc code=start

from typing import List
from bisect import bisect_right


class Solution:
    def maxProfitAssignment(
        self, difficulty: List[int], profit: List[int], worker: List[int]
    ) -> int:
        """
        Interview explanation:
        Each worker does one job with difficulty ≤ ability for max profit. Sort
        jobs by difficulty; precompute best profit up to each difficulty; for
        each worker two-pointer / binary search best profit.

        Algorithm (sort + two pointers):
        - Sort jobs by difficulty; sort workers; scan jobs while difficulty≤ability,
          track best profit; sum.

        Complexity: O(n log n + m log m) time, O(n) space.
        """
        jobs = sorted(zip(difficulty, profit))
        worker.sort()
        ans = best = i = 0
        n = len(jobs)
        for w in worker:
            while i < n and jobs[i][0] <= w:
                best = max(best, jobs[i][1])
                i += 1
            ans += best
        return ans

    def maxProfitAssignment_binary(
        self, difficulty: List[int], profit: List[int], worker: List[int]
    ) -> int:
        """
        Interview explanation:
        Alternate: after sorting jobs and prefix-max profits, binary search each
        worker's max affordable difficulty.

        Algorithm:
        - jobs sorted; pref[i]=max profit among jobs[0..i]; bisect for worker.

        Complexity: O((n+m) log n) time, O(n) space.
        """
        jobs = sorted(zip(difficulty, profit))
        diffs = [d for d, _ in jobs]
        best = []
        cur = 0
        for _, p in jobs:
            cur = max(cur, p)
            best.append(cur)
        ans = 0
        for w in worker:
            i = bisect_right(diffs, w) - 1
            if i >= 0:
                ans += best[i]
        return ans
# @lc code=end
