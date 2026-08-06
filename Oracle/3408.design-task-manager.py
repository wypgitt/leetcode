#
# @lc app=leetcode id=3408 lang=python3
#
# [3408] Design Task Manager
#
# https://leetcode.com/problems/design-task-manager/description/
#
# algorithms
# Medium (48.89%)
# Likes:    493
# Dislikes: 53
# Total Accepted:    103.9K
# Total Submissions: 212.5K
# Testcase Example:  "[\"TaskManager\",\"add\",\"edit\",\"execTop\",\"rmv\",\"add\",\"execTop\"]\n[[[[1,101,10],[2,102,20],[3,103,15]]],[4,104,5],[102,8],[],[101],[5,105,15],[]]"
#
#
# There is a task management system that allows users to manage their
# tasks, each associated with a priority. The system should efficiently
# handle adding, modifying, executing, and removing tasks.
#
# Implement the TaskManager class:
#
# TaskManager(vector<vector<int>>& tasks) initializes the task manager
# with a list of user-task-priority triples. Each element in the input
# list is of the form [userId, taskId, priority], which adds a task to the
# specified user with the given priority.
#
# void add(int userId, int taskId, int priority) adds a task with the
# specified taskId and priority to the user with userId. It is guaranteed
# that taskId does not exist in the system.
#
# void edit(int taskId, int newPriority) updates the priority of the
# existing taskId to newPriority. It is guaranteed that taskId exists in
# the system.
#
# void rmv(int taskId) removes the task identified by taskId from the
# system. It is guaranteed that taskId exists in the system.
#
# int execTop() executes the task with the highest priority across all
# users. If there are multiple tasks with the same highest priority,
# execute the one with the highest taskId. After executing, the taskId is
# removed from the system. Return the userId associated with the executed
# task. If no tasks are available, return -1.
#
# Note that a user may be assigned multiple tasks.
#
# Example 1:
#
# Input:
#
# ["TaskManager", "add", "edit", "execTop", "rmv", "add", "execTop"]
#
# [[[[1, 101, 10], [2, 102, 20], [3, 103, 15]]], [4, 104, 5], [102, 8],
# [], [101], [5, 105, 15], []]
#
# Output:
#
# [null, null, null, 3, null, null, 5]
#
# Explanation
#
# TaskManager taskManager = new TaskManager([[1, 101, 10], [2, 102, 20],
# [3, 103, 15]]); // Initializes with three tasks for Users 1, 2, and 3.
#
# taskManager.add(4, 104, 5); // Adds task 104 with priority 5 for User 4.
#
# taskManager.edit(102, 8); // Updates priority of task 102 to 8.
#
# taskManager.execTop(); // return 3. Executes task 103 for User 3.
#
# taskManager.rmv(101); // Removes task 101 from the system.
#
# taskManager.add(5, 105, 15); // Adds task 105 with priority 15 for User
# 5.
#
# taskManager.execTop(); // return 5. Executes task 105 for User 5.
#
# Constraints:
#
# 1 <= tasks.length <= 10^5
#
# 0 <= userId <= 10^5
#
# 0 <= taskId <= 10^5
#
# 0 <= priority <= 10^9
#
# 0 <= newPriority <= 10^9
#
# At most 2 * 10^5 calls will be made in total to add, edit, rmv, and
# execTop methods.
#
# The input is generated such that taskId will be valid.
#

# @lc code=start
import heapq
from typing import Dict, List, Tuple


class TaskManager:
    """
    Interview explanation:
    Support add/edit/rmv and execTop (highest priority, then highest taskId).
    Use a max-heap of (-priority, -taskId) with lazy deletion against a
    taskId -> (userId, priority) map.

    Algorithm:
    - task maps taskId to current (userId, priority).
    - heap stores versions; pop until top matches the map, then execute.

    Complexity: O(log n) amortized per op; O(n) space.
    """

    def __init__(self, tasks: List[List[int]]):
        self.task: Dict[int, Tuple[int, int]] = {}
        self.heap: List[Tuple[int, int]] = []
        for userId, taskId, priority in tasks:
            self.add(userId, taskId, priority)

    def add(self, userId: int, taskId: int, priority: int) -> None:
        """
        Interview explanation:
        Insert a new task for userId.

        Algorithm:
        - Record mapping and push (-priority, -taskId) onto the heap.

        Complexity: O(log n) time.
        """
        self.task[taskId] = (userId, priority)
        heapq.heappush(self.heap, (-priority, -taskId))

    def edit(self, taskId: int, newPriority: int) -> None:
        """
        Interview explanation:
        Update an existing task's priority (lazy heap update).

        Algorithm:
        - Overwrite map priority; push a new heap entry.

        Complexity: O(log n) time.
        """
        userId, _ = self.task[taskId]
        self.task[taskId] = (userId, newPriority)
        heapq.heappush(self.heap, (-newPriority, -taskId))

    def rmv(self, taskId: int) -> None:
        """
        Interview explanation:
        Remove taskId from the system (lazy heap invalidation).

        Algorithm:
        - Delete from map; stale heap entries are skipped later.

        Complexity: O(1) time.
        """
        del self.task[taskId]

    def execTop(self) -> int:
        """
        Interview explanation:
        Execute the highest-priority task (highest taskId on ties); return
        its userId, or -1 if none.

        Algorithm:
        - Pop heap until entry matches current map priority; then remove
          and return userId.

        Complexity: O(log n) amortized time.
        """
        while self.heap:
            neg_p, neg_t = heapq.heappop(self.heap)
            taskId = -neg_t
            if taskId in self.task and self.task[taskId][1] == -neg_p:
                userId, _ = self.task.pop(taskId)
                return userId
        return -1


# Your TaskManager object will be instantiated and called as such:
# obj = TaskManager(tasks)
# obj.add(userId,taskId,priority)
# obj.edit(taskId,newPriority)
# obj.rmv(taskId)
# param_4 = obj.execTop()
# @lc code=end
