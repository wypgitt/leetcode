#
# @lc app=leetcode id=3443 lang=python3
#
# [3443] Maximum Manhattan Distance After K Changes
#
# https://leetcode.com/problems/maximum-manhattan-distance-after-k-changes/description/
#
# algorithms
# Medium (54.18%)
# Likes:    610
# Dislikes: 69
# Total Accepted:    102K
# Total Submissions: 188.2K
# Testcase Example:  "\"NWSE\"\n1"
#
#
# You are given a string s consisting of the characters 'N', 'S', 'E', and
# 'W', where s[i] indicates movements in an infinite grid:
#
# 'N' : Move north by 1 unit.
#
# 'S' : Move south by 1 unit.
#
# 'E' : Move east by 1 unit.
#
# 'W' : Move west by 1 unit.
#
# Initially, you are at the origin (0, 0). You can change at most k
# characters to any of the four directions.
#
# Find the maximum Manhattan distance from the origin that can be achieved
# at any time while performing the movements in order.
#
# The Manhattan Distance between two cells (x_i, y_i) and (x_j, y_j) is
# |x_i - x_j| + |y_i - y_j|.
#
# Example 1:
#
# Input: s = "NWSE", k = 1
#
# Output: 3
#
# Explanation:
#
# Change s[2] from 'S' to 'N'. The string s becomes "NWNE".
#
#                         Movement
#                         Position (x, y)
#                         Manhattan Distance
#                         Maximum
#
#                         s[0] == 'N'
#                         (0, 1)
#                         0 + 1 = 1
#                         1
#
#                         s[1] == 'W'
#                         (-1, 1)
#                         1 + 1 = 2
#                         2
#
#                         s[2] == 'N'
#                         (-1, 2)
#                         1 + 2 = 3
#                         3
#
#                         s[3] == 'E'
#                         (0, 2)
#                         0 + 2 = 2
#                         3
#
# The maximum Manhattan distance from the origin that can be achieved is
# 3. Hence, 3 is the output.
#
# Example 2:
#
# Input: s = "NSWWEW", k = 3
#
# Output: 6
#
# Explanation:
#
# Change s[1] from 'S' to 'N', and s[4] from 'E' to 'W'. The string s
# becomes "NNWWWW".
#
# The maximum Manhattan distance from the origin that can be achieved is
# 6. Hence, 6 is the output.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# 0 <= k <= s.length
#
# s consists of only 'N', 'S', 'E', and 'W'.
#

# @lc code=start

class Solution:
    def maxDistance(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Along the path, Manhattan distance is |N-S|+|E-W|. Each change can flip a
        canceling move into a reinforcing one, adding at most 2 to distance, but
        never exceeding the number of steps taken.

        Algorithm:
        - Walk the path tracking (x,y). At step i (1-indexed length),
          ans = max(ans, min(i, |x|+|y| + 2*k)).

        Complexity: O(n) time, O(1) space.
        """
        x = y = 0
        ans = 0
        for i, ch in enumerate(s, 1):
            if ch == "N":
                y += 1
            elif ch == "S":
                y -= 1
            elif ch == "E":
                x += 1
            else:
                x -= 1
            ans = max(ans, min(i, abs(x) + abs(y) + 2 * k))
        return ans
# @lc code=end
