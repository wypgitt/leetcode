#
# @lc app=leetcode id=267 lang=python3
#
# [267] Palindrome Permutation II
#
# https://leetcode.com/problems/palindrome-permutation-ii/description/
#
# algorithms
# Medium (42.38%)
# Likes:    900
# Dislikes: 98
# Total Accepted:    76.4K
# Total Submissions: 180.2K
# Testcase Example:  "\"aabb\""
#
#
# Given a string s, return all the palindromic permutations (without
# duplicates) of it.
#
# You may return the answer in any order. If s has no palindromic
# permutation, return an empty list.
#
# Example 1:
#
# Input: s = "aabb"
# Output: ["abba","baab"]
#
# Example 2:
#
# Input: s = "abc"
# Output: []
#
# Constraints:
#
# 1 <= s.length <= 16
#
# s consists of only lowercase English letters.
#
# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def generatePalindromes(self, s: str) -> List[str]:
        """
        Interview explanation:
        Build all palindromic permutations: at most one odd-count char (center);
        backtrack permutations of the half multiset, then mirror.

        Algorithm:
        - Count chars; if >1 odd counts, return [].
        - mid = the odd char (or ""); half = chars with count//2 each.
        - Backtrack unique permutations of half; append mid + reverse(half).

        Complexity: O((n/2)! * n) time worst case, O(n) recursion space.
        """
        cnt = Counter(s)
        mid = ""
        odds = 0
        half: List[str] = []
        for ch, c in cnt.items():
            if c % 2:
                odds += 1
                mid = ch
                if odds > 1:
                    return []
            half.extend([ch] * (c // 2))

        half.sort()
        used = [False] * len(half)
        ans: List[str] = []
        path: List[str] = []

        def dfs() -> None:
            if len(path) == len(half):
                left = "".join(path)
                ans.append(left + mid + left[::-1])
                return
            for i in range(len(half)):
                if used[i]:
                    continue
                if i > 0 and half[i] == half[i - 1] and not used[i - 1]:
                    continue
                used[i] = True
                path.append(half[i])
                dfs()
                path.pop()
                used[i] = False

        dfs()
        return ans
# @lc code=end
