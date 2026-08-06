#
# @lc app=leetcode id=1101 lang=python3
#
# [1101] The Earliest Moment When Everyone Become Friends
#
# https://leetcode.com/problems/the-earliest-moment-when-everyone-become-friends/description/
#
# algorithms
# Medium (66.13%)
# Likes:    1125
# Dislikes: 42
# Total Accepted:    138.3K
# Total Submissions: 209.2K
# Testcase Example:  "[[20190101,0,1],[20190104,3,4],[20190107,2,3],[20190211,1,5],[20190224,2,4],[20190301,0,3],[20190312,1,2],[20190322,4,5]]\n6"
#
#
# There are n people in a social group labeled from 0 to n - 1. You are
# given an array logs where logs[i] = [timestamp_i, x_i, y_i] indicates
# that x_i and y_i will be friends at the time timestamp_i.
#
# Friendship is symmetric. That means if a is friends with b, then b is
# friends with a. Also, person a is acquainted with a person b if a is
# friends with b, or a is a friend of someone acquainted with b.
#
# Return the earliest time for which every person became acquainted with
# every other person. If there is no such earliest time, return -1.
#
# Example 1:
#
# Input: logs =
# [[20190101,0,1],[20190104,3,4],[20190107,2,3],[20190211,1,5],[20190224,2,4],[20190301,0,3],[20190312,1,2],[20190322,4,5]],
# n = 6
# Output: 20190301
# Explanation:
# The first event occurs at timestamp = 20190101, and after 0 and 1 become
# friends, we have the following friendship groups [0,1], [2], [3], [4],
# [5].
# The second event occurs at timestamp = 20190104, and after 3 and 4
# become friends, we have the following friendship groups [0,1], [2],
# [3,4], [5].
# The third event occurs at timestamp = 20190107, and after 2 and 3 become
# friends, we have the following friendship groups [0,1], [2,3,4], [5].
# The fourth event occurs at timestamp = 20190211, and after 1 and 5
# become friends, we have the following friendship groups [0,1,5],
# [2,3,4].
# The fifth event occurs at timestamp = 20190224, and as 2 and 4 are
# already friends, nothing happens.
# The sixth event occurs at timestamp = 20190301, and after 0 and 3 become
# friends, we all become friends.
#
# Example 2:
#
# Input: logs = [[0,2,0],[1,0,1],[3,0,3],[4,1,2],[7,3,1]], n = 4
# Output: 3
# Explanation: At timestamp = 3, all the persons (i.e., 0, 1, 2, and 3)
# become friends.
#
# Constraints:
#
# 2 <= n <= 100
#
# 1 <= logs.length <= 10^4
#
# logs[i].length == 3
#
# 0 <= timestamp_i <= 10^9
#
# 0 <= x_i, y_i <= n - 1
#
# x_i != y_i
#
# All the values timestamp_i are unique.
#
# All the pairs (x_i, y_i) occur at most one time in the input.
#
# @lc code=start
from typing import List


class Solution:
    def earliestAcq(self, logs: List[List[int]], n: int) -> int:
        """
        Interview explanation:
        Premium. Friendship is transitive; process logs by time and union
        people. When components become 1, return that timestamp; else -1.

        Algorithm (Union-Find):
        - Sort logs by timestamp.
        - UF with path compression + union by rank; components = n.
        - On successful union: components--; if 1 return time.

        Complexity: O(M log M + M α(n)) time, O(n) space.
        """
        parent = list(range(n))
        rank = [0] * n
        components = n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> bool:
            nonlocal components
            ra, rb = find(a), find(b)
            if ra == rb:
                return False
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1
            components -= 1
            return True

        for t, a, b in sorted(logs):
            union(a, b)
            if components == 1:
                return t
        return -1
# @lc code=end
