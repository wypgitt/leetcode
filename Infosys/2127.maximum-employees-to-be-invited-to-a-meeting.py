#
# @lc app=leetcode id=2127 lang=python3
#
# [2127] Maximum Employees to Be Invited to a Meeting
#
# https://leetcode.com/problems/maximum-employees-to-be-invited-to-a-meeting/description/
#
# algorithms
# Hard (61.76%)
# Likes:    1704
# Dislikes: 70
# Total Accepted:    90.4K
# Total Submissions: 146.4K
# Testcase Example:  "[2,2,1,2]"
#
# A company is organizing a meeting and has a list of n employees, waiting to be
# invited. They have arranged for a large circular table, capable of seating any
# number of employees.
#
# The employees are numbered from 0 to n - 1. Each employee has a favorite
# person and they will attend the meeting only if they can sit next to their
# favorite person at the table. The favorite person of an employee is not
# themself.
#
# Given a 0-indexed integer array favorite, where favorite[i] denotes the
# favorite person of the i^th employee, return the maximum number of employees
# that can be invited to the meeting.
#
#
#
# Example 1:
#
# Input: favorite = [2,2,1,2]
# Output: 3
# Explanation:
# The above figure shows how the company can invite employees 0, 1, and 2, and
# seat them at the round table.
# All employees cannot be invited because employee 2 cannot sit beside employees
# 0, 1, and 3, simultaneously.
# Note that the company can also invite employees 1, 2, and 3, and give them
# their desired seats.
# The maximum number of employees that can be invited to the meeting is 3.
#
# Example 2:
#
# Input: favorite = [1,2,0]
# Output: 3
# Explanation:
# Each employee is the favorite person of at least one other employee, and the
# only way the company can invite them is if they invite every employee.
# The seating arrangement will be the same as that in the figure given in
# example 1:
# - Employee 0 will sit between employees 2 and 1.
# - Employee 1 will sit between employees 0 and 2.
# - Employee 2 will sit between employees 1 and 0.
# The maximum number of employees that can be invited to the meeting is 3.
#
# Example 3:
#
# Input: favorite = [3,0,1,4,1]
# Output: 4
# Explanation:
# The above figure shows how the company will invite employees 0, 1, 3, and 4,
# and seat them at the round table.
# Employee 2 cannot be invited because the two spots next to their favorite
# employee 1 are taken.
# So the company leaves them out of the meeting.
# The maximum number of employees that can be invited to the meeting is 4.
#
#
#
# Constraints:
#
#
# n == favorite.length
#
#
# 2 <= n <= 10^5
#
#
# 0 <= favorite[i] <= n - 1
#
#
# favorite[i] != i
#


# @lc code=start
from typing import List
from collections import deque


class Solution:
    def maximumInvitations(self, favorite: List[int]) -> int:
        """
        Interview explanation:
        Each person favorites one other; seating is a circle where each sits
        next to their favorite. Max invitees = max of:
        (1) longest cycle length, or
        (2) sum over mutual pairs (2-cycles) of (2 + longest chains into each).

        Algorithm:
        - Indegree + topo to peel chains; track depth into each node.
        - Detect cycles on remaining; handle len==2 specially with chain depths.

        Complexity: O(n) time, O(n) space.
        """
        n = len(favorite)
        indeg = [0] * n
        for f in favorite:
            indeg[f] += 1
        depth = [1] * n
        q = deque(i for i in range(n) if indeg[i] == 0)
        while q:
            u = q.popleft()
            v = favorite[u]
            depth[v] = max(depth[v], depth[u] + 1)
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

        max_cycle = 0
        two_cycle_sum = 0
        for i in range(n):
            if indeg[i] == 0:
                continue
            # walk cycle
            length = 0
            u = i
            while indeg[u] > 0:
                indeg[u] = 0
                length += 1
                u = favorite[u]
            if length == 2:
                # i and favorite[i]
                two_cycle_sum += depth[i] + depth[favorite[i]]
            else:
                max_cycle = max(max_cycle, length)
        return max(max_cycle, two_cycle_sum)
# @lc code=end

