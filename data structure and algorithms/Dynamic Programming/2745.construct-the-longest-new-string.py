#
# @lc app=leetcode id=2745 lang=python3
#
# [2745] Construct the Longest New String
#
# https://leetcode.com/problems/construct-the-longest-new-string/description/
#
# algorithms
# Medium (55.04%)
# Likes:    343
# Dislikes: 29
# Total Accepted:    27.7K
# Total Submissions: 50.4K
# Testcase Example:  "2\n5\n1"
#
# You are given three integers x, y, and z.
#
# You have x strings equal to "AA", y strings equal to "BB", and z strings equal
# to "AB". You want to choose some (possibly all or none) of these strings and
# concatenate them in some order to form a new string. This new string must not
# contain "AAA" or "BBB" as a substring.
#
# Return the maximum possible length of the new string.
#
# A substring is a contiguous non-empty sequence of characters within a string.
#
#
#
# Example 1:
#
# Input: x = 2, y = 5, z = 1
# Output: 12
# Explanation: We can concatenate the strings "BB", "AA", "BB", "AA", "BB", and
# "AB" in that order. Then, our new string is "BBAABBAABBAB".
# That string has length 12, and we can show that it is impossible to construct
# a string of longer length.
#
# Example 2:
#
# Input: x = 3, y = 2, z = 2
# Output: 14
# Explanation: We can concatenate the strings "AB", "AB", "AA", "BB", "AA",
# "BB", and "AA" in that order. Then, our new string is "ABABAABBAABBAA".
# That string has length 14, and we can show that it is impossible to construct
# a string of longer length.
#
#
#
# Constraints:
#
#
# 1 <= x, y, z <= 50
#

# @lc code=start
class Solution:
    def longestString(self, x: int, y: int, z: int) -> int:
        """
        Interview explanation:
        Concatenate x "AA", y "BB", z "AB" without "AAA"/"BBB"; maximize total length (*2 chars each).

        Algorithm:
        - "AB" never creates AAA/BBB. Use min(x,y)*2 + (1 if x!=y else 0) of AA/BB pairs
          plus all z; length = 2 * (pieces).

        Complexity: O(1) time/space.
        """
        return 2 * (2 * min(x, y) + (1 if x != y else 0) + z)
# @lc code=end
