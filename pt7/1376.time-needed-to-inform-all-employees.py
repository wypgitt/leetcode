#
# @lc app=leetcode id=1376 lang=python3
#
# [1376] Time Needed to Inform All Employees
#
# https://leetcode.com/problems/time-needed-to-inform-all-employees/description/
#
# algorithms
# Medium (60.49%)
# Likes:    4259
# Dislikes: 325
# Total Accepted:    260.1K
# Total Submissions: 430K
# Testcase Example:  '1\n0\n[-1]\n[0]'
#
# A company has n employees with a unique ID for each employee from 0 to n - 1.
# The head of the company is the one with headID.
# 
# Each employee has one direct manager given in the manager array where
# manager[i] is the direct manager of the i-th employee, manager[headID] = -1.
# Also, it is guaranteed that the subordination relationships have a tree
# structure.
# 
# The head of the company wants to inform all the company employees of an
# urgent piece of news. He will inform his direct subordinates, and they will
# inform their subordinates, and so on until all employees know about the
# urgent news.
# 
# The i-th employee needs informTime[i] minutes to inform all of his direct
# subordinates (i.e., After informTime[i] minutes, all his direct subordinates
# can start spreading the news).
# 
# Return the number of minutes needed to inform all the employees about the
# urgent news.
# 
# 
# Example 1:
# 
# 
# Input: n = 1, headID = 0, manager = [-1], informTime = [0]
# Output: 0
# Explanation: The head of the company is the only employee in the company.
# 
# 
# Example 2:
# 
# 
# Input: n = 6, headID = 2, manager = [2,2,-1,2,2,2], informTime =
# [0,0,1,0,0,0]
# Output: 1
# Explanation: The head of the company with id = 2 is the direct manager of all
# the employees in the company and needs 1 minute to inform them all.
# The tree structure of the employees in the company is shown.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^5
# 0 <= headID < n
# manager.length == n
# 0 <= manager[i] < n
# manager[headID] == -1
# informTime.length == n
# 0 <= informTime[i] <= 1000
# informTime[i] == 0 if employee i has no subordinates.
# It is guaranteed that all the employees can be informed.
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def numOfMinutes(self, n: int, headID: int, manager: List[int], informTime: List[int]) -> int:
        reports = [[] for _ in range(n)]
        for employee, boss in enumerate(manager):
            if boss != -1:
                reports[boss].append(employee)

        max_time = 0
        stack = [(headID, 0)]

        while stack:
            employee, elapsed = stack.pop()
            max_time = max(max_time, elapsed)

            for report in reports[employee]:
                stack.append((report, elapsed + informTime[employee]))

        return max_time
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# The management relationships form a rooted tree at `headID`. The time for an
# employee to hear the news is the sum of inform times along the path from the
# head to that employee. We need the maximum such path time.
#
# Data structure:
# Build an adjacency list from manager to direct reports. Then use an iterative
# DFS stack containing `(employee, elapsed_time_when_informed)`.
#
# Walkthrough:
# 1. Convert the `manager` array into `reports`.
# 2. Start from the head at elapsed time 0.
# 3. When visiting a manager, each direct report hears after
#    `elapsed + informTime[manager]`.
# 4. Track the maximum elapsed time seen.
#
# Edge cases:
# - Single employee: stack starts with head at 0, answer 0.
# - Manager with informTime 0: reports are informed at the same elapsed time.
# - Deep chain: iterative DFS avoids Python recursion-depth issues.
#
# Complexity:
# - Time: O(n), each employee is processed once.
# - Space: O(n), for adjacency list and stack.
