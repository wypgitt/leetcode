#
# @lc app=leetcode id=2323 lang=python3
#
# [2323] Find Minimum Time to Finish All Jobs II
#
# https://leetcode.com/problems/find-minimum-time-to-finish-all-jobs-ii/description/
#
# algorithms
# Medium (66.15%)
# Likes:    70
# Dislikes: 19
# Total Accepted:    12.9K
# Total Submissions: 19.5K
# Testcase Example:  "[5,2,4]\n[1,7,5]"
#
#
# You are given two 0-indexed integer arrays jobs and workers of equal
# length, where jobs[i] is the amount of time needed to complete the i^th
# job, and workers[j] is the amount of time the j^th worker can work each
# day.
#
# Each job should be assigned to exactly one worker, such that each worker
# completes exactly one job.
#
# Return the minimum number of days needed to complete all the jobs after
# assignment.
#
# Example 1:
#
# Input: jobs = [5,2,4], workers = [1,7,5]
# Output: 2
# Explanation:
# - Assign the 2^nd worker to the 0^th job. It takes them 1 day to finish
# the job.
# - Assign the 0^th worker to the 1^st job. It takes them 2 days to finish
# the job.
# - Assign the 1^st worker to the 2^nd job. It takes them 1 day to finish
# the job.
# It takes 2 days for all the jobs to be completed, so return 2.
# It can be proven that 2 days is the minimum number of days needed.
#
# Example 2:
#
# Input: jobs = [3,18,15,9], workers = [6,5,1,3]
# Output: 3
# Explanation:
# - Assign the 2^nd worker to the 0^th job. It takes them 3 days to finish
# the job.
# - Assign the 0^th worker to the 1^st job. It takes them 3 days to finish
# the job.
# - Assign the 1^st worker to the 2^nd job. It takes them 3 days to finish
# the job.
# - Assign the 3^rd worker to the 3^rd job. It takes them 3 days to finish
# the job.
# It takes 3 days for all the jobs to be completed, so return 3.
# It can be proven that 3 days is the minimum number of days needed.
#
# Constraints:
#
# n == jobs.length == workers.length
#
# 1 <= n <= 10^5
#
# 1 <= jobs[i], workers[i] <= 10^5
#
# @lc code=start
from typing import List


class Solution:
    def minimumTime(self, jobs: List[int], workers: List[int]) -> int:
        """
        Interview explanation:
        Assign each job to exactly one worker (bijection). Days for a pair =
        ceil(job/worker). Minimize the max days over the assignment.

        Algorithm:
        - Greedy: sort both ascending; pair i-th smallest job with i-th
          smallest worker; answer is max ceil.

        Complexity: O(n log n) time, O(1) extra space.
        """
        jobs.sort()
        workers.sort()
        return max((a + b - 1) // b for a, b in zip(jobs, workers))
# @lc code=end
