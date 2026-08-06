#
# @lc app=leetcode id=1209 lang=python3
#
# [1209] Remove All Adjacent Duplicates in String II
#
# https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string-ii/description/
#
# algorithms
# Medium (61.7%)
# Likes:    6143
# Dislikes: 125
# Total Accepted:    438K
# Total Submissions: 711K
# Testcase Example:  "\"abcd\""
#
# You are given a string s and an integer k, a k duplicate removal consists of
# choosing k adjacent and equal letters from s and removing them, causing the
# left and the right side of the deleted substring to concatenate together.
#
# We repeatedly make k duplicate removals on s until we no longer can.
#
# Return the final string after all such duplicate removals have been made. It
# is guaranteed that the answer is unique.
#
# Example 1:
#
# Input: s = "abcd", k = 2
# Output: "abcd"
# Explanation: There's nothing to delete.
#
# Example 2:
#
# Input: s = "deeedbbcccbdaa", k = 3
# Output: "aa"
# Explanation:
# First delete "eee" and "ccc", get "ddbbbdaa"
# Then delete "bbb", get "dddaa"
# Finally delete "ddd", get "aa"
#
# Example 3:
#
# Input: s = "pbbcggttciiippooaais", k = 2
# Output: "ps"
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# 2 <= k <= 10^4
#
# s only contains lowercase English letters.
#



# @lc code=start
class Solution:
    def removeDuplicates(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Repeatedly remove k consecutive equal chars. Stack of (char, count);
        when count hits k pop. Final stack rebuilds the string.

        Algorithm:
        - For each char: if top same, increment; else push (c,1); if count==k pop
        - Join char*count for remaining stack

        Complexity: O(n) time, O(n) space.
        """
        stack = []  # (char, count)
        for ch in s:
            if stack and stack[-1][0] == ch:
                stack[-1] = (ch, stack[-1][1] + 1)
                if stack[-1][1] == k:
                    stack.pop()
            else:
                stack.append((ch, 1))
        return "".join(ch * cnt for ch, cnt in stack)

    def removeDuplicates_twostack(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Alternate: char stack + separate count stack (same algorithm, clearer
        for interviews that prefer parallel stacks).

        Algorithm:
        - chars[], cnts[]; mirror push/pop when cnt reaches k

        Complexity: O(n) time, O(n) space.
        """
        chars, cnts = [], []
        for ch in s:
            if chars and chars[-1] == ch:
                cnts[-1] += 1
                if cnts[-1] == k:
                    chars.pop()
                    cnts.pop()
            else:
                chars.append(ch)
                cnts.append(1)
        return "".join(c * n for c, n in zip(chars, cnts))
# @lc code=end
