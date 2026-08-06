#
# @lc app=leetcode id=1255 lang=python3
#
# [1255] Maximum Score Words Formed by Letters
#
# https://leetcode.com/problems/maximum-score-words-formed-by-letters/description/
#
# algorithms
# Hard (81.48%)
# Likes:    1874
# Dislikes: 119
# Total Accepted:    139K
# Total Submissions: 170K
# Testcase Example:  "[\"dog\",\"cat\",\"dad\",\"good\"]"
#
# Given a list of words, list of single letters (might be repeating) and score
# of every character.
#
# Return the maximum score of any valid set of words formed by using the given
# letters (words[i] cannot be used two or more times).
#
# It is not necessary to use all characters in letters and each letter can only
# be used once. Score of letters 'a', 'b', 'c', ... ,'z' is given by score[0],
# score[1], ... , score[25] respectively.
#
# Example 1:
#
# Input: words = ["dog","cat","dad","good"], letters =
# ["a","a","c","d","d","d","g","o","o"], score =
# [1,0,9,5,0,0,3,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0]
# Output: 23
# Explanation:
# Score a=1, c=9, d=5, g=3, o=2
# Given letters, we can form the words "dad" (5+1+5) and "good" (3+2+2+5) with
# a score of 23.
# Words "dad" and "dog" only get a score of 21.
#
# Example 2:
#
# Input: words = ["xxxz","ax","bx","cx"], letters =
# ["z","a","b","c","x","x","x"], score =
# [4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0,10]
# Output: 27
# Explanation:
# Score a=4, b=4, c=4, x=5, z=10
# Given letters, we can form the words "ax" (4+5), "bx" (4+5) and "cx" (4+5)
# with a score of 27.
# Word "xxxz" only get a score of 25.
#
# Example 3:
#
# Input: words = ["leetcode"], letters = ["l","e","t","c","o","d"], score =
# [0,0,1,1,1,0,0,0,0,0,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,0]
# Output: 0
# Explanation:
# Letter "e" can only be used once.
#
# Constraints:
#
# 1 <= words.length <= 14
#
# 1 <= words[i].length <= 15
#
# 1 <= letters.length <= 100
#
# letters[i].length == 1
#
# score.length == 26
#
# 0 <= score[i] <= 10
#
# words[i], letters[i] contains only lower case English letters.
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def maxScoreWords(
        self, words: List[str], letters: List[str], score: List[int]
    ) -> int:
        """
        Interview explanation:
        Each word used at most once; letters are a multiset. Maximize sum of
        letter scores over a subset of words that fit the letter budget.
        Backtrack over include/exclude each word (n<=14).

        Algorithm:
        - avail = Counter(letters); word_counts and word_scores precomputed.
        - DFS(i): skip word i; or if can subtract counts, add score and recurse.
        - Track max total.

        Complexity: O(2^n * L) time with L word length; O(n) stack.
        """
        avail = Counter(letters)
        n = len(words)
        wcnt = [Counter(w) for w in words]
        wscore = [sum(score[ord(c) - 97] for c in w) for w in words]
        best = 0

        def dfs(i: int, cur: int) -> None:
            nonlocal best
            if i == n:
                best = max(best, cur)
                return
            dfs(i + 1, cur)
            if all(avail[c] >= need for c, need in wcnt[i].items()):
                avail.subtract(wcnt[i])
                dfs(i + 1, cur + wscore[i])
                avail.update(wcnt[i])

        dfs(0, 0)
        return best
# @lc code=end
