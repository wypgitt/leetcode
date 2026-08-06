#
# @lc app=leetcode id=3170 lang=python3
#
# [3170] Lexicographically Minimum String After Removing Stars
#
# https://leetcode.com/problems/lexicographically-minimum-string-after-removing-stars/description/
#
# algorithms
# Medium (50.86%)
# Likes:    601
# Dislikes: 89
# Total Accepted:    121.1K
# Total Submissions: 238.1K
# Testcase Example:  "\"aaba*\""
#
#
# You are given a string s. It may contain any number of '*' characters.
# Your task is to remove all '*' characters.
#
# While there is a '*', do the following operation:
#
# Delete the leftmost '*' and the smallest non-'*' character to its left.
# If there are several smallest characters, you can delete any of them.
#
# Return the lexicographically smallest resulting string after removing
# all '*' characters.
#
# Example 1:
#
# Input: s = "aaba*"
#
# Output: "aab"
#
# Explanation:
#
# We should delete one of the 'a' characters with '*'. If we choose s[3],
# s becomes the lexicographically smallest.
#
# Example 2:
#
# Input: s = "abc"
#
# Output: "abc"
#
# Explanation:
#
# There is no '*' in the string.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of lowercase English letters and '*'.
#
# The input is generated such that it is possible to delete all '*'
# characters.
#

# @lc code=start
import heapq


class Solution:
    def clearStars(self, s: str) -> str:
        """
        Interview explanation:
        Each '*' deletes the smallest letter to its left (prefer rightmost on
        ties) to keep the remaining string lexicographically smallest.

        Algorithm:
        - Min-heap of (char, -index) for live letters; on '*', pop and mark deleted.
        - Rebuild string from undeleted chars.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(s)
        deleted = [False] * n
        heap: list[tuple[str, int]] = []
        for i, c in enumerate(s):
            if c == "*":
                _, neg_j = heapq.heappop(heap)
                deleted[-neg_j] = True
                deleted[i] = True
            else:
                heapq.heappush(heap, (c, -i))
        return "".join(c for i, c in enumerate(s) if not deleted[i])

    def clearStars_stacks(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: 26 stacks of indices per letter; on '*', pop from the
        smallest non-empty stack (rightmost index naturally on top).

        Algorithm:
        - Push indices into stacks[ord(c)-a]; star pops from first non-empty.
        - Filter marked indices.

        Complexity: O(n * 26) time, O(n) space.
        """
        stacks: list[list[int]] = [[] for _ in range(26)]
        deleted = [False] * len(s)
        for i, c in enumerate(s):
            if c == "*":
                deleted[i] = True
                for st in stacks:
                    if st:
                        deleted[st.pop()] = True
                        break
            else:
                stacks[ord(c) - 97].append(i)
        return "".join(c for i, c in enumerate(s) if not deleted[i])
# @lc code=end
