#
# @lc app=leetcode id=1834 lang=python3
#
# [1834] Single-Threaded CPU
#
# https://leetcode.com/problems/single-threaded-cpu/description/
#
# algorithms
# Medium (47.94%)
# Likes:    3550
# Dislikes: 294
# Total Accepted:    164K
# Total Submissions: 343K
# Testcase Example:  "[[1,2],[2,4],[3,2],[4,1]]"
#
# You are given n tasks labeled from 0 to n - 1 represented by a 2D integer
# array tasks, where tasks[i] = [enqueueTime_i, processingTime_i] means that
# the i^th task will be available to process at enqueueTime_i and will take
# processingTime_i_ to finish processing.
#
# You have a single-threaded CPU that can process at most one task at a time
# and will act in the following way:
#
# If the CPU is idle and there are no available tasks to process, the CPU
# remains idle.
#
# If the CPU is idle and there are available tasks, the CPU will choose the one
# with the shortest processing time. If multiple tasks have the same shortest
# processing time, it will choose the task with the smallest index.
#
# Once a task is started, the CPU will process the entire task without
# stopping.
#
# The CPU can finish a task then start a new one instantly.
#
# Return the order in which the CPU will process the tasks.
#
# Example 1:
#
# Input: tasks = [[1,2],[2,4],[3,2],[4,1]]
# Output: [0,2,3,1]
# Explanation: The events go as follows:
# - At time = 1, task 0 is available to process. Available tasks = {0}.
# - Also at time = 1, the idle CPU starts processing task 0. Available tasks =
# {}.
# - At time = 2, task 1 is available to process. Available tasks = {1}.
# - At time = 3, task 2 is available to process. Available tasks = {1, 2}.
# - Also at time = 3, the CPU finishes task 0 and starts processing task 2 as
# it is the shortest. Available tasks = {1}.
# - At time = 4, task 3 is available to process. Available tasks = {1, 3}.
# - At time = 5, the CPU finishes task 2 and starts processing task 3 as it is
# the shortest. Available tasks = {1}.
# - At time = 6, the CPU finishes task 3 and starts processing task 1.
# Available tasks = {}.
# - At time = 10, the CPU finishes task 1 and becomes idle.
#
# Example 2:
#
# Input: tasks = [[7,10],[7,12],[7,5],[7,4],[7,2]]
# Output: [4,3,2,0,1]
# Explanation: The events go as follows:
# - At time = 7, all the tasks become available. Available tasks = {0,1,2,3,4}.
# - Also at time = 7, the idle CPU starts processing task 4. Available tasks =
# {0,1,2,3}.
# - At time = 9, the CPU finishes task 4 and starts processing task 3.
# Available tasks = {0,1,2}.
# - At time = 13, the CPU finishes task 3 and starts processing task 2.
# Available tasks = {0,1}.
# - At time = 18, the CPU finishes task 2 and starts processing task 0.
# Available tasks = {1}.
# - At time = 28, the CPU finishes task 0 and starts processing task 1.
# Available tasks = {}.
# - At time = 40, the CPU finishes task 1 and becomes idle.
#
# Constraints:
#
# 1 <= tasks.length <= 10^5
#
# tasks[i] = [enqueueTime_i, processingTime_i]
#
# 1 <= enqueueTime_i, processingTime_i <= 10^9
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def getOrder(self, tasks: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Single-threaded CPU: available tasks in min-heap by (processingTime, index);
        clock jumps to next enqueue if idle.

        Algorithm (heap):
        - Sort tasks by enqueue time keeping index; time=0; while pending/available:
          push all with enqueue<=time; if heap empty jump time; else pop process.

        Complexity: O(n log n) time, O(n) space.
        """
        indexed = sorted((e, p, i) for i, (e, p) in enumerate(tasks))
        ans = []
        heap = []
        time = i = 0
        n = len(tasks)
        while len(ans) < n:
            while i < n and indexed[i][0] <= time:
                e, p, idx = indexed[i]
                heapq.heappush(heap, (p, idx))
                i += 1
            if not heap:
                time = indexed[i][0]
                continue
            p, idx = heapq.heappop(heap)
            time += p
            ans.append(idx)
        return ans
# @lc code=end
