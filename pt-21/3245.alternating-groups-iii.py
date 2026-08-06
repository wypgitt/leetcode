#
# @lc app=leetcode id=3245 lang=python3
#
# [3245] Alternating Groups III
#
# https://leetcode.com/problems/alternating-groups-iii/description/
#
# algorithms
# Hard (19.69%)
# Likes:    65
# Dislikes: 10
# Total Accepted:    3.1K
# Total Submissions: 15.6K
# Testcase Example:  "[0,1,1,0,1]\n[[2,1,0],[1,4]]"
#
#
# There are some red and blue tiles arranged circularly. You are given an
# array of integers colors and a 2D integers array queries.
#
# The color of tile i is represented by colors[i]:
#
# colors[i] == 0 means that tile i is red.
#
# colors[i] == 1 means that tile i is blue.
#
# An alternating group is a contiguous subset of tiles in the circle with
# alternating colors (each tile in the group except the first and last one
# has a different color from its adjacent tiles in the group).
#
# You have to process queries of two types:
#
# queries[i] = [1, size_i], determine the count of alternating groups with
# size size_i.
#
# queries[i] = [2, index_i, color_i], change colors[index_i] to color_i.
#
# Return an array answer containing the results of the queries of the
# first type in order.
#
# Note that since colors represents a circle, the first and the last tiles
# are considered to be next to each other.
#
# Example 1:
#
# Input: colors = [0,1,1,0,1], queries = [[2,1,0],[1,4]]
#
# Output: [2]
#
# Explanation:
#
# First query:
#
# Change colors[1] to 0.
#
# Second query:
#
# Count of the alternating groups with size 4:
#
# Example 2:
#
# Input: colors = [0,0,1,0,1,1], queries = [[1,3],[2,3,0],[1,5]]
#
# Output: [2,0]
#
# Explanation:
#
# First query:
#
# Count of the alternating groups with size 3:
#
# Second query: colors will not change.
#
# Third query: There is no alternating group with size 5.
#
# Constraints:
#
# 4 <= colors.length <= 5 * 10^4
#
# 0 <= colors[i] <= 1
#
# 1 <= queries.length <= 5 * 10^4
#
# queries[i][0] == 1 or queries[i][0] == 2
#
# For all i that:
#
# queries[i][0] == 1: queries[i].length == 2, 3 <= queries[i][1] <=
# colors.length - 1
#
# queries[i][0] == 2: queries[i].length == 3, 0 <= queries[i][1] <=
# colors.length - 1, 0 <= queries[i][2] <= 1
#

# @lc code=start
import bisect
from typing import List


class Solution:
    def numberOfAlternatingGroups(self, colors: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Circular tiles; alternating groups are runs without equal adjacent pairs.
        Maintain break indices (equal adjacent) in a sorted list; Fenwick trees
        store segment-length frequencies/sums so size queries are O(log n).

        Algorithm:
        - Breaks: i where colors[i] == colors[(i+1)%n]. Segments between breaks.
        - Groups of size L in a segment of length S: max(0, S-L+1).
        - On color flip, equalities at i-1 and i always toggle; update BITs.
        - Query: sum(S)-(L-1)*cnt over segments with S >= L (or n if no breaks).

        Complexity: O((n+q) log n) time, O(n) space.
        """

        class BIT:
            def __init__(self, n: int):
                self.bit = [0] * (n + 1)

            def add(self, i: int, val: int) -> None:
                i += 1
                while i < len(self.bit):
                    self.bit[i] += val
                    i += i & -i

            def query(self, i: int) -> int:
                i += 1
                res = 0
                while i > 0:
                    res += self.bit[i]
                    i -= i & -i
                return res

        n = len(colors)
        sl: List[int] = []
        bit1, bit2 = BIT(n + 1), BIT(n + 1)

        def update(i: int, d: int) -> None:
            if d == 1:
                bisect.insort(sl, i)
                if len(sl) == 1:
                    bit1.add(n, 1)
                    bit2.add(n, n)
            curr = bisect.bisect_left(sl, i)
            m = len(sl)
            prv, nxt = (curr - 1) % m, (curr + 1) % m
            if m != 1:
                L = (sl[nxt] - sl[prv] - 1) % n + 1
                bit1.add(L, d * -1)
                bit2.add(L, d * -L)
                L = (sl[curr] - sl[prv]) % n
                bit1.add(L, d)
                bit2.add(L, d * L)
                L = (sl[nxt] - sl[curr]) % n
                bit1.add(L, d)
                bit2.add(L, d * L)
            if d == -1:
                if len(sl) == 1:
                    bit1.add(n, -1)
                    bit2.add(n, -n)
                sl.pop(curr)

        for i in range(n):
            if colors[i] == colors[(i + 1) % n]:
                update(i, 1)

        ans = []
        for q in queries:
            if q[0] == 1:
                L = q[1]
                if not sl:
                    ans.append(n)
                else:
                    ans.append(
                        (bit2.query(n) - bit2.query(L - 1))
                        - (L - 1) * (bit1.query(n) - bit1.query(L - 1))
                    )
            else:
                _, i, c = q
                if colors[i] == c:
                    continue
                colors[i] = c
                update((i - 1) % n, 1 if colors[i] == colors[(i - 1) % n] else -1)
                update(i, 1 if colors[i] == colors[(i + 1) % n] else -1)
        return ans
# @lc code=end
