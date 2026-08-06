#
# @lc app=leetcode id=765 lang=python3
#
# [765] Couples Holding Hands
#
# https://leetcode.com/problems/couples-holding-hands/description/
#
# algorithms
# Hard (59.6%)
# Likes:    2504
# Dislikes: 132
# Total Accepted:    86.5K
# Total Submissions: 145K
# Testcase Example:  "[0,2,1,3]"
#
# There are n couples sitting in 2n seats arranged in a row and want to hold
# hands.
#
# The people and seats are represented by an integer array row where row[i] is
# the ID of the person sitting in the i^th seat. The couples are numbered in
# order, the first couple being (0, 1), the second couple being (2, 3), and so
# on with the last couple being (2n - 2, 2n - 1).
#
# Return the minimum number of swaps so that every couple is sitting side by
# side. A swap consists of choosing any two people, then they stand up and
# switch seats.
#
# Example 1:
#
# Input: row = [0,2,1,3]
# Output: 1
# Explanation: We only need to swap the second (row[1]) and third (row[2])
# person.
#
# Example 2:
#
# Input: row = [3,2,0,1]
# Output: 0
# Explanation: All couples are already seated side by side.
#
# Constraints:
#
# 2n == row.length
#
# 2 <= n <= 30
#
# 0 <= row[i] < 2n
#
# All the elements of row are unique.
#


# @lc code=start
from typing import List


class Solution:
    def minSwapsCouples(self, row: List[int]) -> int:
        """
        Interview explanation:
        Couples are (0,1), (2,3), ... Treat each couple as a node. Each sofa
        pair of seats that currently holds people from couples A and B is an
        edge A—B. Number of swaps = N_couples - number of cycles in this graph
        (Union-Find / cycle count). Equivalently greedy: fix each seat pair.

        Algorithm (Union-Find):
        - For i in 0,2,4,...: union couple(row[i]) with couple(row[i+1])
        - swaps = n/2 - number of UF components

        Complexity: O(n α(n)) time, O(n) space.
        """
        n = len(row) // 2
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for i in range(0, len(row), 2):
            union(row[i] // 2, row[i + 1] // 2)
        components = len({find(i) for i in range(n)})
        return n - components

    def minSwapsCouples_greedy(self, row: List[int]) -> int:
        """
        Interview explanation:
        Alternate classic greedy: for each even seat i, if row[i+1] is not the
        partner of row[i], swap the partner into i+1 from wherever they sit.

        Algorithm:
        - pos[person] = index; for i in 0,2,...: partner = row[i]^1
          if row[i+1] != partner: swap with pos[partner]; count++

        Complexity: O(n) time, O(n) space.
        """
        pos = {p: i for i, p in enumerate(row)}
        swaps = 0
        for i in range(0, len(row), 2):
            partner = row[i] ^ 1
            if row[i + 1] != partner:
                j = pos[partner]
                pos[row[i + 1]] = j
                row[j] = row[i + 1]
                row[i + 1] = partner
                pos[partner] = i + 1
                swaps += 1
        return swaps
# @lc code=end

