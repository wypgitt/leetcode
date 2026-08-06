#
# @lc app=leetcode id=433 lang=python3
#
# [433] Minimum Genetic Mutation
#
# https://leetcode.com/problems/minimum-genetic-mutation/description/
#
# algorithms
# Medium (56.60%)
# Likes:    3325
# Dislikes: 348
# Total Accepted:    281K
# Total Submissions: 496.4K
# Testcase Example:  '"AACCGGTT"\n"AACCGGTA"\n["AACCGGTA"]'
#
# A gene string can be represented by an 8-character long string, with choices
# from 'A', 'C', 'G', and 'T'.
# 
# Suppose we need to investigate a mutation from a gene string startGene to a
# gene string endGene where one mutation is defined as one single character
# changed in the gene string.
# 
# 
# For example, "AACCGGTT" --> "AACCGGTA" is one mutation.
# 
# 
# There is also a gene bank bank that records all the valid gene mutations. A
# gene must be in bank to make it a valid gene string.
# 
# Given the two gene strings startGene and endGene and the gene bank bank,
# return the minimum number of mutations needed to mutate from startGene to
# endGene. If there is no such a mutation, return -1.
# 
# Note that the starting point is assumed to be valid, so it might not be
# included in the bank.
# 
# 
# Example 1:
# 
# 
# Input: startGene = "AACCGGTT", endGene = "AACCGGTA", bank = ["AACCGGTA"]
# Output: 1
# 
# 
# Example 2:
# 
# 
# Input: startGene = "AACCGGTT", endGene = "AAACGGTA", bank =
# ["AACCGGTA","AACCGCTA","AAACGGTA"]
# Output: 2
# 
# 
# 
# Constraints:
# 
# 
# 0 <= bank.length <= 10
# startGene.length == endGene.length == bank[i].length == 8
# startGene, endGene, and bank[i] consist of only the characters ['A', 'C',
# 'G', 'T'].
# 
# 
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def minMutation(self, startGene: str, endGene: str, bank: List[str]) -> int:
        bank_set = set(bank)
        if endGene not in bank_set:
            return -1

        q = deque([(startGene, 0)])
        seen = {startGene}
        choices = 'ACGT'

        while q:
            gene, steps = q.popleft()
            if gene == endGene:
                return steps
            chars = list(gene)
            for i, old in enumerate(chars):
                for ch in choices:
                    if ch == old:
                        continue
                    chars[i] = ch
                    nxt = ''.join(chars)
                    if nxt in bank_set and nxt not in seen:
                        seen.add(nxt)
                        q.append((nxt, steps + 1))
                chars[i] = old
        return -1
# @lc code=end

"""
Interview explanation:
This is an unweighted shortest-path problem where each valid gene string is a node and one-character mutations are edges. BFS is the correct algorithm because every mutation has equal cost, so the first time we reach endGene is the minimum number of mutations.

Data structure: a set gives O(1) membership checks for valid bank genes, and a queue stores the BFS frontier.

Edge cases: if endGene is not in the bank, no valid final mutation exists. The seen set prevents cycles and repeated work.

Complexity: for B bank strings of fixed length L=8, each visited gene tries 4L mutations, so time is O(B * L * 4) and space is O(B).
"""
