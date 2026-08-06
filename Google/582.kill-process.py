#
# @lc app=leetcode id=582 lang=python3
#
# [582] Kill Process
#
# https://leetcode.com/problems/kill-process/description/
#
# algorithms
# Medium (70.66%)
# Likes:    1141
# Dislikes: 22
# Total Accepted:    98K
# Total Submissions: 138.7K
# Testcase Example:  '[1,3,10,5]\n[3,0,5,3]\n5'
#
# You have n processes forming a rooted tree structure. You are given two
# integer arrays pid and ppid, where pid[i] is the ID of the i^th process and
# ppid[i] is the ID of the i^th process's parent process.
# 
# Each process has only one parent process but may have multiple children
# processes. Only one process has ppid[i] = 0, which means this process has no
# parent process (the root of the tree).
# 
# When a process is killed, all of its children processes will also be killed.
# 
# Given an integer kill representing the ID of a process you want to kill,
# return a list of the IDs of the processes that will be killed. You may return
# the answer in any order.
# 
# 
# Example 1:
# 
# 
# Input: pid = [1,3,10,5], ppid = [3,0,5,3], kill = 5
# Output: [5,10]
# Explanation: The processes colored in red are the processes that should be
# killed.
# 
# 
# Example 2:
# 
# 
# Input: pid = [1], ppid = [0], kill = 1
# Output: [1]
# 
# 
# 
# Constraints:
# 
# 
# n == pid.length
# n == ppid.length
# 1 <= n <= 5 * 10^4
# 1 <= pid[i] <= 5 * 10^4
# 0 <= ppid[i] <= 5 * 10^4
# Only one process has no parent.
# All the values of pid are unique.
# kill is guaranteed to be in pid.
# 
# 
#

# @lc code=start
from collections import defaultdict, deque
from typing import List


class Solution:
    def killProcess(self, pid: List[int], ppid: List[int], kill: int) -> List[int]:
        children = defaultdict(list)
        for child, parent in zip(pid, ppid):
            children[parent].append(child)

        ans = []
        q = deque([kill])
        while q:
            cur = q.popleft()
            ans.append(cur)
            q.extend(children[cur])
        return ans
# @lc code=end

"""
Interview explanation:
The parent process relation is a rooted forest. Killing one process kills the entire subtree under it. Build an adjacency list from parent to children, then BFS or DFS from kill.

Data structure: defaultdict(list) stores children for each parent; a queue performs traversal.

Edge cases: if the killed process has no children, the answer is just [kill]. Parent id 0 represents the root parent and can be present in the map harmlessly.

Complexity: building the graph is O(n), and the traversal visits only killed descendants, O(k). Space is O(n) for the adjacency list.
"""
