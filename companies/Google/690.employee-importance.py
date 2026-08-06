#
# @lc app=leetcode id=690 lang=python3
#
# [690] Employee Importance
#
# https://leetcode.com/problems/employee-importance/description/
#
# algorithms
# Medium (69.68%)
# Likes:    2226
# Dislikes: 1360
# Total Accepted:    259K
# Total Submissions: 371K
# Testcase Example:  "[[1,5,[2,3]],[2,3,[]],[3,3,[]]]"
#
# You have a data structure of employee information, including the employee's
# unique ID, importance value, and direct subordinates' IDs.
#
# You are given an array of employees employees where:
#
# employees[i].id is the ID of the i^th employee.
#
# employees[i].importance is the importance value of the i^th employee.
#
# employees[i].subordinates is a list of the IDs of the direct subordinates of
# the i^th employee.
#
# Given an integer id that represents an employee's ID, return the total
# importance value of this employee and all their direct and indirect
# subordinates.
#
# Example 1:
#
# Input: employees = [[1,5,[2,3]],[2,3,[]],[3,3,[]]], id = 1
# Output: 11
# Explanation: Employee 1 has an importance value of 5 and has two direct
# subordinates: employee 2 and employee 3.
# They both have an importance value of 3.
# Thus, the total importance value of employee 1 is 5 + 3 + 3 = 11.
#
# Example 2:
#
# Input: employees = [[1,2,[5]],[5,-3,[]]], id = 5
# Output: -3
# Explanation: Employee 5 has an importance value of -3 and has no direct
# subordinates.
# Thus, the total importance value of employee 5 is -3.
#
# Constraints:
#
# 1 <= employees.length <= 2000
#
# 1 <= employees[i].id <= 2000
#
# All employees[i].id are unique.
#
# -100 <= employees[i].importance <= 100
#
# One employee has at most one direct leader and may have several subordinates.
#
# The IDs in employees[i].subordinates are valid IDs.
#

# @lc code=start
from collections import deque
from typing import List

"""
# Definition for Employee.
class Employee:
    def __init__(self, id: int, importance: int, subordinates: List[int]):
        self.id = id
        self.importance = importance
        self.subordinates = subordinates
"""


class Solution:
    def getImportance(self, employees: List["Employee"], id: int) -> int:
        """
        Interview explanation:
        Total importance of an employee plus all subordinates (transitive).
        Build id -> Employee map; DFS or BFS accumulate importance.

        Algorithm:
        - Map employees by id. DFS/BFS from id summing importance and enqueueing
          subordinates.

        Complexity: O(n) time, O(n) space.
        """
        emp = {e.id: e for e in employees}

        def dfs(eid: int) -> int:
            e = emp[eid]
            return e.importance + sum(dfs(s) for s in e.subordinates)

        return dfs(id)

    def getImportanceBFS(self, employees: List["Employee"], id: int) -> int:
        """
        Interview explanation:
        Same aggregation via BFS/queue over the subordinate graph.

        Algorithm:
        - Queue starting at id; pop, add importance, push subordinates.

        Complexity: O(n) time, O(n) space.
        """
        emp = {e.id: e for e in employees}
        ans = 0
        q = deque([id])
        while q:
            e = emp[q.popleft()]
            ans += e.importance
            q.extend(e.subordinates)
        return ans
# @lc code=end
