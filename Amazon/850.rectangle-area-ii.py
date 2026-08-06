#
# @lc app=leetcode id=850 lang=python3
#
# [850] Rectangle Area II
#
# https://leetcode.com/problems/rectangle-area-ii/description/
#
# algorithms
# Hard (56.5%)
# Likes:    1056
# Dislikes: 66
# Total Accepted:    45.6K
# Total Submissions: 80.7K
# Testcase Example:  "[[0,0,2,2],[1,0,2,3],[1,0,3,1]]"
#
# You are given a 2D array of axis-aligned rectangles. Each rectangle[i] =
# [x_i1, y_i1, x_i2, y_i2] denotes the i^th rectangle where (x_i1, y_i1) are
# the coordinates of the bottom-left corner, and (x_i2, y_i2) are the
# coordinates of the top-right corner.
#
# Calculate the total area covered by all rectangles in the plane. Any area
# covered by two or more rectangles should only be counted once.
#
# Return the total area. Since the answer may be too large, return it modulo
# 10^9 + 7.
#
# Example 1:
#
# Input: rectangles = [[0,0,2,2],[1,0,2,3],[1,0,3,1]]
# Output: 6
# Explanation: A total area of 6 is covered by all three rectangles, as
# illustrated in the picture.
# From (1,1) to (2,2), the green and red rectangles overlap.
# From (1,0) to (2,3), all three rectangles overlap.
#
# Example 2:
#
# Input: rectangles = [[0,0,1000000000,1000000000]]
# Output: 49
# Explanation: The answer is 10^18 modulo (10^9 + 7), which is 49.
#
# Constraints:
#
# 1 <= rectangles.length <= 200
#
# rectanges[i].length == 4
#
# 0 <= x_i1, y_i1, x_i2, y_i2 <= 10^9
#
# x_i1 <= x_i2
#
# y_i1 <= y_i2
#
# All rectangles have non zero area.
#

# @lc code=start

from typing import List


class Solution:
    def rectangleArea(self, rectangles: List[List[int]]) -> int:
        """
        Interview explanation:
        Soft line sweep on x: collect vertical edges (open/close), sort by x;
        between consecutive x, active y-intervals' covered length * dx. Merge
        y-intervals with sweep/sorted list.

        Algorithm:
        - Events (x, typ, y1, y2); sort; active list of [y1,y2]; measure union
          length of y; add length * Δx. Mod 10^9+7.

        Complexity: O(R^2 log R) typical with simple active merge, O(R) space.
        """
        MOD = 10**9 + 7
        events = []
        for x1, y1, x2, y2 in rectangles:
            events.append((x1, 1, y1, y2))
            events.append((x2, -1, y1, y2))
        events.sort()
        active: List[List[int]] = []

        def measure() -> int:
            if not active:
                return 0
            segs = sorted(active)
            total = 0
            cur_l, cur_r = segs[0]
            for l, r in segs[1:]:
                if l > cur_r:
                    total += cur_r - cur_l
                    cur_l, cur_r = l, r
                else:
                    cur_r = max(cur_r, r)
            total += cur_r - cur_l
            return total

        ans = 0
        prev_x = events[0][0]
        i = 0
        while i < len(events):
            x = events[i][0]
            ans += measure() * (x - prev_x)
            while i < len(events) and events[i][0] == x:
                _, typ, y1, y2 = events[i]
                if typ == 1:
                    active.append([y1, y2])
                else:
                    active.remove([y1, y2])
                i += 1
            prev_x = x
        return ans % MOD
# @lc code=end
