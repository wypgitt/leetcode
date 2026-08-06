#
# @lc app=leetcode id=3598 lang=python3
#
# [3598] Longest Common Prefix Between Adjacent Strings After Removals
#
# https://leetcode.com/problems/longest-common-prefix-between-adjacent-strings-after-removals/description/
#
# algorithms
# Medium (32.74%)
# Likes:    88
# Dislikes: 5
# Total Accepted:    19.7K
# Total Submissions: 60K
# Testcase Example:  "[\"jump\",\"run\",\"run\",\"jump\",\"run\"]"
#
#
# You are given an array of strings words. For each index i in the range
# [0, words.length - 1], perform the following steps:
#
# Remove the element at index i from the words array.
#
# Compute the length of the longest common prefix among all adjacent pairs
# in the modified array.
#
# Return an array answer, where answer[i] is the length of the longest
# common prefix between the adjacent pairs after removing the element at
# index i. If no adjacent pairs remain or if none share a common prefix,
# then answer[i] should be 0.
#
# Example 1:
#
# Input: words = ["jump","run","run","jump","run"]
#
# Output: [3,0,0,3,3]
#
# Explanation:
#
# Removing index 0:
#
# words becomes ["run", "run", "jump", "run"]
#
# Longest adjacent pair is ["run", "run"] having a common prefix "run"
# (length 3)
#
# Removing index 1:
#
# words becomes ["jump", "run", "jump", "run"]
#
# No adjacent pairs share a common prefix (length 0)
#
# Removing index 2:
#
# words becomes ["jump", "run", "jump", "run"]
#
# No adjacent pairs share a common prefix (length 0)
#
# Removing index 3:
#
# words becomes ["jump", "run", "run", "run"]
#
# Longest adjacent pair is ["run", "run"] having a common prefix "run"
# (length 3)
#
# Removing index 4:
#
# words becomes ["jump", "run", "run", "jump"]
#
# Longest adjacent pair is ["run", "run"] having a common prefix "run"
# (length 3)
#
# Example 2:
#
# Input: words = ["dog","racer","car"]
#
# Output: [0,0,0]
#
# Explanation:
#
# Removing any index results in an answer of 0.
#
# Constraints:
#
# 1 <= words.length <= 10^5
#
# 1 <= words[i].length <= 10^4
#
# words[i] consists of lowercase English letters.
#
# The sum of words[i].length is smaller than or equal 10^5.
#

# @lc code=start

from typing import List


class Solution:
    def longestCommonPrefix(self, words: List[str]) -> List[int]:
        """
        Interview explanation:
        After deleting index i, the answer is the max LCP among remaining
        adjacent pairs — all old pairs except those touching i, plus the new
        bridge pair (i-1,i+1).

        Algorithm:
        - Precompute lcp[i]=LCP(words[i],words[i+1]).
        - Prefix/suffix maxima of lcp; for each i combine left max, right max,
          and LCP(words[i-1], words[i+1]).

        Complexity: O(n + Σ|words[i]|) time, O(n) space.
        """
        n = len(words)

        def lcp(i: int, j: int) -> int:
            if i < 0 or j >= n:
                return 0
            a, b = words[i], words[j]
            lim = min(len(a), len(b))
            k = 0
            while k < lim and a[k] == b[k]:
                k += 1
            return k

        if n == 1:
            return [0]

        adj = [lcp(i, i + 1) for i in range(n - 1)]
        suf = [0] * (n + 1)
        for i in range(n - 2, -1, -1):
            suf[i] = max(suf[i + 1], adj[i])

        ans = [0] * n
        pref = 0
        for i in range(n):
            if i >= 2:
                pref = max(pref, adj[i - 2])
            ans[i] = max(pref, suf[i + 1], lcp(i - 1, i + 1))
        return ans
# @lc code=end
