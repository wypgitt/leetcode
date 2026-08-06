#
# @lc app=leetcode id=2271 lang=python3
#
# [2271] Maximum White Tiles Covered by a Carpet
#
# https://leetcode.com/problems/maximum-white-tiles-covered-by-a-carpet/description/
#
# algorithms
# Medium (36.26%)
# Likes:    849
# Dislikes: 59
# Total Accepted:    23K
# Total Submissions: 63.3K
# Testcase Example:  "[[1,5],[10,11],[12,18],[20,25],[30,32]]\n10"
#
# You are given a 2D integer array tiles where tiles[i] = [l_i, r_i] represents
# that every tile j in the range l_i <= j <= r_i is colored white.
#
# You are also given an integer carpetLen, the length of a single carpet that
# can be placed anywhere.
#
# Return the maximum number of white tiles that can be covered by the carpet.
#
#
#
# Example 1:
#
# Input: tiles = [[1,5],[10,11],[12,18],[20,25],[30,32]], carpetLen = 10
# Output: 9
# Explanation: Place the carpet starting on tile 10.
# It covers 9 white tiles, so we return 9.
# Note that there may be other places where the carpet covers 9 white tiles.
# It can be shown that the carpet cannot cover more than 9 white tiles.
#
# Example 2:
#
# Input: tiles = [[10,11],[1,1]], carpetLen = 2
# Output: 2
# Explanation: Place the carpet starting on tile 10.
# It covers 2 white tiles, so we return 2.
#
#
#
# Constraints:
#
#
# 1 <= tiles.length <= 5 * 10^4
#
#
# tiles[i].length == 2
#
#
# 1 <= l_i <= r_i <= 10^9
#
#
# 1 <= carpetLen <= 10^9
#
#
# The tiles are non-overlapping.
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def maximumWhiteTiles(self, tiles: List[List[int]], carpetLen: int) -> int:
        """
        Interview explanation:
        Place a carpet of length carpetLen to cover max white tiles (given intervals).

        Algorithm:
        - Sort tiles; prefix sums of lengths; for each left start, binary search
          rightmost tile reachable; add partial cover on last tile.

        Complexity: O(n log n) time, O(n) space.
        """
        tiles.sort()
        n = len(tiles)
        pref = [0] * (n + 1)
        for i, (s, e) in enumerate(tiles):
            pref[i + 1] = pref[i] + (e - s + 1)
        starts = [t[0] for t in tiles]
        ans = 0
        for i, (s, e) in enumerate(tiles):
            cover_to = s + carpetLen - 1
            j = bisect.bisect_right(starts, cover_to) - 1
            if j < i:
                continue
            total = pref[j] - pref[i]
            # full tiles i..j-1 already in total relative? wait pref[j]-pref[i] is tiles i..j-1
            # include partial of tile j
            if cover_to >= tiles[j][1]:
                total = pref[j + 1] - pref[i]
            else:
                total = pref[j] - pref[i] + (cover_to - tiles[j][0] + 1)
            ans = max(ans, total)
        return ans

    def maximumWhiteTiles_two_pointers(self, tiles: List[List[int]], carpetLen: int) -> int:
        """
        Interview explanation:
        Two-pointers alternate: carpet starts at tile left endpoints; expand j.

        Algorithm:
        - Sort; maintain window of tiles under carpet starting at tiles[i][0].

        Complexity: O(n log n) time, O(n) space.
        """
        tiles.sort()
        n = len(tiles)
        pref = [0] * (n + 1)
        for i, (s, e) in enumerate(tiles):
            pref[i + 1] = pref[i] + e - s + 1
        ans = j = 0
        for i in range(n):
            end = tiles[i][0] + carpetLen - 1
            while j < n and tiles[j][1] <= end:
                j += 1
            if j == n:
                ans = max(ans, pref[n] - pref[i])
            else:
                partial = max(0, end - tiles[j][0] + 1)
                ans = max(ans, pref[j] - pref[i] + partial)
        return ans
# @lc code=end
