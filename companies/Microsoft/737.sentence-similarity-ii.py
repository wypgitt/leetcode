#
# @lc app=leetcode id=737 lang=python3
#
# [737] Sentence Similarity II
#
# https://leetcode.com/problems/sentence-similarity-ii/description/
#
# algorithms
# Medium (51.39%)
# Likes:    855
# Dislikes: 43
# Total Accepted:    80.1K
# Total Submissions: 155.9K
# Testcase Example:  "[\"great\",\"acting\",\"skills\"]\n[\"fine\",\"drama\",\"talent\"]\n[[\"great\",\"good\"],[\"fine\",\"good\"],[\"drama\",\"acting\"],[\"skills\",\"talent\"]]"
#
#
# We can represent a sentence as an array of words, for example, the
# sentence "I am happy with leetcode" can be represented as arr =
# ["I","am",happy","with","leetcode"].
#
# Given two sentences sentence1 and sentence2 each represented as a string
# array and given an array of string pairs similarPairs where
# similarPairs[i] = [x_i, y_i] indicates that the two words x_i and y_i
# are similar.
#
# Return true if sentence1 and sentence2 are similar, or false if they are
# not similar.
#
# Two sentences are similar if:
#
# They have the same length (i.e., the same number of words)
#
# sentence1[i] and sentence2[i] are similar.
#
# Notice that a word is always similar to itself, also notice that the
# similarity relation is transitive. For example, if the words a and b are
# similar, and the words b and c are similar, then a and c are similar.
#
# Example 1:
#
# Input: sentence1 = ["great","acting","skills"], sentence2 =
# ["fine","drama","talent"], similarPairs =
# [["great","good"],["fine","good"],["drama","acting"],["skills","talent"]]
# Output: true
# Explanation: The two sentences have the same length and each word i of
# sentence1 is also similar to the corresponding word in sentence2.
#
# Example 2:
#
# Input: sentence1 = ["I","love","leetcode"], sentence2 =
# ["I","love","onepiece"], similarPairs =
# [["manga","onepiece"],["platform","anime"],["leetcode","platform"],["anime","manga"]]
# Output: true
# Explanation: "leetcode" --> "platform" --> "anime" --> "manga" -->
# "onepiece".
# Since "leetcode is similar to "onepiece" and the first two words are the
# same, the two sentences are similar.
#
# Example 3:
#
# Input: sentence1 = ["I","love","leetcode"], sentence2 =
# ["I","love","onepiece"], similarPairs =
# [["manga","hunterXhunter"],["platform","anime"],["leetcode","platform"],["anime","manga"]]
# Output: false
# Explanation: "leetcode" is not similar to "onepiece".
#
# Constraints:
#
# 1 <= sentence1.length, sentence2.length <= 1000
#
# 1 <= sentence1[i].length, sentence2[i].length <= 20
#
# sentence1[i] and sentence2[i] consist of lower-case and upper-case
# English letters.
#
# 0 <= similarPairs.length <= 2000
#
# similarPairs[i].length == 2
#
# 1 <= x_i.length, y_i.length <= 20
#
# x_i and y_i consist of English letters.
#
# @lc code=start
from typing import Dict, List


class Solution:
    def areSentencesSimilarTwo(
        self, sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]
    ) -> bool:
        """
        Interview explanation:
        Premium. Like Sentence Similarity but similarity is transitive: union all
        similar pairs with Union-Find, then aligned words must be equal or in the
        same component.

        Algorithm:
        - If lengths differ: False
        - UF-union each similar pair
        - For each aligned pair: if find(a) != find(b) and a != b: False

        Complexity: O((n + P) * α(W)) time, O(W) space for W words.
        """
        if len(sentence1) != len(sentence2):
            return False
        parent: Dict[str, str] = {}

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

        for a, b in similarPairs:
            union(a, b)

        for a, b in zip(sentence1, sentence2):
            if a != b and find(a) != find(b):
                return False
        return True
# @lc code=end

