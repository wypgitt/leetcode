#
# @lc app=leetcode id=1209 lang=python3
#
# [1209] Remove All Adjacent Duplicates in String II
#
# https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string-ii/description/
#
# algorithms
# Medium (61.24%)
# Likes:    6105
# Dislikes: 123
# Total Accepted:    424.8K
# Total Submissions: 693.5K
# Testcase Example:  '"abcd"\n2'
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
# 
# Example 1:
# 
# 
# Input: s = "abcd", k = 2
# Output: "abcd"
# Explanation: There's nothing to delete.
# 
# Example 2:
# 
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
# 
# Input: s = "pbbcggttciiippooaais", k = 2
# Output: "ps"
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# 2 <= k <= 10^4
# s only contains lowercase English letters.
# 
# 
#

# @lc code=start
class Solution:
    def removeDuplicates(self, s: str, k: int) -> str:
        stack = []

        for ch in s:
            if stack and stack[-1][0] == ch:
                stack[-1][1] += 1
            else:
                stack.append([ch, 1])

            if stack[-1][1] == k:
                stack.pop()

        return "".join(ch * count for ch, count in stack)
# @lc code=end

# Explanation
# -----------
# The stack stores compressed runs as [character, count]. For each new
# character, either extend the top run or start a new run. When a run reaches
# length k, pop it immediately. This is exactly what the deletion process does:
# after removing a run, the characters on both sides may become adjacent, and
# the stack exposes that new adjacency automatically.
#
# The stack is the right data structure because the only run that can change
# after reading the next character is the most recent surviving run.
#
# Interview trace: for "deeedbbcccbdaa" with k=3, "eee" is popped, later
# "ccc" is popped, then the surrounding "bbb" becomes a run and is popped,
# leaving "aa".
#
# Edge cases: k = 1 removes every character; alternating characters never
# accumulate; chained removals are handled because popped groups reveal the
# previous stack top.
#
# Time complexity: O(n), each character is pushed once and popped at most once.
# Space complexity: O(n) for the stack in the worst case.
