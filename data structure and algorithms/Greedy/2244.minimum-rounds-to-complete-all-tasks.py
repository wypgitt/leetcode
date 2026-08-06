#
# @lc app=leetcode id=2244 lang=python3
#
# [2244] Minimum Rounds to Complete All Tasks
#
# https://leetcode.com/problems/minimum-rounds-to-complete-all-tasks/description/
#
# algorithms
# Medium (63.37%)
# Likes:    2859
# Dislikes: 86
# Total Accepted:    177K
# Total Submissions: 279.2K
# Testcase Example:  "[2,2,3,3,2,4,4,4,4,4]"
#
# You are given a 0-indexed integer array tasks, where tasks[i] represents the
# difficulty level of a task. In each round, you can complete either 2 or 3
# tasks of the same difficulty level.
#
# Return the minimum rounds required to complete all the tasks, or -1 if it is
# not possible to complete all the tasks.
#
#
#
# Example 1:
#
# Input: tasks = [2,2,3,3,2,4,4,4,4,4]
# Output: 4
# Explanation: To complete all the tasks, a possible plan is:
# - In the first round, you complete 3 tasks of difficulty level 2.
# - In the second round, you complete 2 tasks of difficulty level 3.
# - In the third round, you complete 3 tasks of difficulty level 4.
# - In the fourth round, you complete 2 tasks of difficulty level 4.
# It can be shown that all the tasks cannot be completed in fewer than 4 rounds,
# so the answer is 4.
#
# Example 2:
#
# Input: tasks = [2,3,3]
# Output: -1
# Explanation: There is only 1 task of difficulty level 2, but in each round,
# you can only complete either 2 or 3 tasks of the same difficulty level. Hence,
# you cannot complete all the tasks, and the answer is -1.
#
#
#
# Constraints:
#
#
# 1 <= tasks.length <= 10^5
#
#
# 1 <= tasks[i] <= 10^9
#
#
#
# Note: This question is the same as 2870: Minimum Number of Operations to Make
# Array Empty.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def minimumRounds(self, tasks: List[int]) -> int:
        """
        Interview explanation:
        Each round completes 2 or 3 tasks of the same difficulty. Min rounds for
        all tasks, or -1 if some difficulty has count 1.

        Algorithm:
        - For count c: if c==1 impossible; else rounds = ceil(c/3) =
          (c+2)//3.

        Complexity: O(n) time, O(n) space.
        """
        ans = 0
        for c in Counter(tasks).values():
            if c == 1:
                return -1
            ans += (c + 2) // 3
        return ans
# @lc code=end
