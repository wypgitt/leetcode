#
# @lc app=leetcode id=2345 lang=python3
#
# [2345] Finding the Number of Visible Mountains
#
# https://leetcode.com/problems/finding-the-number-of-visible-mountains/description/
#
# algorithms
# Medium (37.45%)
# Likes:    186
# Dislikes: 80
# Total Accepted:    14.2K
# Total Submissions: 37.9K
# Testcase Example:  "[[2,2],[6,3],[5,4]]"
#
#
# You are given a 0-indexed 2D integer array peaks where peaks[i] = [x_i,
# y_i] states that mountain i has a peak at coordinates (x_i, y_i). A
# mountain can be described as a right-angled isosceles triangle, with its
# base along the x-axis and a right angle at its peak. More formally, the
# gradients of ascending and descending the mountain are 1 and -1
# respectively.
#
# A mountain is considered visible if its peak does not lie within another
# mountain (including the border of other mountains).
#
# Return the number of visible mountains.
#
# Example 1:
#
# Input: peaks = [[2,2],[6,3],[5,4]]
# Output: 2
# Explanation: The diagram above shows the mountains.
# - Mountain 0 is visible since its peak does not lie within another
# mountain or its sides.
# - Mountain 1 is not visible since its peak lies within the side of
# mountain 2.
# - Mountain 2 is visible since its peak does not lie within another
# mountain or its sides.
# There are 2 mountains that are visible.
#
# Example 2:
#
# Input: peaks = [[1,3],[1,3]]
# Output: 0
# Explanation: The diagram above shows the mountains (they completely
# overlap).
# Both mountains are not visible since their peaks lie within each other.
#
# Constraints:
#
# 1 <= peaks.length <= 10^5
#
# peaks[i].length == 2
#
# 1 <= x_i, y_i <= 10^5
#
# @lc code=start
from typing import List
from collections import Counter
from math import inf


class Solution:
    def visibleMountains(self, peaks: List[List[int]]) -> int:
        """
        Interview explanation:
        Mountains are isosceles right triangles with peak (x,y). Visible iff
        peak not inside/on border of another mountain. Count visible mountains.
        Identical overlapping mountains hide each other.

        Algorithm:
        - Map peak to interval [x-y, x+y]. Sort by left asc, right desc.
        - Sweep: keep max right; a mountain is visible if it extends past cur
          right and its interval is unique.

        Complexity: O(n log n) time, O(n) space.
        """
        arr = [(x - y, x + y) for x, y in peaks]
        cnt = Counter(arr)
        arr.sort(key=lambda t: (t[0], -t[1]))
        ans = 0
        cur = -inf
        for l, r in arr:
            if r <= cur:
                continue
            cur = r
            if cnt[(l, r)] == 1:
                ans += 1
        return ans
# @lc code=end
