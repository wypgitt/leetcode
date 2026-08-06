#
# @lc app=leetcode id=1598 lang=python3
#
# [1598] Crawler Log Folder
#
# https://leetcode.com/problems/crawler-log-folder/description/
#
# algorithms
# Easy (71.7%)
# Likes:    1564
# Dislikes: 99
# Total Accepted:    299K
# Total Submissions: 417K
# Testcase Example:  "[\"d1/\",\"d2/\",\"../\",\"d21/\",\"./\"]"
#
# The Leetcode file system keeps a log each time some user performs a change
# folder operation.
#
# The operations are described below:
#
# "../" : Move to the parent folder of the current folder. (If you are already
# in the main folder, remain in the same folder).
#
# "./" : Remain in the same folder.
#
# "x/" : Move to the child folder named x (This folder is guaranteed to always
# exist).
#
# You are given a list of strings logs where logs[i] is the operation performed
# by the user at the i^th step.
#
# The file system starts in the main folder, then the operations in logs are
# performed.
#
# Return the minimum number of operations needed to go back to the main folder
# after the change folder operations.
#
# Example 1:
#
# Input: logs = ["d1/","d2/","../","d21/","./"]
# Output: 2
# Explanation: Use this change folder operation "../" 2 times and go back to
# the main folder.
#
# Example 2:
#
# Input: logs = ["d1/","d2/","./","d3/","../","d31/"]
# Output: 3
#
# Example 3:
#
# Input: logs = ["d1/","../","../","../"]
# Output: 0
#
# Constraints:
#
# 1 <= logs.length <= 10^3
#
# 2 <= logs[i].length <= 10
#
# logs[i] contains lowercase English letters, digits, '.', and '/'.
#
# logs[i] follows the format described in the statement.
#
# Folder names consist of lowercase English letters and digits.
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, logs: List[str]) -> int:
        """
        Interview explanation:
        Track folder depth: "../" goes up (not below 0), "./" stays, "x/" down.
        Answer is final depth (ops to return to main).

        Algorithm (counter):
        - depth=0; for log: ../ → max(0,depth-1); ./ → noop; else depth+=1.

        Complexity: O(n) time, O(1) space.
        """
        depth = 0
        for log in logs:
            if log == "../":
                depth = max(0, depth - 1)
            elif log != "./":
                depth += 1
        return depth

    def minOperations_stack(self, logs: List[str]) -> int:
        """
        Interview explanation:
        Alternate explicit stack of folder names; return len(stack).

        Algorithm:
        - stack=[]; apply logs; return len(stack).

        Complexity: O(n) time/space.
        """
        stack = []
        for log in logs:
            if log == "../":
                if stack:
                    stack.pop()
            elif log != "./":
                stack.append(log)
        return len(stack)
# @lc code=end

