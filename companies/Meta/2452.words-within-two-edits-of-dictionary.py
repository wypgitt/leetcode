#
# @lc app=leetcode id=2452 lang=python3
#
# [2452] Words Within Two Edits of Dictionary
#
# https://leetcode.com/problems/words-within-two-edits-of-dictionary/description/
#
# algorithms
# Medium (73.23%)
# Likes:    585
# Dislikes: 43
# Total Accepted:    124.8K
# Total Submissions: 170.4K
# Testcase Example:  "[\"word\",\"note\",\"ants\",\"wood\"]\n[\"wood\",\"joke\",\"moat\"]"
#
# You are given two string arrays, queries and dictionary. All words in each
# array comprise of lowercase English letters and have the same length.
#
# In one edit you can take a word from queries, and change any letter in it to
# any other letter. Find all words from queries that, after a maximum of two
# edits, equal some word from dictionary.
#
# Return a list of all words from queries, that match with some word from
# dictionary after a maximum of two edits. Return the words in the same order
# they appear in queries.
#
#
#
# Example 1:
#
# Input: queries = ["word","note","ants","wood"], dictionary =
# ["wood","joke","moat"]
# Output: ["word","note","wood"]
# Explanation:
# - Changing the 'r' in "word" to 'o' allows it to equal the dictionary word
# "wood".
# - Changing the 'n' to 'j' and the 't' to 'k' in "note" changes it to "joke".
# - It would take more than 2 edits for "ants" to equal a dictionary word.
# - "wood" can remain unchanged (0 edits) and match the corresponding dictionary
# word.
# Thus, we return ["word","note","wood"].
#
# Example 2:
#
# Input: queries = ["yes"], dictionary = ["not"]
# Output: []
# Explanation:
# Applying any two edits to "yes" cannot make it equal to "not". Thus, we return
# an empty array.
#
#
#
# Constraints:
#
#
# 1 <= queries.length, dictionary.length <= 100
#
#
# n == queries[i].length == dictionary[j].length
#
#
# 1 <= n <= 100
#
#
# All queries[i] and dictionary[j] are composed of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def twoEditWords(self, queries: List[str], dictionary: List[str]) -> List[str]:
        """
        Interview explanation:
        Return queries that can match some dictionary word with at most two
        character edits (substitutions).

        Algorithm:
        - For each query, check Hamming distance <= 2 against any dict word.

        Complexity: O(Q * D * L) time, O(1) extra space.
        """
        ans = []
        for q in queries:
            for d in dictionary:
                if sum(a != b for a, b in zip(q, d)) <= 2:
                    ans.append(q)
                    break
        return ans
# @lc code=end

