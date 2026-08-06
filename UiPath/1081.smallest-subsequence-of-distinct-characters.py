#
# @lc app=leetcode id=1081 lang=python3
#
# [1081] Smallest Subsequence of Distinct Characters
#
# https://leetcode.com/problems/smallest-subsequence-of-distinct-characters/description/
#
# algorithms
# Medium (70.55%)
# Likes:    3123
# Dislikes: 210
# Total Accepted:    192K
# Total Submissions: 272K
# Testcase Example:  "\"bcabc\""
#
# Given a string s, return the lexicographically smallest subsequence of s that
# contains all the distinct characters of s exactly once.
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
# 1 <= s.length <= 1000
#
# s consists of lowercase English letters.
#
# Note: This question is the same as 316:
# https://leetcode.com/problems/remove-duplicate-letters/
#

# @lc code=start
class Solution:
    def smallestSubsequence(self, s: str) -> str:
        """
        Interview explanation:
        Same as 316 Remove Duplicate Letters. Build the lexicographically
        smallest subsequence with each distinct char once using a monotonic
        increasing stack: pop larger chars that still appear later.

        Algorithm (stack):
        - last index of each char; seen set; stack.
        - For c in s: if seen skip; while stack top > c and top appears later:
          pop/unsee; push c and mark seen.

        Complexity: O(n) time, O(1) alphabet space (26 letters).
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
