#
# @lc app=leetcode id=320 lang=python3
#
# [320] Generalized Abbreviation
#
# https://leetcode.com/problems/generalized-abbreviation/description/
#
# algorithms
# Medium (60.90%)
# Likes:    720
# Dislikes: 233
# Total Accepted:    77.9K
# Total Submissions: 127.8K
# Testcase Example:  "\"word\""
#
#
# A word's generalized abbreviation can be constructed by taking any
# number of non-overlapping and non-adjacent substrings and replacing them
# with their respective lengths.
#
# For example, "abcde" can be abbreviated into:
#
# "a3e" ("bcd" turned into "3")
#
# "1bcd1" ("a" and "e" both turned into "1")
#
# "5" ("abcde" turned into "5")
#
# "abcde" (no substrings replaced)
#
# However, these abbreviations are invalid:
#
# "23" ("ab" turned into "2" and "cde" turned into "3") is invalid as the
# substrings chosen are adjacent.
#
# "22de" ("ab" turned into "2" and "bc" turned into "2") is invalid as the
# substring chosen overlap.
#
# Given a string word, return a list of all the possible generalized
# abbreviations of word. Return the answer in any order.
#
# Example 1:
#
# Input: word = "word"
# Output:
# ["4","3d","2r1","2rd","1o2","1o1d","1or1","1ord","w3","w2d","w1r1","w1rd","wo2","wo1d","wor1","word"]
#
# Example 2:
#
# Input: word = "a"
# Output: ["1","a"]
#
# Constraints:
#
# 1 <= word.length <= 15
#
# word consists of only lowercase English letters.
#
# @lc code=start
from typing import List


class Solution:
    def generateAbbreviations(self, word: str) -> List[str]:
        """
        Interview explanation:
        For each character, either keep it or abbreviate it as part of a count.
        Backtrack building the current string; when abbreviating, accumulate count.

        Algorithm (backtrack — primary):
        - dfs(i, path, count): at end flush count; else branch keep (flush count
          then append char) or abbreviate (count+1).

        Complexity: O(2^n * n) time/space to build all abbreviations.
        """
        n = len(word)
        ans: List[str] = []

        def dfs(i: int, path: List[str], count: int) -> None:
            if i == n:
                if count:
                    path.append(str(count))
                ans.append("".join(path))
                if count:
                    path.pop()
                return
            # abbreviate
            dfs(i + 1, path, count + 1)
            # keep char
            if count:
                path.append(str(count))
            path.append(word[i])
            dfs(i + 1, path, 0)
            path.pop()
            if count:
                path.pop()

        dfs(0, [], 0)
        return ans

    def generateAbbreviationsBit(self, word: str) -> List[str]:
        """
        Interview explanation:
        Alternate: for mask in 0..(1<<n)-1, bit 1 means abbreviate that position;
        compress consecutive abbreviated bits into a number.

        Complexity: O(2^n * n).
        """
        n = len(word)
        ans = []
        for mask in range(1 << n):
            parts = []
            count = 0
            for i in range(n):
                if mask & (1 << i):
                    count += 1
                else:
                    if count:
                        parts.append(str(count))
                        count = 0
                    parts.append(word[i])
            if count:
                parts.append(str(count))
            ans.append("".join(parts))
        return ans
# @lc code=end

