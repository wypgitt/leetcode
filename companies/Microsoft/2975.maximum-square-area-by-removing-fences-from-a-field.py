#
# @lc app=leetcode id=2975 lang=python3
#
# [2975] Maximum Square Area by Removing Fences From a Field
#
# https://leetcode.com/problems/maximum-square-area-by-removing-fences-from-a-field/description/
#
# algorithms
# Medium (49.55%)
# Likes:    460
# Dislikes: 162
# Total Accepted:    99.3K
# Total Submissions: 200.3K
# Testcase Example:  "4\n3\n[2,3]\n[2]"
#
#
# There is a large (m - 1) x (n - 1) rectangular field with corners at (1,
# 1) and (m, n) containing some horizontal and vertical fences given in
# arrays hFences and vFences respectively.
#
# Horizontal fences are from the coordinates (hFences[i], 1) to
# (hFences[i], n) and vertical fences are from the coordinates (1,
# vFences[i]) to (m, vFences[i]).
#
# Return the maximum area of a square field that can be formed by removing
# some fences (possibly none) or -1 if it is impossible to make a square
# field.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# Note: The field is surrounded by two horizontal fences from the
# coordinates (1, 1) to (1, n) and (m, 1) to (m, n) and two vertical
# fences from the coordinates (1, 1) to (m, 1) and (1, n) to (m, n). These
# fences cannot be removed.
#
# Example 1:
#
# Input: m = 4, n = 3, hFences = [2,3], vFences = [2]
# Output: 4
# Explanation: Removing the horizontal fence at 2 and the vertical fence
# at 2 will give a square field of area 4.
#
# Example 2:
#
# Input: m = 6, n = 7, hFences = [2], vFences = [4]
# Output: -1
# Explanation: It can be proved that there is no way to create a square
# field by removing fences.
#
# Constraints:
#
# 3 <= m, n <= 10^9
#
# 1 <= hFences.length, vFences.length <= 600
#
# 1 < hFences[i] < m
#
# 1 < vFences[i] < n
#
# hFences and vFences are unique.
#

# @lc code=start
from typing import List


class Solution:
    def maximizeSquareArea(self, m: int, n: int, hFences: List[int], vFences: List[int]) -> int:
        """
        Interview explanation:
        Borders at 1 and m (horizontal) / 1 and n (vertical) are fixed. A square needs
        equal spacing between two kept horizontal fences and two kept vertical fences;
        that spacing is the side length.

        Algorithm:
        - Gather all h positions {1}+hFences+{m}, all pairwise gaps; same for v.
          Max common gap g gives area g^2 mod 1e9+7, or -1 if none.

        Complexity: O(h^2 + v^2) time, O(h^2 + v^2) space (h,v <= 600).
        """
        MOD = 10**9 + 7

        def gaps(fences: List[int], end: int) -> set:
            arr = sorted([1] + fences + [end])
            s = set()
            for i in range(len(arr)):
                for j in range(i + 1, len(arr)):
                    s.add(arr[j] - arr[i])
            return s

        common = gaps(hFences, m) & gaps(vFences, n)
        if not common:
            return -1
        side = max(common)
        return side * side % MOD
# @lc code=end
