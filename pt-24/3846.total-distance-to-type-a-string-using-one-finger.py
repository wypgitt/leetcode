#
# @lc app=leetcode id=3846 lang=python3
#
# [3846] Total Distance to Type a String Using One Finger
#
# https://leetcode.com/problems/total-distance-to-type-a-string-using-one-finger/description/
#
# algorithms
# Medium (89.44%)
# Likes:    4
# Dislikes: 2
# Total Accepted:    898
# Total Submissions: 1K
# Testcase Example:  "\"hello\""
#
#
# There is a special keyboard where keys are arranged in a rectangular
# grid as follows.
#
#                         q
#                         w
#                         e
#                         r
#                         t
#                         y
#                         u
#                         i
#                         o
#                         p
#
#                         a
#                         s
#                         d
#                         f
#                         g
#                         h
#                         j
#                         k
#                         l
#
#                         z
#                         x
#                         c
#                         v
#                         b
#                         n
#                         m
#
# You are given a string s that consists of lowercase English letters
# only. Return an integer denoting the total distance to type s using only
# one finger. Your finger starts on the key 'a'.
#
# The distance between two keys at (r1, c1) and (r2, c2) is |r1 - r2| +
# |c1 - c2|.
#
# Example 1:
#
# Input: s = "hello"
#
# Output: 17
#
# Explanation:
#
# Your finger starts at 'a', which is at (1, 0).
#
# Move to 'h', which is at (1, 5). The distance is |1 - 1| + |0 - 5| = 5.
#
# Move to 'e', which is at (0, 2). The distance is |1 - 0| + |5 - 2| = 4.
#
# Move to 'l', which is at (1, 8). The distance is |0 - 1| + |2 - 8| = 7.
#
# Move to 'l', which is at (1, 8). The distance is |1 - 1| + |8 - 8| = 0.
#
# Move to 'o', which is at (0, 8). The distance is |1 - 0| + |8 - 8| = 1.
#
# Total distance is 5 + 4 + 7 + 0 + 1 = 17.
#
# Example 2:
#
# Input: s = "a"
#
# Output: 0
#
# Explanation:
#
# Your finger starts at 'a', which is at (1, 0).
#
# Move to 'a', which is at (1, 0). The distance is |1 - 1| + |0 - 0| = 0.
#
# Total distance is 0.
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of lowercase English letters only.
#

# @lc code=start
class Solution:
    def totalDistance(self, s: str) -> int:
        """
        Interview explanation:
        Type s on a 3-row keyboard starting at 'a'. Distance is Manhattan
        between successive key positions.

        Algorithm:
        - Build char -> (row, col) for qwerty rows.
        - Accumulate |dr| + |dc| from previous key (start at 'a').

        Complexity: O(|s|) time, O(1) space.
        """
        rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
        pos = {}
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                pos[ch] = (r, c)
        pr, pc = pos["a"]
        total = 0
        for ch in s:
            r, c = pos[ch]
            total += abs(r - pr) + abs(c - pc)
            pr, pc = r, c
        return total
# @lc code=end
