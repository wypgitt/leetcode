#
# @lc app=leetcode id=621 lang=python3
#
# [621] Task Scheduler
#
# https://leetcode.com/problems/task-scheduler/description/
#
# algorithms
# Medium (63.56%)
# Likes:    12030
# Dislikes: 2240
# Total Accepted:    1.0M
# Total Submissions: 1.6M
# Testcase Example:  "[\"A\",\"A\",\"A\",\"B\",\"B\",\"B\"]"
#
# You are given an array of CPU tasks, each labeled with a letter from A to Z,
# and a number n. Each CPU interval can be idle or allow the completion of one
# task. Tasks can be completed in any order, but there's a constraint: there
# has to be a gap of at least n intervals between two tasks with the same
# label.
#
# Return the minimum number of CPU intervals required to complete all tasks.
#
# Example 1:
#
# Input: tasks = ["A","A","A","B","B","B"], n = 2
#
# Output: 8
#
# Explanation: A possible sequence is: A -> B -> idle -> A -> B -> idle -> A ->
# B.
#
# After completing task A, you must wait two intervals before doing A again.
# The same applies to task B. In the 3^rd interval, neither A nor B can be
# done, so you idle. By the 4^th interval, you can do A again as 2 intervals
# have passed.
#
# Example 2:
#
# Input: tasks = ["A","C","A","B","D","B"], n = 1
#
# Output: 6
#
# Explanation: A possible sequence is: A -> B -> C -> D -> A -> B.
#
# With a cooling interval of 1, you can repeat a task after just one other
# task.
#
# Example 3:
#
# Input: tasks = ["A","A","A", "B","B","B"], n = 3
#
# Output: 10
#
# Explanation: A possible sequence is: A -> B -> idle -> idle -> A -> B -> idle
# -> idle -> A -> B.
#
# There are only two types of tasks, A and B, which need to be separated by 3
# intervals. This leads to idling twice between repetitions of these tasks.
#
# Constraints:
#
# 1 <= tasks.length <= 10^4
#
# tasks[i] is an uppercase English letter.
#
# 0 <= n <= 100
#

# @lc code=start

from collections import Counter
from typing import List


class Solution:
    def leastInterval(self, tasks: List[str], n: int) -> int:
        """
        Interview explanation:
        Cool-down n between same tasks. Bottleneck is the most frequent task:
        schedule it with n idle slots between, then fill slots with other tasks.

        Algorithm:
        - Let maxf = max frequency, cnt = #tasks with frequency maxf.
        - Formula: max(len(tasks), (maxf - 1) * (n + 1) + cnt).

        Complexity: O(N) time, O(1) space (26 letters) / O(U) for Counter.
        """
        freq = Counter(tasks)
        maxf = max(freq.values())
        cnt = sum(1 for v in freq.values() if v == maxf)
        return max(len(tasks), (maxf - 1) * (n + 1) + cnt)
# @lc code=end
