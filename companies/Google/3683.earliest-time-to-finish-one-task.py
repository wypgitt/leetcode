#
# @lc app=leetcode id=3683 lang=python3
#
# [3683] Earliest Time to Finish One Task
#
# https://leetcode.com/problems/earliest-time-to-finish-one-task/description/
#
# algorithms
# Easy (84.88%)
# Likes:    54
# Dislikes: 5
# Total Accepted:    75.6K
# Total Submissions: 89K
# Testcase Example:  "[[1,6],[2,3]]"
#
#
# You are given a 2D integer array tasks where tasks[i] = [s_i, t_i].
#
# Each [s_i, t_i] in tasks represents a task with start time s_i that
# takes t_i units of time to finish.
#
# Return the earliest time at which at least one task is finished.
#
# Example 1:
#
# Input: tasks = [[1,6],[2,3]]
#
# Output: 5
#
# Explanation:
#
# The first task starts at time t = 1 and finishes at time 1 + 6 = 7. The
# second task finishes at time 2 + 3 = 5. You can finish one task at time
# 5.
#
# Example 2:
#
# Input: tasks = [[100,100],[100,100],[100,100]]
#
# Output: 200
#
# Explanation:
#
# All three tasks finish at time 100 + 100 = 200.
#
# Constraints:
#
# 1 <= tasks.length <= 100
#
# tasks[i] = [s_i, t_i]
#
# 1 <= s_i, t_i <= 100
#

# @lc code=start

from typing import List


class Solution:
    def earliestTime(self, tasks: List[List[int]]) -> int:
        """
        Interview explanation:
        Each task finishes at s_i + t_i independently; the earliest finish is
        the minimum of those completion times.

        Algorithm:
        - Return min(s + t for s, t in tasks).

        Complexity: O(n) time, O(1) space.
        """
        return min(s + t for s, t in tasks)
# @lc code=end
