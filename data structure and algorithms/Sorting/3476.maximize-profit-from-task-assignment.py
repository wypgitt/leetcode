#
# @lc app=leetcode id=3476 lang=python3
#
# [3476] Maximize Profit from Task Assignment
#
# https://leetcode.com/problems/maximize-profit-from-task-assignment/description/
#
# algorithms
# Medium (65.21%)
# Likes:    10
# Dislikes: 2
# Total Accepted:    1.1K
# Total Submissions: 1.8K
# Testcase Example:  "[1,2,3,4,5]\n[[1,100],[2,400],[3,100],[3,400]]"
#
#
# You are given an integer array workers, where workers[i] represents the
# skill level of the i^th worker. You are also given a 2D integer array
# tasks, where:
#
# tasks[i][0] represents the skill requirement needed to complete the
# task.
#
# tasks[i][1] represents the profit earned from completing the task.
#
# Each worker can complete at most one task, and they can only take a task
# if their skill level is equal to the task's skill requirement. An
# additional worker joins today who can take up any task, regardless of
# the skill requirement.
#
# Return the maximum total profit that can be earned by optimally
# assigning the tasks to the workers.
#
# Example 1:
#
# Input: workers = [1,2,3,4,5], tasks = [[1,100],[2,400],[3,100],[3,400]]
#
# Output: 1000
#
# Explanation:
#
# Worker 0 completes task 0.
#
# Worker 1 completes task 1.
#
# Worker 2 completes task 3.
#
# The additional worker completes task 2.
#
# Example 2:
#
# Input: workers = [10,10000,100000000], tasks = [[1,100]]
#
# Output: 100
#
# Explanation:
#
# Since no worker matches the skill requirement, only the additional
# worker can complete task 0.
#
# Example 3:
#
# Input: workers = [7], tasks = [[3,3],[3,3]]
#
# Output: 3
#
# Explanation:
#
# The additional worker completes task 1. Worker 0 cannot work since no
# task has a skill requirement of 7.
#
# Constraints:
#
# 1 <= workers.length <= 10^5
#
# 1 <= workers[i] <= 10^9
#
# 1 <= tasks.length <= 10^5
#
# tasks[i].length == 2
#
# 1 <= tasks[i][0], tasks[i][1] <= 10^9
#

# @lc code=start
import collections
import heapq
from typing import List


class Solution:
    def maxProfit(self, workers: List[int], tasks: List[List[int]]) -> int:
        """
        Interview explanation:
        Skill-matched workers each take at most one equal-skill task; one
        wildcard worker may take any leftover task. Greedily assign highest
        profits per skill, then give the wildcard the best remainder.

        Algorithm:
        - Group task profits by skill in max-heaps.
        - For each worker, pop the best matching profit if any.
        - Extra profit = max heap-top among remaining heaps.

        Complexity: O(T log T + W log T) time, O(T) space.
        """
        skill_heaps: dict = collections.defaultdict(list)
        for skill, profit in tasks:
            heapq.heappush(skill_heaps[skill], -profit)

        total = 0
        for skill in workers:
            if skill_heaps[skill]:
                total += -heapq.heappop(skill_heaps[skill])

        extra = 0
        for heap in skill_heaps.values():
            if heap:
                extra = max(extra, -heap[0])
        return total + extra
# @lc code=end

