#
# @lc app=leetcode id=316 lang=python3
#
# [316] Remove Duplicate Letters
#
# https://leetcode.com/problems/remove-duplicate-letters/description/
#
# algorithms
# Medium (54.2%)
# Likes:    9464
# Dislikes: 709
# Total Accepted:    481K
# Total Submissions: 887K
# Testcase Example:  "\"bcabc\""
#
# Given a string s, remove duplicate letters so that every letter appears once
# and only once. You must make sure your result is the smallest in
# lexicographical order among all possible results.
#
# Example 1:
#
# Input: s = "bcabc"
# Output: "abc"
#
# Example 2:
#
# Input: s = "cbacdcbc"
# Output: "acdb"
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of lowercase English letters.
#
# Note: This question is the same as 1081:
# https://leetcode.com/problems/smallest-subsequence-of-distinct-characters/
#

# @lc code=start
class Solution:
    def removeDuplicateLetters(self, s: str) -> str:
        """
        Interview explanation:
        Smallest lexicographical subsequence using each distinct letter once.
        Greedy stack: pop larger letters that still appear later when a smaller
        new letter arrives.

        Algorithm:
        - last[c] = last index of c; seen set for letters in stack.
        - For each char: if not seen, while stack top > c and appears later, pop.
        - Push c and mark seen.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        last = {c: i for i, c in enumerate(s)}
        stack = []
        seen = set()
        for i, c in enumerate(s):
            if c in seen:
                continue
            while stack and c < stack[-1] and last[stack[-1]] > i:
                seen.remove(stack.pop())
            stack.append(c)
            seen.add(c)
        return "".join(stack)
# @lc code=end

