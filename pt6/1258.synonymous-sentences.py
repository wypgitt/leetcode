#
# @lc app=leetcode id=1258 lang=python3
#
# [1258] Synonymous Sentences
#
# https://leetcode.com/problems/synonymous-sentences/description/
#
# algorithms
# Medium (57.25%)
# Likes:    374
# Dislikes: 171
# Total Accepted:    29.7K
# Total Submissions: 51.9K
# Testcase Example:  '[["happy","joy"],["sad","sorrow"],["joy","cheerful"]]\n' +
# '"I am happy today but was sad yesterday"'
#
# You are given a list of equivalent string pairs synonyms where synonyms[i] =
# [si, ti] indicates that si and ti are equivalent strings. You are also given
# a sentence text.
# 
# Return all possible synonymous sentences sorted lexicographically.
# 
# 
# Example 1:
# 
# 
# Input: synonyms = [["happy","joy"],["sad","sorrow"],["joy","cheerful"]], text
# = "I am happy today but was sad yesterday"
# Output: ["I am cheerful today but was sad yesterday","I am cheerful today but
# was sorrow yesterday","I am happy today but was sad yesterday","I am happy
# today but was sorrow yesterday","I am joy today but was sad yesterday","I am
# joy today but was sorrow yesterday"]
# 
# 
# Example 2:
# 
# 
# Input: synonyms = [["happy","joy"],["cheerful","glad"]], text = "I am happy
# today but was sad yesterday"
# Output: ["I am happy today but was sad yesterday","I am joy today but was sad
# yesterday"]
# 
# 
# 
# Constraints:
# 
# 
# 0 <= synonyms.length <= 10
# synonyms[i].length == 2
# 1 <= si.length, ti.length <= 10
# si != ti
# text consists of at most 10 words.
# All the pairs of synonyms are unique.
# The words of text are separated by single spaces.
# 
# 
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def generateSentences(self, synonyms: List[List[str]], text: str) -> List[str]:
        parent = {}

        def find(word: str) -> str:
            parent.setdefault(word, word)
            if parent[word] != word:
                parent[word] = find(parent[word])
            return parent[word]

        def union(a: str, b: str) -> None:
            root_a = find(a)
            root_b = find(b)
            if root_a != root_b:
                parent[root_b] = root_a

        for a, b in synonyms:
            union(a, b)

        groups = defaultdict(list)
        for word in list(parent):
            groups[find(word)].append(word)

        choices = {}
        for words in groups.values():
            sorted_words = sorted(words)
            for word in sorted_words:
                choices[word] = sorted_words

        ans = []
        sentence = text.split()

        def backtrack(index: int, path: List[str]) -> None:
            if index == len(sentence):
                ans.append(" ".join(path))
                return

            for word in choices.get(sentence[index], [sentence[index]]):
                path.append(word)
                backtrack(index + 1, path)
                path.pop()

        backtrack(0, [])
        return ans
# @lc code=end

# Explanation
# -----------
# Synonyms form connected components, so union-find groups all words that can
# replace each other. After building components, sort each component's words.
# During backtracking over the sentence, a word either expands to its sorted
# synonym group or stays as itself if it has no synonyms.
#
# Union-find is chosen because synonym relationships are transitive:
# happy~joy and joy~cheerful means happy, joy, and cheerful are all choices.
#
# Iterating choices in sorted order at each position produces lexicographic
# sentence order, because the first differing word determines sentence order.
#
# Edge cases: words not present in synonyms; multiple synonym chains; duplicate
# relationships are harmless.
#
# Time complexity: O(S alpha(W) + R * L), where R is the number of generated
# sentences and L is sentence length. Space complexity: O(W + R * L).
