#
# @lc app=leetcode id=394 lang=python3
#
# [394] Decode String
#
# https://leetcode.com/problems/decode-string/description/
#
# algorithms
# Medium (63.03%)
# Likes:    14147
# Dislikes: 711
# Total Accepted:    1.3M
# Total Submissions: 2.0M
# Testcase Example:  "\"3[a]2[bc]\""
#
# Given an encoded string, return its decoded string.
#
# The encoding rule is: k[encoded_string], where the encoded_string inside the
# square brackets is being repeated exactly k times. Note that k is guaranteed
# to be a positive integer.
#
# You may assume that the input string is always valid; there are no extra
# white spaces, square brackets are well-formed, etc. Furthermore, you may
# assume that the original data does not contain any digits and that digits are
# only for those repeat numbers, k. For example, there will not be input like
# 3a or 2[4].
#
# The test cases are generated so that the length of the output will never
# exceed 10^5.
#
# Example 1:
#
# Input: s = "3[a]2[bc]"
# Output: "aaabcbc"
#
# Example 2:
#
# Input: s = "3[a2[c]]"
# Output: "accaccacc"
#
# Example 3:
#
# Input: s = "2[abc]3[cd]ef"
# Output: "abcabccdcdcdef"
#
# Constraints:
#
# 1 <= s.length <= 30
#
# s consists of lowercase English letters, digits, and square brackets '[]'.
#
# s is guaranteed to be a valid input.
#
# All the integers in s are in the range [1, 300].
#

# @lc code=start
class Solution:
    def decodeString(self, s: str) -> str:
        """
        Interview explanation:
        Nested k[encoded] decoding with a stack. Push (prev_string, repeat)
        when seeing '[', pop and expand on ']'. Digits accumulate the count.

        Algorithm:
        - stack, cur, num = [], "", 0
        - digit: num = num*10 + d
        - '[': push (cur, num); reset cur, num
        - ']': prev, n = pop; cur = prev + cur * n
        - else: cur += ch

        Complexity: O(output length) time/space.
        """
        stack = []
        cur = []
        num = 0
        for ch in s:
            if ch.isdigit():
                num = num * 10 + int(ch)
            elif ch == "[":
                stack.append(("".join(cur), num))
                cur = []
                num = 0
            elif ch == "]":
                prev, n = stack.pop()
                cur = [prev + "".join(cur) * n]
            else:
                cur.append(ch)
        return "".join(cur)
# @lc code=end
