#
# @lc app=leetcode id=541 lang=python3
#
# [541] Reverse String II
#
# https://leetcode.com/problems/reverse-string-ii/description/
#
# algorithms
# Easy (54.27%)
# Likes:    2414
# Dislikes: 4516
# Total Accepted:    412K
# Total Submissions: 760K
# Testcase Example:  "\"abcdefg\""
#
# Given a string s and an integer k, reverse the first k characters for every
# 2k characters counting from the start of the string.
#
# If there are fewer than k characters left, reverse all of them. If there are
# less than 2k but greater than or equal to k characters, then reverse the
# first k characters and leave the other as original.
#
# Example 1:
#
# Input: s = "abcdefg", k = 2
# Output: "bacdfeg"
#
# Example 2:
#
# Input: s = "abcd", k = 2
# Output: "bacd"
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of only lowercase English letters.
#
# 1 <= k <= 10^4
#

# @lc code=start
class Solution:
    def reverseStr(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Process the string in blocks of 2k: reverse the first k characters of
        each block; leave the rest of the block as-is.

        Algorithm:
        - Convert to list; for i in 0, 2k, 4k, ... reverse s[i:i+k].

        Complexity: O(n) time, O(n) space for the list.
        """
        chars = list(s)
        for i in range(0, len(chars), 2 * k):
            chars[i : i + k] = reversed(chars[i : i + k])
        return "".join(chars)
# @lc code=end

