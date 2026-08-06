#
# @lc app=leetcode id=1335 lang=python3
#
# [1335] Minimum Difficulty of a Job Schedule
#
# https://leetcode.com/problems/minimum-difficulty-of-a-job-schedule/description/
#
# algorithms
# Hard (59.8%)
# Likes:    3632
# Dislikes: 335
# Total Accepted:    232K
# Total Submissions: 389K
# Testcase Example:  "[6,5,4,3,2,1]"
#
# You want to schedule a list of jobs in d days. Jobs are dependent (i.e To
# work on the i^th job, you have to finish all the jobs j where 0 <= j < i).
#
# You have to finish at least one task every day. The difficulty of a job
# schedule is the sum of difficulties of each day of the d days. The difficulty
# of a day is the maximum difficulty of a job done on that day.
#
# You are given an integer array jobDifficulty and an integer d. The difficulty
# of the i^th job is jobDifficulty[i].
#
# Return the minimum difficulty of a job schedule. If you cannot find a
# schedule for the jobs return -1.
#
# Example 1:
#
# Input: jobDifficulty = [6,5,4,3,2,1], d = 2
# Output: 7
# Explanation: First day you can finish the first 5 jobs, total difficulty = 6.
# Second day you can finish the last job, total difficulty = 1.
# The difficulty of the schedule = 6 + 1 = 7
#
# Example 2:
#
# Input: jobDifficulty = [9,9,9], d = 4
# Output: -1
# Explanation: If you finish a job per day you will still have a free day. you
# cannot find a schedule for the given jobs.
#
# Example 3:
#
# Input: jobDifficulty = [1,1,1], d = 3
# Output: 3
# Explanation: The schedule is one job per day. total difficulty will be 3.
#
# Constraints:
#
# 1 <= jobDifficulty.length <= 300
#
# 0 <= jobDifficulty[i] <= 1000
#
# 1 <= d <= 10
#

# @lc code=start
from typing import List


class Solution:
    def minDifficulty(self, jobDifficulty: List[int], d: int) -> int:
        """
        Interview explanation:
        Partition n jobs (order fixed) into d contiguous days; day cost = max
        difficulty that day; minimize sum of day costs. Classic DP:
        dp[i][k] = min cost scheduling jobs i..n-1 in k days.

        Algorithm (DP):
        - If n<d return -1. dp[n]=0 for 0 days left at end.
        - For days from 1..d, for start i, scan j=i..n-d remaining taking running max.

        Complexity: O(n^2 * d) time, O(n*d) or O(n) space.
        """
        n = len(jobDifficulty)
        if n < d:
            return -1
        INF = 10**9
        # dp[i] = min cost for jobs[i:] with remaining days (rolling)
        dp = [INF] * (n + 1)
        dp[n] = 0
        for days in range(1, d + 1):
            ndp = [INF] * (n + 1)
            for i in range(n - days + 1):
                maxd = 0
                for j in range(i, n - days + 1):
                    maxd = max(maxd, jobDifficulty[j])
                    ndp[i] = min(ndp[i], maxd + dp[j + 1])
            dp = ndp
        return dp[0]
# @lc code=end

