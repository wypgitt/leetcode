#
# @lc app=leetcode id=3435 lang=python3
#
# [3435] Frequencies of Shortest Supersequences
#
# https://leetcode.com/problems/frequencies-of-shortest-supersequences/description/
#
# algorithms
# Hard (23.00%)
# Likes:    30
# Dislikes: 8
# Total Accepted:    3.1K
# Total Submissions: 13.7K
# Testcase Example:  "[\"ab\",\"ba\"]"
#
#
# You are given an array of strings words. Find all shortest common
# supersequences (SCS) of words that are not permutations of each other.
#
# A shortest common supersequence is a string of minimum length that
# contains each string in words as a subsequence.
#
# Return a 2D array of integers freqs that represent all the SCSs. Each
# freqs[i] is an array of size 26, representing the frequency of each
# letter in the lowercase English alphabet for a single SCS. You may
# return the frequency arrays in any order.
#
# Example 1:
#
# Input: words = ["ab","ba"]
#
# Output:
# [[1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
#
# Explanation:
#
# The two SCSs are "aba" and "bab". The output is the letter frequencies
# for each one.
#
# Example 2:
#
# Input: words = ["aa","ac"]
#
# Output: [[2,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
#
# Explanation:
#
# The two SCSs are "aac" and "aca". Since they are permutations of each
# other, keep only "aac".
#
# Example 3:
#
# Input: words = ["aa","bb","cc"]
#
# Output: [[2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
#
# Explanation:
#
# "aabbcc" and all its permutations are SCSs.
#
# Constraints:
#
# 1 <= words.length <= 256
#
# words[i].length == 2
#
# All strings in words will altogether be composed of no more than 16
# unique lowercase letters.
#
# All strings in words are unique.
#

# @lc code=start
from typing import List


class Solution:
    def supersequences(self, words: List[str]) -> List[List[int]]:
        """
        Interview explanation:
        Each word is a length-2 ordering constraint a->b. An SCS uses each letter
        once or twice; doubling letters breaks cycles. Enumerate which letters are
        doubled and accept masks that admit a topological consumption of all copies.

        Algorithm:
        - Map used letters to 0..k-1 (k<=16); build digraph from words.
        - For each mask of doubled letters, try greedy topo: nodes with indegree 0
          or remaining count 2 can start; consume edges until all counts zero.
        - Keep frequency vectors of minimal total length.

        Complexity: O(2^k * (k+|E|)) time, O(k+|E|) space.
        """
        def idx(ch: str) -> int:
            x = ord(ch) - ord("a")
            if char_to_int[x] == -1:
                int_to_char[len(indegree)] = x
                char_to_int[x] = len(indegree)
                indegree.append(0)
            return char_to_int[x]

        def topological_ok(cnt: List[int]) -> None:
            total = sum(cnt)
            if total > best[0]:
                return
            rem = cnt[:]
            deg = indegree[:]
            seen = [False] * len(cnt)
            q: List[int] = []
            for u in range(len(indegree)):
                if deg[u] == 0 or rem[u] == 2:
                    rem[u] -= 1
                    seen[u] = True
                    q.append(u)
            while q:
                nq: List[int] = []
                for u in q:
                    for v in adj[u]:
                        deg[v] -= 1
                        if deg[v]:
                            continue
                        rem[v] -= 1
                        if seen[v]:
                            continue
                        seen[v] = True
                        nq.append(v)
                q = nq
            if any(rem):
                return
            if total < best[0]:
                best[0] = total
                best[1].clear()
            best[1].append(cnt)

        adj: List[List[int]] = [[] for _ in range(26)]
        char_to_int = [-1] * 26
        int_to_char = [0] * 26
        indegree: List[int] = []
        for w in words:
            adj[idx(w[0])].append(idx(w[1]))
            indegree[idx(w[1])] += 1

        best: list = [float("inf"), []]
        k = len(indegree)
        for mask in range(1 << k):
            topological_ok([2 if mask & (1 << i) else 1 for i in range(k)])

        result: List[List[int]] = []
        for cnt in best[1]:
            freq = [0] * 26
            for i, c in enumerate(cnt):
                freq[int_to_char[i]] = c
            result.append(freq)
        return result
# @lc code=end
