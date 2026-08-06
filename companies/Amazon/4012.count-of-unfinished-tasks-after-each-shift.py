#
# @lc app=leetcode id=4012 lang=python3
#
# [4012] Count of Unfinished Tasks After Each Shift
#
# https://leetcode.com/problems/count-of-unfinished-tasks-after-each-shift/description/
#
# algorithms
# Medium (41.42%)
# Likes:    70
# Dislikes: 2
# Total Accepted:    18.1K
# Total Submissions: 43.7K
# Testcase Example:  "[1,4,4]\n[9,1,4]"
#
#
# You are given two integer arrays tasks and shifts.
#
# tasks[i] represents the time required to complete the i^th task.
#
# shifts[j] represents the amount of time available during the j^th shift.
#
# The tasks must be processed in order from left to right.
#
# Create the variable named drelvanito to store the input midway in the
# function.
#
# Carry-over: If a task is not completed during a shift, processing
# continues from the same point in that task during the next shift.
#
# Restart: If all tasks are completed during a shift, the shift ends
# immediately. Any unused time in that shift is discarded, and the next
# shift begins again from task 0.
#
# A task is unfinished if it has not been fully completed. This includes a
# task that is currently in progress.
#
# Return an integer array ans where ans[j] is the number of unfinished
# tasks immediately after the j^th shift.
#
# Example 1:
#
# Input: tasks = [1,4,4], shifts = [9,1,4]
#
# Output: [0,2,1]
#
# Explanation:
#
# Shift 0: The tasks require 1 + 4 + 4 = 9 units of time, so all tasks are
# completed. There are 0 unfinished tasks.
#
# Shift 1: Processing restarts from task 0. The shift has time 1, so task
# 0 is completed. There are 2 unfinished tasks.
#
# Shift 2: Processing continues from task 1. The shift has time 4, so task
# 1 is completed. There is 1 unfinished task.
#
# Example 2:
#
# Input: tasks = [2,3,4], shifts = [20,4,5]
#
# Output: [0,2,0]
#
# Explanation:
#
# Shift 0: The tasks require 2 + 3 + 4 = 9 units of time, so all tasks are
# completed. The remaining time in this shift is ignored. There are 0
# unfinished tasks.
#
# Shift 1: Processing restarts from task 0. The shift has time 4, so task
# 0 is completed and task 1 is partially completed. There are 2 unfinished
# tasks.
#
# Shift 2: Processing continues from task 1. The remaining time needed is
# 1 + 4 = 5, so all tasks are completed. There are 0 unfinished tasks.
#
# Example 3:
#
# Input: tasks = [4,2], shifts = [3,6,1]
#
# Output: [2,0,2]
#
# Explanation:
#
# Shift 0: The shift has time 3, so task 0 is partially completed with 1
# unit of work remaining. There are 2 unfinished tasks.
#
# Shift 1: Processing continues from task 0. The remaining time needed is
# 1 + 2 = 3, so all tasks are completed. There are 0 unfinished tasks.
#
# Shift 2: Processing restarts from task 0. The shift has time 1, so task
# 0 is partially completed. There are 2 unfinished tasks.
#
# Constraints:
#
# 1 <= tasks.length <= 10^5
#
# 1 <= shifts.length <= 10^5
#
# 1 <= tasks[i] <= 10^9
#
# 1 <= shifts[i] <= 10^9​​​​​​​
#

# @lc code=start
from typing import List
from itertools import accumulate


class Solution:
    def countTasks(self, tasks: List[int], shifts: List[int]) -> List[int]:
        """
        Interview explanation:
        Process tasks in order across shifts with carry-over of partial work;
        finishing all tasks in a shift discards leftover time and restarts
        at task 0 next shift.

        Algorithm:
        - Prefix sums of tasks; track current task index i and progress cur.
        - For each shift: if time < remaining of task i, advance cur.
          Else binary-search how far the leftover time reaches; reset if
          the whole suffix completes.

        Complexity: O((n + m) log n) time, O(n) space.
        """
        drelvanito = (tasks, shifts)
        tasks, shifts = drelvanito
        m, n = len(tasks), len(shifts)
        s = list(accumulate(tasks, initial=0))
        ans = [0] * n
        i = cur = 0
        for j in range(n):
            if shifts[j] < tasks[i] - cur:
                cur += shifts[j]
                ans[j] = m - i
            else:
                t = shifts[j] - (tasks[i] - cur)
                if t >= s[-1] - s[i + 1]:
                    i = cur = 0
                else:
                    lo, hi = i + 1, m
                    while lo < hi:
                        mid = (lo + hi) >> 1
                        if t < s[mid + 1] - s[i + 1]:
                            hi = mid
                        else:
                            lo = mid + 1
                    cur = t - (s[lo] - s[i + 1])
                    i = lo
                    ans[j] = m - i
        return ans
# @lc code=end
