#
# @lc app=leetcode id=1723 lang=python3
#
# [1723] Find Minimum Time to Finish All Jobs
#
# https://leetcode.com/problems/find-minimum-time-to-finish-all-jobs/description/
#
# algorithms
# Hard (46.09%)
# Likes:    1151
# Dislikes: 40
# Total Accepted:    46.2K
# Total Submissions: 100K
# Testcase Example:  "[3,2,3]"
#
# You are given an integer array jobs, where jobs[i] is the amount of time it
# takes to complete the i^th job.
#
# There are k workers that you can assign jobs to. Each job should be assigned
# to exactly one worker. The working time of a worker is the sum of the time it
# takes to complete all jobs assigned to them. Your goal is to devise an
# optimal assignment such that the maximum working time of any worker is
# minimized.
#
# Return the minimum possible maximum working time of any assignment.
#
# Example 1:
#
# Input: jobs = [3,2,3], k = 3
# Output: 3
# Explanation: By assigning each person one job, the maximum time is 3.
#
# Example 2:
#
# Input: jobs = [1,2,4,7,8], k = 2
# Output: 11
# Explanation: Assign the jobs the following way:
# Worker 1: 1, 2, 8 (working time = 1 + 2 + 8 = 11)
# Worker 2: 4, 7 (working time = 4 + 7 = 11)
# The maximum working time is 11.
#
# Constraints:
#
# 1 <= k <= jobs.length <= 12
#
# 1 <= jobs[i] <= 10^7
#

# @lc code=start
from typing import List


class Solution:
    def minimumTimeRequired(self, jobs: List[int], k: int) -> int:
        """
        Interview explanation:
        Assign jobs to k workers minimizing the max load. Binary search on max time
        T + backtracking assignment with pruning (sort jobs descending).

        Algorithm:
        - lo = max(jobs), hi = sum(jobs)
        - check(T): try assign each job to a worker with load+job<=T; prune empty
          worker symmetry.
        - Binary search minimal T.

        Complexity: O(k^n * log S) worst; pruned well for n<=12. O(k) space.
        """
        jobs.sort(reverse=True)
        lo, hi = jobs[0], sum(jobs)

        def can(T: int) -> bool:
            loads = [0] * k

            def dfs(i: int) -> bool:
                if i == len(jobs):
                    return True
                seen = set()
                for w in range(k):
                    if loads[w] in seen:
                        continue
                    if loads[w] + jobs[i] <= T:
                        seen.add(loads[w])
                        loads[w] += jobs[i]
                        if dfs(i + 1):
                            return True
                        loads[w] -= jobs[i]
                    if loads[w] == 0:
                        break
                return False

            return dfs(0)

        while lo < hi:
            mid = (lo + hi) // 2
            if can(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
