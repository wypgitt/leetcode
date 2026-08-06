#
# @lc app=leetcode id=1376 lang=python3
#
# [1376] Time Needed to Inform All Employees
#
# https://leetcode.com/problems/time-needed-to-inform-all-employees/description/
#
# algorithms
# Medium (60.56%)
# Likes:    4279
# Dislikes: 329
# Total Accepted:    265K
# Total Submissions: 437K
# Testcase Example:  "1"
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
# Example 1:
#
# Input: n = 1, headID = 0, manager = [-1], informTime = [0]
# Output: 0
# Explanation: The head of the company is the only employee in the company.
#
# Example 2:
#
# Input: n = 6, headID = 2, manager = [2,2,-1,2,2,2], informTime =
# [0,0,1,0,0,0]
# Output: 1
# Explanation: The head of the company with id = 2 is the direct manager of all
# the employees in the company and needs 1 minute to inform them all.
# The tree structure of the employees in the company is shown.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 0 <= headID < n
#
# manager.length == n
#
# 0 <= manager[i] < n
#
# manager[headID] == -1
#
# informTime.length == n
#
# 0 <= informTime[i] <= 1000
#
# informTime[i] == 0 if employee i has no subordinates.
#
# It is guaranteed that all the employees can be informed.
#

# @lc code=start

from collections import defaultdict, deque
from typing import List


class Solution:
    def numOfMinutes(self, n: int, headID: int, manager: List[int], informTime: List[int]) -> int:
        """
        Interview explanation:
        Company tree: manager[i]→i edges. Time to inform all = max path sum of
        informTime along the tree from head (each node delays its subtree by informTime[node]).

        Algorithm (BFS/DFS):
        - Build children adjacency; DFS/BFS accumulate time; return max

        Complexity: O(n) time, O(n) space.
        """
        children = defaultdict(list)
        for i, m in enumerate(manager):
            if m != -1:
                children[m].append(i)

        def dfs(u: int) -> int:
            best = 0
            for v in children[u]:
                best = max(best, dfs(v))
            return informTime[u] + best

        return dfs(headID)

    def numOfMinutes_bfs(self, n: int, headID: int, manager: List[int], informTime: List[int]) -> int:
        """
        Interview explanation:
        Alternate BFS from head accumulating time to each employee; track max.

        Algorithm:
        - Build children; queue (node, time_so_far); max time when visiting

        Complexity: O(n) time, O(n) space.
        """
        children = defaultdict(list)
        for i, m in enumerate(manager):
            if m != -1:
                children[m].append(i)
        ans = 0
        q = deque([(headID, 0)])
        while q:
            u, t = q.popleft()
            ans = max(ans, t)
            for v in children[u]:
                q.append((v, t + informTime[u]))
        return ans
# @lc code=end
