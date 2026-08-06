#
# @lc app=leetcode id=3253 lang=python3
#
# [3253] Construct String with Minimum Cost (Easy)
#
# https://leetcode.com/problems/construct-string-with-minimum-cost-easy/description/
#
# algorithms
# Medium (58.75%)
# Likes:    11
# Dislikes: 2
# Total Accepted:    856
# Total Submissions: 1.5K
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
# 1 <= target.length <= 2000
#
# 1 <= words.length == costs.length <= 50
#
# 1 <= words[i].length <= target.length
#
# target and words[i] consist only of lowercase English letters.
#
# 1 <= costs[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minimumCost(self, target: str, words: List[str], costs: List[int]) -> int:
        """
        Interview explanation:
        Classic string construction DP: dp[i] = min cost to build target[:i].
        Try appending each word at every reachable prefix.

        Algorithm:
        - Keep min cost per identical word; dp[0]=0, INF elsewhere.
        - For each i with finite dp[i], for each word matching target[i:],
          relax dp[i+len].

        Complexity: O(|target| * sum(|words[i]|)) time, O(|target|) space.
        """
        n = len(target)
        best = {}
        for w, c in zip(words, costs):
            if w not in best or c < best[w]:
                best[w] = c
        items = list(best.items())

        INF = 10**18
        dp = [INF] * (n + 1)
        dp[0] = 0
        for i in range(n):
            if dp[i] >= INF:
                continue
            for w, c in items:
                L = len(w)
                if i + L <= n and target.startswith(w, i):
                    dp[i + L] = min(dp[i + L], dp[i] + c)
        return -1 if dp[n] >= INF else dp[n]
# @lc code=end
