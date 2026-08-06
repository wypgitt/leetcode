#
# @lc app=leetcode id=3485 lang=python3
#
# [3485] Longest Common Prefix of K Strings After Removal
#
# https://leetcode.com/problems/longest-common-prefix-of-k-strings-after-removal/description/
#
# algorithms
# Hard (24.42%)
# Likes:    65
# Dislikes: 5
# Total Accepted:    6.9K
# Total Submissions: 28.1K
# Testcase Example:  "[\"jump\",\"run\",\"run\",\"jump\",\"run\"]\n2"
#
#
# You are given an array of strings words and an integer k.
#
# For each index i in the range [0, words.length - 1], find the length of
# the longest common prefix among any k strings (selected at distinct
# indices) from the remaining array after removing the i^th element.
#
# Return an array answer, where answer[i] is the answer for i^th element.
# If removing the i^th element leaves the array with fewer than k strings,
# answer[i] is 0.
#
# Example 1:
#
# Input: words = ["jump","run","run","jump","run"], k = 2
#
# Output: [3,4,4,3,4]
#
# Explanation:
#
# Removing index 0 ("jump"):
#
# words becomes: ["run", "run", "jump", "run"]. "run" occurs 3 times.
# Choosing any two gives the longest common prefix "run" (length 3).
#
# Removing index 1 ("run"):
#
# words becomes: ["jump", "run", "jump", "run"]. "jump" occurs twice.
# Choosing these two gives the longest common prefix "jump" (length 4).
#
# Removing index 2 ("run"):
#
# words becomes: ["jump", "run", "jump", "run"]. "jump" occurs twice.
# Choosing these two gives the longest common prefix "jump" (length 4).
#
# Removing index 3 ("jump"):
#
# words becomes: ["jump", "run", "run", "run"]. "run" occurs 3 times.
# Choosing any two gives the longest common prefix "run" (length 3).
#
# Removing index 4 ("run"):
#
# words becomes: ["jump", "run", "run", "jump"]. "jump" occurs twice.
# Choosing these two gives the longest common prefix "jump" (length 4).
#
# Example 2:
#
# Input: words = ["dog","racer","car"], k = 2
#
# Output: [0,0,0]
#
# Explanation:
#
# Removing any index results in an answer of 0.
#
# Constraints:
#
# 1 <= k <= words.length <= 10^5
#
# 1 <= words[i].length <= 10^4
#
# words[i] consists of lowercase English letters.
#
# The sum of words[i].length is smaller than or equal 10^5.
#

# @lc code=start
from typing import List
from collections import Counter
import heapq


class TrieNode:
    __slots__ = ('children', 'count')

    def __init__(self):
        self.children = {}
        self.count = 0


class Solution:
    def longestCommonPrefix(self, words: List[str], k: int) -> List[int]:
        """
        Interview explanation:
        For each removed index, the answer is the deepest trie depth that still
        has ≥ k strings passing through it.

        Algorithm:
        - Insert all words into a trie; track depths with count ≥ k via a
          Counter + max-heap (lazy deletion).
        - For each word: erase, query max depth, re-insert.

        Complexity: O(Σ|words[i]|) time and space.
        """
        root = TrieNode()
        depth_freq = Counter()
        heap = []  # max-heap of depths via negatives

        def add_depth(d: int) -> None:
            depth_freq[d] += 1
            if depth_freq[d] == 1:
                heapq.heappush(heap, -d)

        def rem_depth(d: int) -> None:
            depth_freq[d] -= 1

        def insert(word: str) -> None:
            node = root
            for i, c in enumerate(word):
                if c not in node.children:
                    node.children[c] = TrieNode()
                node = node.children[c]
                node.count += 1
                if node.count == k:
                    add_depth(i + 1)

        def erase(word: str) -> None:
            node = root
            for i, c in enumerate(word):
                node = node.children[c]
                if node.count == k:
                    rem_depth(i + 1)
                node.count -= 1

        def best() -> int:
            while heap and depth_freq[-heap[0]] == 0:
                heapq.heappop(heap)
            return 0 if not heap else -heap[0]

        for w in words:
            insert(w)

        ans = []
        for w in words:
            erase(w)
            ans.append(best())
            insert(w)
        return ans
# @lc code=end
