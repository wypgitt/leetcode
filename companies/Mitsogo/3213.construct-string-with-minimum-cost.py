#
# @lc app=leetcode id=3213 lang=python3
#
# [3213] Construct String with Minimum Cost
#
# https://leetcode.com/problems/construct-string-with-minimum-cost/description/
#
# algorithms
# Hard (19.02%)
# Likes:    174
# Dislikes: 32
# Total Accepted:    13.5K
# Total Submissions: 70.8K
# Testcase Example:  "\"abcdef\"\n[\"abdef\",\"abc\",\"d\",\"def\",\"ef\"]\n[100,1,1,10,5]"
#
#
# You are given a string target, an array of strings words, and an integer
# array costs, both arrays of the same length.
#
# Imagine an empty string s.
#
# You can perform the following operation any number of times (including
# zero):
#
# Choose an index i in the range [0, words.length - 1].
#
# Append words[i] to s.
#
# The cost of operation is costs[i].
#
# Return the minimum cost to make s equal to target. If it's not possible,
# return -1.
#
# Example 1:
#
# Input: target = "abcdef", words = ["abdef","abc","d","def","ef"], costs
# = [100,1,1,10,5]
#
# Output: 7
#
# Explanation:
#
# The minimum cost can be achieved by performing the following operations:
#
# Select index 1 and append "abc" to s at a cost of 1, resulting in s =
# "abc".
#
# Select index 2 and append "d" to s at a cost of 1, resulting in s =
# "abcd".
#
# Select index 4 and append "ef" to s at a cost of 5, resulting in s =
# "abcdef".
#
# Example 2:
#
# Input: target = "aaaa", words = ["z","zz","zzz"], costs = [1,10,100]
#
# Output: -1
#
# Explanation:
#
# It is impossible to make s equal to target, so we return -1.
#
# Constraints:
#
# 1 <= target.length <= 5 * 10^4
#
# 1 <= words.length == costs.length <= 5 * 10^4
#
# 1 <= words[i].length <= target.length
#
# The total sum of words[i].length is less than or equal to 5 * 10^4.
#
# target and words[i] consist only of lowercase English letters.
#
# 1 <= costs[i] <= 10^4
#

# @lc code=start
from typing import Dict, List


class Solution:
    def minimumCost(self, target: str, words: List[str], costs: List[int]) -> int:
        """
        Interview explanation:
        Form target by concatenating given words; each word has a cost. Classic
        string DP with a trie of words (min cost per unique word).

        Algorithm:
        - Keep minimum cost for each distinct word; insert into a trie storing
          end-of-word min cost.
        - dp[i] = min cost to build target[:i]; from each i with finite dp[i],
          walk the trie along target[i..] and relax dp at word ends.

        Complexity: O(n * L + sum(|words|)) time where L is max match length,
        O(sum(|words|)+n) space.
        """
        best: Dict[str, int] = {}
        for w, c in zip(words, costs):
            if w not in best or c < best[w]:
                best[w] = c

        class Node:
            __slots__ = ("ch", "cost")

            def __init__(self) -> None:
                self.ch: Dict[str, "Node"] = {}
                self.cost = 10**18

        root = Node()
        for w, c in best.items():
            node = root
            for ch in w:
                if ch not in node.ch:
                    node.ch[ch] = Node()
                node = node.ch[ch]
            node.cost = min(node.cost, c)

        n = len(target)
        INF = 10**18
        dp = [INF] * (n + 1)
        dp[0] = 0
        for i in range(n):
            if dp[i] >= INF:
                continue
            node = root
            for j in range(i, n):
                ch = target[j]
                if ch not in node.ch:
                    break
                node = node.ch[ch]
                if node.cost < INF:
                    dp[j + 1] = min(dp[j + 1], dp[i] + node.cost)
        return -1 if dp[n] >= INF else dp[n]
# @lc code=end
