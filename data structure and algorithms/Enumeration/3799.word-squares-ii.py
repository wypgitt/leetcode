#
# @lc app=leetcode id=3799 lang=python3
#
# [3799] Word Squares II
#
# https://leetcode.com/problems/word-squares-ii/description/
#
# algorithms
# Medium (55.19%)
# Likes:    58
# Dislikes: 27
# Total Accepted:    20.3K
# Total Submissions: 36.8K
# Testcase Example:  "[\"able\",\"area\",\"echo\",\"also\"]"
#
#
# You are given a string array words, consisting of distinct 4-letter
# strings, each containing lowercase English letters.
#
# A word square consists of 4 distinct words: top, left, right and bottom,
# arranged as follows:
#
# top forms the top row.
#
# bottom forms the bottom row.
#
# left forms the left column (top to bottom).
#
# right forms the right column (top to bottom).
#
# It must satisfy:
#
# top[0] == left[0], top[3] == right[0]
#
# bottom[0] == left[3], bottom[3] == right[3]
#
# Return all valid distinct word squares, sorted in ascending
# lexicographic order by the 4-tuple (top, left, right, bottom)​​​​​​​.
#
# Example 1:
#
# Input: words = ["able","area","echo","also"]
#
# Output: [["able","area","echo","also"],["area","able","also","echo"]]
#
# Explanation:
#
# There are exactly two valid 4-word squares that satisfy all corner
# constraints:
#
# "able" (top), "area" (left), "echo" (right), "also" (bottom)
#
# top[0] == left[0] == 'a'
#
# top[3] == right[0] == 'e'
#
# bottom[0] == left[3] == 'a'
#
# bottom[3] == right[3] == 'o'
#
# "area" (top), "able" (left), "also" (right), "echo" (bottom)
#
# All corner constraints are satisfied.
#
# Thus, the answer is
# [["able","area","echo","also"],["area","able","also","echo"]].
#
# Example 2:
#
# Input: words = ["code","cafe","eden","edge"]
#
# Output: []
#
# Explanation:
#
# No combination of four words satisfies all four corner constraints.
# Thus, the answer is empty array [].
#
# Constraints:
#
# 4 <= words.length <= 15
#
# words[i].length == 4
#
# words[i] consists of only lowercase English letters.
#
# All words[i] are distinct.
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def wordSquares(self, words: List[str]) -> List[List[str]]:
        """
        Interview explanation:
        Enumerate distinct 4-tuples (top, left, right, bottom) whose four corner
        equalities hold. Sort words so lexicographic enumeration order is sorted.

        Algorithm:
        - Sort words; nested loops over four distinct indices.
        - Keep tuples with top[0]==left[0], top[3]==right[0],
          bottom[0]==left[3], bottom[3]==right[3].

        Complexity: O(n^4) time, O(1) extra space (output excluded).
        """
        words = sorted(words)
        n = len(words)
        ans: List[List[str]] = []
        for i in range(n):
            top = words[i]
            for j in range(n):
                if j == i:
                    continue
                left = words[j]
                if top[0] != left[0]:
                    continue
                for k in range(n):
                    if k == i or k == j:
                        continue
                    right = words[k]
                    if top[3] != right[0]:
                        continue
                    for h in range(n):
                        if h == i or h == j or h == k:
                            continue
                        bottom = words[h]
                        if bottom[0] == left[3] and bottom[3] == right[3]:
                            ans.append([top, left, right, bottom])
        return ans

    def wordSquares_lookup(self, words: List[str]) -> List[List[str]]:
        """
        Interview explanation:
        Alternate: index words by first letter / (first, last) to prune candidates.

        Algorithm:
        - Build lookup[c] and lookup[(c0,c3)]; nest over filtered index lists.

        Complexity: O(n^4) worst case, typically faster with hashing.
        """
        words = sorted(words)
        by_first: dict[str, List[int]] = defaultdict(list)
        by_ends: dict[tuple[str, str], List[int]] = defaultdict(list)
        for i, w in enumerate(words):
            by_first[w[0]].append(i)
            by_ends[(w[0], w[3])].append(i)
        ans: List[List[str]] = []
        for i, top in enumerate(words):
            for j in by_first[top[0]]:
                if j == i:
                    continue
                left = words[j]
                for k in by_first[top[3]]:
                    if k == i or k == j:
                        continue
                    right = words[k]
                    for h in by_ends[(left[3], right[3])]:
                        if h == i or h == j or h == k:
                            continue
                        ans.append([top, left, right, words[h]])
        return ans
# @lc code=end
