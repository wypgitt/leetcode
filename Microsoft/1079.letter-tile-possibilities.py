#
# @lc app=leetcode id=1079 lang=python3
#
# [1079] Letter Tile Possibilities
#
# https://leetcode.com/problems/letter-tile-possibilities/description/
#
# algorithms
# Medium (83.53%)
# Likes:    3161
# Dislikes: 92
# Total Accepted:    262K
# Total Submissions: 313K
# Testcase Example:  "\"AAB\""
#
# You have n tiles, where each tile has one letter tiles[i] printed on it.
#
# Return the number of possible non-empty sequences of letters you can make
# using the letters printed on those tiles.
#
# Example 1:
#
# Input: tiles = "AAB"
# Output: 8
# Explanation: The possible sequences are "A", "B", "AA", "AB", "BA", "AAB",
# "ABA", "BAA".
#
# Example 2:
#
# Input: tiles = "AAABBC"
# Output: 188
#
# Example 3:
#
# Input: tiles = "V"
# Output: 1
#
# Constraints:
#
# 1 <= tiles.length <= 7
#
# tiles consists of uppercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def numTilePossibilities(self, tiles: str) -> int:
        """
        Interview explanation:
        Count all non-empty sequences formable from the multiset of tiles.
        Backtrack over remaining letter counts: at each step pick any letter
        still available, decrement, recurse, restore. Each recursive call
        (except root) is one valid sequence.

        Algorithm (backtrack):
        - Counter of letters.
        - dfs(): for each letter with cnt>0: use it (ans++), dfs(), restore.

        Complexity: O(∑ k! / freqs) ≤ O(n·n!) time for n≤7, O(Σ) space.
        """
        cnt = Counter(tiles)

        def dfs() -> int:
            total = 0
            for ch in cnt:
                if cnt[ch] == 0:
                    continue
                cnt[ch] -= 1
                total += 1 + dfs()
                cnt[ch] += 1
            return total

        return dfs()
# @lc code=end
