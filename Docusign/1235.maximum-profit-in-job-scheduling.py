#
# @lc app=leetcode id=1235 lang=python3
#
# [1235] Maximum Profit in Job Scheduling
#
# https://leetcode.com/problems/maximum-profit-in-job-scheduling/description/
#
# algorithms
# Hard (54.81%)
# Likes:    7375
# Dislikes: 123
# Total Accepted:    433K
# Total Submissions: 791K
# Testcase Example:  "[1,2,3,3]"
#
# We have n jobs, where every job is scheduled to be done from startTime[i] to
# endTime[i], obtaining a profit of profit[i].
#
# You're given the startTime, endTime and profit arrays, return the maximum
# profit you can take such that there are no two jobs in the subset with
# overlapping time range.
#
# If you choose a job that ends at time X you will be able to start another job
# that starts at time X.
#
# Example 1:
#
# Input: startTime = [1,2,3,3], endTime = [3,4,5,6], profit = [50,10,40,70]
# Output: 120
# Explanation: The subset chosen is the first and fourth job.
# Time range [1-3]+[3-6] , we get profit of 120 = 50 + 70.
#
# Example 2:
#
# Input: startTime = [1,2,3,4,6], endTime = [3,5,10,6,9], profit =
# [20,20,100,70,60]
# Output: 150
# Explanation: The subset chosen is the first, fourth and fifth job.
# Profit obtained 150 = 20 + 70 + 60.
#
# Example 3:
#
# Input: startTime = [1,1,1], endTime = [2,3,4], profit = [5,6,4]
# Output: 6
#
# Constraints:
#
# 1 <= startTime.length == endTime.length == profit.length <= 5 * 10^4
#
# 1 <= startTime[i] < endTime[i] <= 10^9
#
# 1 <= profit[i] <= 10^4
#


# @lc code=start
from typing import List
import bisect

class Solution:
    def jobScheduling(self, startTime: List[int], endTime: List[int], profit: List[int]) -> int:
        """
        Interview explanation:
        Max profit non-overlapping jobs. Sort by end time; DP[i] = best using
        first i jobs; for job i binary search latest job ending <= start[i].

        Algorithm:
        - jobs sorted by end; ends list; dp[0]=0
        - for i,j: dp[i+1]=max(dp[i], profit[j]+dp[bisect_right(ends, start)])

        Complexity: O(n log n) time, O(n) space.
        """
        jobs = sorted(zip(endTime, startTime, profit))
        n = len(jobs)
        ends = [e for e, _, _ in jobs]
        dp = [0] * (n + 1)
        for i, (e, s, p) in enumerate(jobs):
            j = bisect.bisect_right(ends, s, hi=i)
            dp[i + 1] = max(dp[i], dp[j] + p)
        return dp[n]

    def jobScheduling_memo(self, startTime: List[int], endTime: List[int], profit: List[int]) -> int:
        """
        Interview explanation:
        Alternate top-down: sort by start; for each job take or skip; if take,
        bisect next job with start >= end.

        Algorithm:
        - jobs by start; dfs(i)=max(dfs(i+1), profit+dfs(next)); memo

        Complexity: O(n log n) time, O(n) space.
        """
        jobs = sorted(zip(startTime, endTime, profit))
        starts = [s for s, _, _ in jobs]
        n = len(jobs)
        memo = {}

        def dfs(i: int) -> int:
            if i >= n:
                return 0
            if i in memo:
                return memo[i]
            # skip
            best = dfs(i + 1)
            # take
            s, e, p = jobs[i]
            nxt = bisect.bisect_left(starts, e)
            best = max(best, p + dfs(nxt))
            memo[i] = best
            return best

        return dfs(0)
# @lc code=end
