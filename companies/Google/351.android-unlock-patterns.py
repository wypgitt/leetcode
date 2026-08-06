#
# @lc app=leetcode id=351 lang=python3
#
# [351] Android Unlock Patterns
#
# https://leetcode.com/problems/android-unlock-patterns/description/
#
# algorithms
# Medium (53.90%)
# Likes:    214
# Dislikes: 240
# Total Accepted:    84.8K
# Total Submissions: 157.4K
# Testcase Example:  "1\n1"
#
#
# Android devices have a special lock screen with a 3 x 3 grid of dots.
# Users can set an "unlock pattern" by connecting the dots in a specific
# sequence, forming a series of joined line segments where each segment's
# endpoints are two consecutive dots in the sequence. A sequence of k dots
# is a valid unlock pattern if both of the following are true:
#
# All the dots in the sequence are distinct.
#
# If the line segment connecting two consecutive dots in the sequence
# passes through the center of any other dot, the other dot must have
# previously appeared in the sequence. No jumps through the center
# non-selected dots are allowed.
#
# For example, connecting dots 2 and 9 without dots 5 or 6 appearing
# beforehand is valid because the line from dot 2 to dot 9 does not pass
# through the center of either dot 5 or 6.
#
# However, connecting dots 1 and 3 without dot 2 appearing beforehand is
# invalid because the line from dot 1 to dot 3 passes through the center
# of dot 2.
#
# Here are some example valid and invalid unlock patterns:
#
# The 1st pattern [4,1,3,6] is invalid because the line connecting dots 1
# and 3 pass through dot 2, but dot 2 did not previously appear in the
# sequence.
#
# The 2nd pattern [4,1,9,2] is invalid because the line connecting dots 1
# and 9 pass through dot 5, but dot 5 did not previously appear in the
# sequence.
#
# The 3rd pattern [2,4,1,3,6] is valid because it follows the conditions.
# The line connecting dots 1 and 3 meets the condition because dot 2
# previously appeared in the sequence.
#
# The 4th pattern [6,5,4,1,9,2] is valid because it follows the
# conditions. The line connecting dots 1 and 9 meets the condition because
# dot 5 previously appeared in the sequence.
#
# Given two integers m and n, return the number of unique and valid unlock
# patterns of the Android grid lock screen that consist of at least m keys
# and at most n keys.
#
# Two unlock patterns are considered unique if there is a dot in one
# sequence that is not in the other, or the order of the dots is
# different.
#
# Example 1:
#
# Input: m = 1, n = 1
# Output: 9
#
# Example 2:
#
# Input: m = 1, n = 2
# Output: 65
#
# Constraints:
#
# 1 <= m, n <= 9
#
# @lc code=start
class Solution:
    def numberOfPatterns(self, m: int, n: int) -> int:
        """
        Interview explanation:
        DFS backtracking over the 3x3 pad (keys 1..9). Skip through a knight/
        mid-line jump unless the midpoint was already used. Count paths with
        length in [m, n]. Use 4-fold corner/edge symmetry.

        Algorithm:
        - skip[a][b] = midpoint that must be visited to go a->b (0 if free).
        - DFS(curr, length): if length in [m,n] count; extend to unused keys.
        - Answer = 4*dfs(1)+4*dfs(2)+dfs(5).

        Complexity: O(9!) worst but tiny constant; O(1) extra space.
        """
        skip = [[0] * 10 for _ in range(10)]
        skip[1][3] = skip[3][1] = 2
        skip[1][7] = skip[7][1] = 4
        skip[3][9] = skip[9][3] = 6
        skip[7][9] = skip[9][7] = 8
        skip[1][9] = skip[9][1] = skip[3][7] = skip[7][3] = 5
        skip[2][8] = skip[8][2] = skip[4][6] = skip[6][4] = 5
        visited = [False] * 10

        def dfs(curr: int, length: int) -> int:
            if length > n:
                return 0
            total = 1 if length >= m else 0
            if length == n:
                return total
            visited[curr] = True
            for nxt in range(1, 10):
                mid = skip[curr][nxt]
                if not visited[nxt] and (mid == 0 or visited[mid]):
                    total += dfs(nxt, length + 1)
            visited[curr] = False
            return total

        return 4 * dfs(1, 1) + 4 * dfs(2, 1) + dfs(5, 1)
# @lc code=end
