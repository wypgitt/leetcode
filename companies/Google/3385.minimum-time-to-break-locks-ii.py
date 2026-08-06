#
# @lc app=leetcode id=3385 lang=python3
#
# [3385] Minimum Time to Break Locks II
#
# https://leetcode.com/problems/minimum-time-to-break-locks-ii/description/
#
# algorithms
# Hard (45.93%)
# Likes:    5
# Dislikes: 1
# Total Accepted:    378
# Total Submissions: 823
# Testcase Example:  "[3,4,1]"
#
#
# Bob is stuck in a dungeon and must break n locks, each requiring some
# amount of energy to break. The required energy for each lock is stored
# in an array called strength where strength[i] indicates the energy
# needed to break the i^th lock.
#
# To break a lock, Bob uses a sword with the following characteristics:
#
# The initial energy of the sword is 0.
#
# The initial factor X by which the energy of the sword increases is 1.
#
# Every minute, the energy of the sword increases by the current factor X.
#
# To break the i^th lock, the energy of the sword must reach at least
# strength[i].
#
# After breaking a lock, the energy of the sword resets to 0, and the
# factor X increases by 1.
#
# Your task is to determine the minimum time in minutes required for Bob
# to break all n locks and escape the dungeon.
#
# Return the minimum time required for Bob to break all n locks.
#
# Example 1:
#
# Input: strength = [3,4,1]
#
# Output: 4
#
# Explanation:
#
#                         Time
#                         Energy
#                         X
#                         Action
#                         Updated X
#
#                         0
#                         0
#                         1
#                         Nothing
#                         1
#
#                         1
#                         1
#                         1
#                         Break 3^rd Lock
#                         2
#
#                         2
#                         2
#                         2
#                         Nothing
#                         2
#
#                         3
#                         4
#                         2
#                         Break 2^nd Lock
#                         3
#
#                         4
#                         3
#                         3
#                         Break 1^st Lock
#                         3
#
# The locks cannot be broken in less than 4 minutes; thus, the answer is
# 4.
#
# Example 2:
#
# Input: strength = [2,5,4]
#
# Output: 6
#
# Explanation:
#
#                         Time
#                         Energy
#                         X
#                         Action
#                         Updated X
#
#                         0
#                         0
#                         1
#                         Nothing
#                         1
#
#                         1
#                         1
#                         1
#                         Nothing
#                         1
#
#                         2
#                         2
#                         1
#                         Break 1^st Lock
#                         2
#
#                         3
#                         2
#                         2
#                         Nothing
#                         2
#
#                         4
#                         4
#                         2
#                         Break 3^rd Lock
#                         3
#
#                         5
#                         3
#                         3
#                         Nothing
#                         3
#
#                         6
#                         6
#                         3
#                         Break 2^nd Lock
#                         4
#
# The locks cannot be broken in less than 6 minutes; thus, the answer is
# 6.
#
# Constraints:
#
# n == strength.length
#
# 1 <= n <= 80
#
# 1 <= strength[i] <= 10^6
#

# @lc code=start

from typing import List


class Solution:
    def findMinimumTime(self, strength: List[int]) -> int:
        """
        Interview explanation:
        Breaking order assigns each lock to a unique factor X = 1..n. Time for
        lock s at factor x is ceil(s/x). Minimize sum over a bijection — classic
        min-cost bipartite matching (Hungarian), since n <= 80.

        Algorithm:
        - cost[i][j] = ceil(strength[i] / (j+1)).
        - Run Hungarian / Kuhn-Munkres for minimum assignment cost.

        Complexity: O(n^3) time, O(n^2) space.
        """
        n = len(strength)
        cost = [[(strength[i] + j) // (j + 1) for j in range(n)] for i in range(n)]
        return self._hungarian(cost)

    def _hungarian(self, a: List[List[int]]) -> int:
        """Min-cost assignment; KACTL-style O(n^2 m) implementation."""
        if not a:
            return 0
        n, m = len(a) + 1, len(a[0]) + 1
        u = [0] * n
        v = [0] * m
        p = [0] * m
        for i in range(1, n):
            p[0] = i
            j0 = 0
            dist = [float('inf')] * m
            pre = [-1] * m
            done = [False] * (m + 1)
            while True:
                done[j0] = True
                i0 = p[j0]
                j1 = 0
                delta = float('inf')
                for j in range(1, m):
                    if done[j]:
                        continue
                    cur = a[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < dist[j]:
                        dist[j] = cur
                        pre[j] = j0
                    if dist[j] < delta:
                        delta = dist[j]
                        j1 = j
                for j in range(m):
                    if done[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        dist[j] -= delta
                j0 = j1
                if p[j0] == 0:
                    break
            while j0:
                j1 = pre[j0]
                p[j0] = p[j1]
                j0 = j1
        return -v[0]
# @lc code=end
