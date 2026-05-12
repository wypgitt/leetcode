#
# @lc app=leetcode id=1247 lang=python3
#
# [1247] Minimum Swaps to Make Strings Equal
#
# https://leetcode.com/problems/minimum-swaps-to-make-strings-equal/description/
#
# algorithms
# Medium (65.32%)
# Likes:    1470
# Dislikes: 252
# Total Accepted:    52.2K
# Total Submissions: 79.9K
# Testcase Example:  '"xx"\n"yy"'
#
# You are given two strings s1 and s2 of equal length consisting of letters "x"
# and "y" only. Your task is to make these two strings equal to each other. You
# can swap any two characters that belong to different strings, which means:
# swap s1[i] and s2[j].
# 
# Return the minimum number of swaps required to make s1 and s2 equal, or
# return -1 if it is impossible to do so.
# 
# 
# Example 1:
# 
# 
# Input: s1 = "xx", s2 = "yy"
# Output: 1
# Explanation: Swap s1[0] and s2[1], s1 = "yx", s2 = "yx".
# 
# 
# Example 2:
# 
# 
# Input: s1 = "xy", s2 = "yx"
# Output: 2
# Explanation: Swap s1[0] and s2[0], s1 = "yy", s2 = "xx".
# Swap s1[0] and s2[1], s1 = "xy", s2 = "xy".
# Note that you cannot swap s1[0] and s1[1] to make s1 equal to "yx", cause we
# can only swap chars in different strings.
# 
# 
# Example 3:
# 
# 
# Input: s1 = "xx", s2 = "xy"
# Output: -1
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s1.length, s2.length <= 1000
# s1.length == s2.length
# s1, s2 only contain 'x' or 'y'.
# 
# 
#

# @lc code=start
class Solution:
    def minimumSwap(self, s1: str, s2: str) -> int:
        xy = yx = 0

        for a, b in zip(s1, s2):
            if a == "x" and b == "y":
                xy += 1
            elif a == "y" and b == "x":
                yx += 1

        if (xy + yx) % 2 == 1:
            return -1

        return xy // 2 + yx // 2 + 2 * (xy % 2)
# @lc code=end

# Explanation
# -----------
# Matching positions need no work. Mismatches are either "xy" or "yx". Two
# mismatches of the same type can be fixed in one swap: xy + xy, or yx + yx.
# If one xy and one yx remain, they need two swaps.
#
# If the total number of mismatches is odd, there is no way to pair them, so
# return -1.
#
# Counting mismatch types is enough because all characters are only x or y;
# positions themselves do not matter after we know the mismatch categories.
#
# Edge cases: already equal strings return 0; one xy and one yx returns 2;
# odd mismatch count returns -1.
#
# Time complexity: O(n).
# Space complexity: O(1).
