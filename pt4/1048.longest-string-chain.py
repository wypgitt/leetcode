#
# @lc app=leetcode id=1048 lang=python3
#
# [1048] Longest String Chain
#
# https://leetcode.com/problems/longest-string-chain/description/
#
# algorithms
# Medium (62.99%)
# Likes:    7821
# Dislikes: 272
# Total Accepted:    527K
# Total Submissions: 836.5K
# Testcase Example:  '["a","b","ba","bca","bda","bdca"]'
#
# You are given an array of words where each word consists of lowercase English
# letters.
# 
# wordA is a predecessor of wordB if and only if we can insert exactly one
# letter anywhere in wordA without changing the order of the other characters
# to make it equal to wordB.
# 
# 
# For example, "abc" is a predecessor of "abac", while "cba" is not a
# predecessor of "bcad".
# 
# 
# A word chain is a sequence of words [word1, word2, ..., wordk] with k >= 1,
# where word1 is a predecessor of word2, word2 is a predecessor of word3, and
# so on. A single word is trivially a word chain with k == 1.
# 
# Return the length of the longest possible word chain with words chosen from
# the given list of words.
# 
# 
# Example 1:
# 
# 
# Input: words = ["a","b","ba","bca","bda","bdca"]
# Output: 4
# Explanation: One of the longest word chains is ["a","ba","bda","bdca"].
# 
# 
# Example 2:
# 
# 
# Input: words = ["xbc","pcxbcf","xb","cxbc","pcxbc"]
# Output: 5
# Explanation: All the words can be put in a word chain ["xb", "xbc", "cxbc",
# "pcxbc", "pcxbcf"].
# 
# 
# Example 3:
# 
# 
# Input: words = ["abcd","dbqca"]
# Output: 1
# Explanation: The trivial word chain ["abcd"] is one of the longest word
# chains.
# ["abcd","dbqca"] is not a valid word chain because the ordering of the
# letters is changed.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= words.length <= 1000
# 1 <= words[i].length <= 16
# words[i] only consists of lowercase English letters.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def longestStrChain(self, words: List[str]) -> int:
        words.sort(key=len)
        best_chain_ending_at = {}
        answer = 1

        for word in words:
            best = 1
            for i in range(len(word)):
                predecessor = word[:i] + word[i + 1 :]
                best = max(best, best_chain_ending_at.get(predecessor, 0) + 1)

            best_chain_ending_at[word] = best
            answer = max(answer, best)

        return answer
# @lc code=end

"""
Interview Explanation

Core idea:
If wordA is a predecessor of wordB, then wordA can be made by deleting exactly
one character from wordB. Process shorter words first, and each word can look
up all possible predecessors in a dictionary.

Algorithm:
1. Sort words by length.
2. For each word, delete each character once to form candidate predecessors.
3. If a predecessor exists, extend its best chain by one.
4. Store the best chain length ending at the current word.

Data structure choice:
A hash map from word to best chain length gives O(1) average lookup for each
candidate predecessor. Sorting by length guarantees predecessor states are
already computed.

Correctness:
Every valid chain ending at a word must have a previous word formed by deleting
one character from that word. The algorithm tries all such deletions and
extends the best available predecessor chain. Since words are processed from
shorter to longer, all possible predecessor chain lengths are final when used.

Complexity:
Let n be the number of words and L the maximum word length. Sorting is
O(n log n). For each word, we create up to L strings of length O(L), so the DP
work is O(n * L^2). Space is O(n) for the map.

Tests and edge cases:
- No valid predecessor relationships: answer 1.
- Multiple possible predecessors: dictionary max chooses the best chain.
- Same length words cannot be predecessors and are naturally ignored.
- Maximum word length is only 16, so slicing cost is small.
"""
