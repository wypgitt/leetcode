#
# @lc app=leetcode id=841 lang=python3
#
# [841] Keys and Rooms
#
# https://leetcode.com/problems/keys-and-rooms/description/
#
# algorithms
# Medium (76.1%)
# Likes:    6745
# Dislikes: 303
# Total Accepted:    726K
# Total Submissions: 954K
# Testcase Example:  "[[1],[2],[3],[]]"
#
# There are n rooms labeled from 0 to n - 1 and all the rooms are locked except
# for room 0. Your goal is to visit all the rooms. However, you cannot enter a
# locked room without having its key.
#
# When you visit a room, you may find a set of distinct keys in it. Each key
# has a number on it, denoting which room it unlocks, and you can take all of
# them with you to unlock the other rooms.
#
# Given an array rooms where rooms[i] is the set of keys that you can obtain if
# you visited room i, return true if you can visit all the rooms, or false
# otherwise.
#
# Example 1:
#
# Input: rooms = [[1],[2],[3],[]]
# Output: true
# Explanation:
# We visit room 0 and pick up key 1.
# We then visit room 1 and pick up key 2.
# We then visit room 2 and pick up key 3.
# We then visit room 3.
# Since we were able to visit every room, we return true.
#
# Example 2:
#
# Input: rooms = [[1,3],[3,0,1],[2],[0]]
# Output: false
# Explanation: We can not enter room number 2 since the only key that unlocks
# it is in that room.
#
# Constraints:
#
# n == rooms.length
#
# 2 <= n <= 1000
#
# 0 <= rooms[i].length <= 1000
#
# 1 <= sum(rooms[i].length) <= 3000
#
# 0 <= rooms[i][j] < n
#
# All the values of rooms[i] are unique.
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def canVisitAllRooms(self, rooms: List[List[int]]) -> bool:
        """
        Interview explanation:
        Room graph: edge i→key means you can visit that room. Start from 0;
        DFS visit all reachable; success iff all n rooms visited.

        Algorithm (DFS):
        - visited set; stack/recursion from 0; explore keys as edges.

        Complexity: O(n + keys) time, O(n) space.
        """
        n = len(rooms)
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v in rooms[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen) == n

    def canVisitAllRooms_bfs(self, rooms: List[List[int]]) -> bool:
        """
        Interview explanation:
        Alternate classic BFS from room 0; same reachability check.

        Algorithm:
        - Queue BFS; mark visited; return len(visited)==n.

        Complexity: O(n + keys) time, O(n) space.
        """
        n = len(rooms)
        seen = {0}
        q = deque([0])
        while q:
            u = q.popleft()
            for v in rooms[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return len(seen) == n
# @lc code=end
