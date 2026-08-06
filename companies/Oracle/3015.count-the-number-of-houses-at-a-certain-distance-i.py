#
# @lc app=leetcode id=3015 lang=python3
#
# [3015] Count the Number of Houses at a Certain Distance I
#
# https://leetcode.com/problems/count-the-number-of-houses-at-a-certain-distance-i/description/
#
# algorithms
# Medium (58.37%)
# Likes:    225
# Dislikes: 46
# Total Accepted:    28.9K
# Total Submissions: 49.5K
# Testcase Example:  "3\n1\n3"
#
#
# You are given three positive integers n, x, and y.
#
# In a city, there exist houses numbered 1 to n connected by n streets.
# There is a street connecting the house numbered i with the house
# numbered i + 1 for all 1 <= i <= n - 1 . An additional street connects
# the house numbered x with the house numbered y.
#
# For each k, such that 1 <= k <= n, you need to find the number of pairs
# of houses (house_1, house_2) such that the minimum number of streets
# that need to be traveled to reach house_2 from house_1 is k.
#
# Return a 1-indexed array result of length n where result[k] represents
# the total number of pairs of houses such that the minimum streets
# required to reach one house from the other is k.
#
# Note that x and y can be equal.
#
# Example 1:
#
# Input: n = 3, x = 1, y = 3
# Output: [6,0,0]
# Explanation: Let's look at each pair of houses:
# - For the pair (1, 2), we can go from house 1 to house 2 directly.
# - For the pair (2, 1), we can go from house 2 to house 1 directly.
# - For the pair (1, 3), we can go from house 1 to house 3 directly.
# - For the pair (3, 1), we can go from house 3 to house 1 directly.
# - For the pair (2, 3), we can go from house 2 to house 3 directly.
# - For the pair (3, 2), we can go from house 3 to house 2 directly.
#
# Example 2:
#
# Input: n = 5, x = 2, y = 4
# Output: [10,8,2,0,0]
# Explanation: For each distance k the pairs are:
# - For k == 1, the pairs are (1, 2), (2, 1), (2, 3), (3, 2), (2, 4), (4,
# 2), (3, 4), (4, 3), (4, 5), and (5, 4).
# - For k == 2, the pairs are (1, 3), (3, 1), (1, 4), (4, 1), (2, 5), (5,
# 2), (3, 5), and (5, 3).
# - For k == 3, the pairs are (1, 5), and (5, 1).
# - For k == 4 and k == 5, there are no pairs.
#
# Example 3:
#
# Input: n = 4, x = 1, y = 1
# Output: [6,4,2,0]
# Explanation: For each distance k the pairs are:
# - For k == 1, the pairs are (1, 2), (2, 1), (2, 3), (3, 2), (3, 4), and
# (4, 3).
# - For k == 2, the pairs are (1, 3), (3, 1), (2, 4), and (4, 2).
# - For k == 3, the pairs are (1, 4), and (4, 1).
# - For k == 4, there are no pairs.
#
# Constraints:
#
# 2 <= n <= 100
#
# 1 <= x, y <= n
#

# @lc code=start

from typing import List


class Solution:
    def countOfPairs(self, n: int, x: int, y: int) -> List[int]:
        """
        Interview explanation:
        Houses form a path 1..n plus optional chord (x,y). Count ordered pairs at
        each distance. n <= 100, so compute all-pairs distances directly.

        Algorithm:
        - For every ordered pair (i,j), i!=j, distance is
          min(|i-j|, |i-x|+1+|y-j|, |i-y|+1+|x-j|).
        - Increment result[dist-1].

        Complexity: O(n^2) time, O(n) space.
        """
        if x > y:
            x, y = y, x
        res = [0] * n
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i == j:
                    continue
                d = abs(i - j)
                d = min(d, abs(i - x) + 1 + abs(y - j))
                d = min(d, abs(i - y) + 1 + abs(x - j))
                res[d - 1] += 1
        return res

    def countOfPairs_bfs(self, n: int, x: int, y: int) -> List[int]:
        """
        Interview explanation:
        Build the graph explicitly and BFS from every house to accumulate
        distance histogram (ordered pairs via two directed counts).

        Algorithm:
        - Adjacency: path edges plus chord x-y.
        - From each source BFS; for each reached node at dist d>0, res[d-1]+=1.

        Complexity: O(n^2) time, O(n) space.
        """
        from collections import deque

        g: List[List[int]] = [[] for _ in range(n + 1)]
        for i in range(1, n):
            g[i].append(i + 1)
            g[i + 1].append(i)
        if x != y:
            g[x].append(y)
            g[y].append(x)

        res = [0] * n
        for src in range(1, n + 1):
            dist = [-1] * (n + 1)
            dist[src] = 0
            q = deque([src])
            while q:
                u = q.popleft()
                for v in g[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1
                        q.append(v)
            for d in dist[1:]:
                if d > 0:
                    res[d - 1] += 1
        return res
# @lc code=end
