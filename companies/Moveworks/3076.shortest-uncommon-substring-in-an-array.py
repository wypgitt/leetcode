#
# @lc app=leetcode id=3076 lang=python3
#
# [3076] Shortest Uncommon Substring in an Array
#
# https://leetcode.com/problems/shortest-uncommon-substring-in-an-array/description/
#
# algorithms
# Medium (50.83%)
# Likes:    178
# Dislikes: 32
# Total Accepted:    39.2K
# Total Submissions: 77K
# Testcase Example:  "[\"cab\",\"ad\",\"bad\",\"c\"]"
#
#
# You are given an array arr of size n consisting of non-empty strings.
#
# Find a string array answer of size n such that:
#
# answer[i] is the shortest substring of arr[i] that does not occur as a
# substring in any other string in arr. If multiple such substrings exist,
# answer[i] should be the lexicographically smallest. And if no such
# substring exists, answer[i] should be an empty string.
#
# Return the array answer.
#
# Example 1:
#
# Input: arr = ["cab","ad","bad","c"]
# Output: ["ab","","ba",""]
# Explanation: We have the following:
# - For the string "cab", the shortest substring that does not occur in
# any other string is either "ca" or "ab", we choose the lexicographically
# smaller substring, which is "ab".
# - For the string "ad", there is no substring that does not occur in any
# other string.
# - For the string "bad", the shortest substring that does not occur in
# any other string is "ba".
# - For the string "c", there is no substring that does not occur in any
# other string.
#
# Example 2:
#
# Input: arr = ["abc","bcd","abcd"]
# Output: ["","","abcd"]
# Explanation: We have the following:
# - For the string "abc", there is no substring that does not occur in any
# other string.
# - For the string "bcd", there is no substring that does not occur in any
# other string.
# - For the string "abcd", the shortest substring that does not occur in
# any other string is "abcd".
#
# Constraints:
#
# n == arr.length
#
# 2 <= n <= 100
#
# 1 <= arr[i].length <= 20
#
# arr[i] consists only of lowercase English letters.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def shortestSubstrings(self, arr: List[str]) -> List[str]:
        """
        Interview explanation:
        For each string, find its shortest substring that appears in no other
        string; break ties lexicographically (empty if none). Lengths <= 20.

        Algorithm:
        - Map each substring to the set of string indices containing it.
        - For each i, scan substrings by increasing length then lex order;
          pick the first whose occurrence set is exactly {i}.

        Complexity: O(n^2 * L^3) worst with small L<=20, O(n L^2) space.
        """
        n = len(arr)
        occ: dict = defaultdict(set)
        for i, s in enumerate(arr):
            seen = set()
            for l in range(len(s)):
                for r in range(l + 1, len(s) + 1):
                    sub = s[l:r]
                    if sub not in seen:
                        seen.add(sub)
                        occ[sub].add(i)

        ans = [""] * n
        for i, s in enumerate(arr):
            best = None
            for length in range(1, len(s) + 1):
                cands = []
                for l in range(len(s) - length + 1):
                    sub = s[l : l + length]
                    if occ[sub] == {i}:
                        cands.append(sub)
                if cands:
                    best = min(cands)
                    break
            ans[i] = best if best is not None else ""
        return ans
# @lc code=end
