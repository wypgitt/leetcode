#
# @lc app=leetcode id=1320 lang=python3
#
# [1320] Minimum Distance to Type a Word Using Two Fingers
#
# https://leetcode.com/problems/minimum-distance-to-type-a-word-using-two-fingers/description/
#
# algorithms
# Hard (72.32%)
# Likes:    1376
# Dislikes: 54
# Total Accepted:    103K
# Total Submissions: 142K
# Testcase Example:  "\"CAKE\""
#
# You have a keyboard layout as shown above in the X-Y plane, where each
# English uppercase letter is located at some coordinate.
#
# For example, the letter 'A' is located at coordinate (0, 0), the letter 'B'
# is located at coordinate (0, 1), the letter 'P' is located at coordinate (2,
# 3) and the letter 'Z' is located at coordinate (4, 1).
#
# Given the string word, return the minimum total distance to type such string
# using only two fingers.
#
# The distance between coordinates (x_1, y_1) and (x_2, y_2) is |x_1 - x_2| +
# |y_1 - y_2|.
#
# Note that the initial positions of your two fingers are considered free so do
# not count towards your total distance, also your two fingers do not have to
# start at the first letter or the first two letters.
#
# Example 1:
#
# Input: word = "CAKE"
# Output: 3
# Explanation: Using two fingers, one optimal way to type "CAKE" is:
# Finger 1 on letter 'C' -> cost = 0
# Finger 1 on letter 'A' -> cost = Distance from letter 'C' to letter 'A' = 2
# Finger 2 on letter 'K' -> cost = 0
# Finger 2 on letter 'E' -> cost = Distance from letter 'K' to letter 'E' = 1
# Total distance = 3
#
# Example 2:
#
# Input: word = "HAPPY"
# Output: 6
# Explanation: Using two fingers, one optimal way to type "HAPPY" is:
# Finger 1 on letter 'H' -> cost = 0
# Finger 1 on letter 'A' -> cost = Distance from letter 'H' to letter 'A' = 2
# Finger 2 on letter 'P' -> cost = 0
# Finger 2 on letter 'P' -> cost = Distance from letter 'P' to letter 'P' = 0
# Finger 1 on letter 'Y' -> cost = Distance from letter 'A' to letter 'Y' = 4
# Total distance = 6
#
# Constraints:
#
# 2 <= word.length <= 300
#
# word consists of uppercase English letters.
#

# @lc code=start
from functools import lru_cache


class Solution:
    def minimumDistance(self, word: str) -> int:
        """
        Interview explanation:
        Type word on 6x6 keyboard A-Z with two fingers. Cost is Manhattan
        distance between keys; first touch of a finger is free. DP over index
        and both finger positions (26 = not yet placed).

        Algorithm (DP / memo DFS):
        - pos(ch)=(r,c); dist(a,b)=0 if either free else Manhattan.
        - dfs(i, f1, f2): min of moving f1 or f2 to word[i], recurse.

        Complexity: O(n * 27^2) time/space.
        """
        codes = [ord(c) - 65 for c in word]

        def dist(a: int, b: int) -> int:
            if a == 26:
                return 0
            return abs(a // 6 - b // 6) + abs(a % 6 - b % 6)

        @lru_cache(None)
        def dfs(i: int, f1: int, f2: int) -> int:
            if i == len(codes):
                return 0
            c = codes[i]
            return min(
                dist(f1, c) + dfs(i + 1, c, f2),
                dist(f2, c) + dfs(i + 1, f1, c),
            )

        return dfs(0, 26, 26)
# @lc code=end

