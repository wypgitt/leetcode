#
# @lc app=leetcode id=1258 lang=python3
#
# [1258] Synonymous Sentences
#
# https://leetcode.com/problems/synonymous-sentences/description/
#
# algorithms
# Medium (57.48%)
# Likes:    375
# Dislikes: 171
# Total Accepted:    30.4K
# Total Submissions: 52.9K
# Testcase Example:  "[[\"happy\",\"joy\"],[\"sad\",\"sorrow\"],[\"joy\",\"cheerful\"]]\n\"I am happy today but was sad yesterday\""
#
#
# You are given a list of equivalent string pairs synonyms where
# synonyms[i] = [s_i, t_i] indicates that s_i and t_i are equivalent
# strings. You are also given a sentence text.
#
# Return all possible synonymous sentences sorted lexicographically.
#
# Example 1:
#
# Input: synonyms = [["happy","joy"],["sad","sorrow"],["joy","cheerful"]],
# text = "I am happy today but was sad yesterday"
# Output: ["I am cheerful today but was sad yesterday","I am cheerful
# today but was sorrow yesterday","I am happy today but was sad
# yesterday","I am happy today but was sorrow yesterday","I am joy today
# but was sad yesterday","I am joy today but was sorrow yesterday"]
#
# Example 2:
#
# Input: synonyms = [["happy","joy"],["cheerful","glad"]], text = "I am
# happy today but was sad yesterday"
# Output: ["I am happy today but was sad yesterday","I am joy today but
# was sad yesterday"]
#
# Constraints:
#
# 0 <= synonyms.length <= 10
#
# synonyms[i].length == 2
#
# 1 <= s_i.length,_ t_i.length <= 10
#
# s_i != t_i
#
# text consists of at most 10 words.
#
# All the pairs of synonyms are unique.
#
# The words of text are separated by single spaces.
#
# @lc code=start

from typing import List
from collections import defaultdict


class Solution:
    def generateSentences(
        self, synonyms: List[List[str]], text: str
    ) -> List[str]:
        """
        Interview explanation:
        Premium. Synonyms are undirected equivalences. Union words in synonym
        pairs, then for each text token expand to all words in its component
        (or itself). Backtrack all combinations; sort lexicographically.

        Algorithm:
        - UF unite synonym pairs; build component lists sorted.
        - Split text; DFS replace each word by sorted component choices.
        - Sort final sentences.

        Complexity: O(C * L + S log S) where C is product of options, L words.
        """
        parent = {}

        def find(x: str) -> str:
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: str, b: str) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for a, b in synonyms:
            union(a, b)

        groups = defaultdict(list)
        for w in list(parent):
            groups[find(w)].append(w)
        for g in groups.values():
            g.sort()

        words = text.split()
        ans: List[str] = []

        def dfs(i: int, path: List[str]) -> None:
            if i == len(words):
                ans.append(" ".join(path))
                return
            w = words[i]
            options = groups[find(w)] if w in parent else [w]
            for opt in options:
                path.append(opt)
                dfs(i + 1, path)
                path.pop()

        dfs(0, [])
        ans.sort()
        return ans
# @lc code=end
