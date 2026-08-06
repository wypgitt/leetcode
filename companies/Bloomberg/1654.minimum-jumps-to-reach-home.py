#
# @lc app=leetcode id=1654 lang=python3
#
# [1654] Minimum Jumps to Reach Home
#
# https://leetcode.com/problems/minimum-jumps-to-reach-home/description/
#
# algorithms
# Medium (30.98%)
# Likes:    1577
# Dislikes: 285
# Total Accepted:    54.3K
# Total Submissions: 175K
# Testcase Example:  "[14,4,18,1,15]"
#
# A certain bug's home is on the x-axis at position x. Help them get there from
# position 0.
#
# The bug jumps according to the following rules:
#
# It can jump exactly a positions forward (to the right).
#
# It can jump exactly b positions backward (to the left).
#
# It cannot jump backward twice in a row.
#
# It cannot jump to any forbidden positions.
#
# The bug may jump forward beyond its home, but it cannot jump to positions
# numbered with negative integers.
#
# Given an array of integers forbidden, where forbidden[i] means that the bug
# cannot jump to the position forbidden[i], and integers a, b, and x, return
# the minimum number of jumps needed for the bug to reach its home. If there is
# no possible sequence of jumps that lands the bug on position x, return -1.
#
# Example 1:
#
# Input: forbidden = [14,4,18,1,15], a = 3, b = 15, x = 9
# Output: 3
# Explanation: 3 jumps forward (0 -> 3 -> 6 -> 9) will get the bug home.
#
# Example 2:
#
# Input: forbidden = [8,3,16,6,12,20], a = 15, b = 13, x = 11
# Output: -1
#
# Example 3:
#
# Input: forbidden = [1,6,2,14,5,17,4], a = 16, b = 9, x = 7
# Output: 2
# Explanation: One jump forward (0 -> 16) then one jump backward (16 -> 7) will
# get the bug home.
#
# Constraints:
#
# 1 <= forbidden.length <= 1000
#
# 1 <= a, b, forbidden[i] <= 2000
#
# 0 <= x <= 2000
#
# All the elements in forbidden are distinct.
#
# Position x is not forbidden.
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def minimumJumps(self, forbidden: List[int], a: int, b: int, x: int) -> int:
        """
        Interview explanation:
        Jump +a forward or -b backward (cannot backward twice in a row). Forbidden
        positions blocked. BFS on (position, last_was_back) with bound beyond
        max(x, max_forbidden) + a + b.

        Algorithm (BFS):
        - Queue (pos, back_flag, steps); visit set (pos, back_flag).
        - Try forward always; try backward if not last_was_back.

        Complexity: O(bound) time/space.
        """
        forbid = set(forbidden)
        limit = max([x] + forbidden) + a + b
        q = deque([(0, False, 0)])  # pos, last_back, steps
        seen = {(0, False)}
        while q:
            pos, back, steps = q.popleft()
            if pos == x:
                return steps
            nxt = pos + a
            if nxt <= limit and nxt not in forbid and (nxt, False) not in seen:
                seen.add((nxt, False))
                q.append((nxt, False, steps + 1))
            if not back:
                nxt = pos - b
                if nxt >= 0 and nxt not in forbid and (nxt, True) not in seen:
                    seen.add((nxt, True))
                    q.append((nxt, True, steps + 1))
        return -1
# @lc code=end
