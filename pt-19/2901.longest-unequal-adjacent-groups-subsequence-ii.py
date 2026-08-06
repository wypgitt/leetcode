#
# @lc app=leetcode id=2901 lang=python3
#
# [2901] Longest Unequal Adjacent Groups Subsequence II
#
# https://leetcode.com/problems/longest-unequal-adjacent-groups-subsequence-ii/description/
#
# algorithms
# Medium (51.31%)
# Likes:    579
# Dislikes: 169
# Total Accepted:    84.2K
# Total Submissions: 164.1K
# Testcase Example:  "[\"bab\",\"dab\",\"cab\"]\n[1,2,2]"
#
#
# You are given a string array words, and an array groups, both arrays
# having length n.
#
# The hamming distance between two strings of equal length is the number
# of positions at which the corresponding characters are different.
#
# You need to select the longest subsequence from an array of indices [0,
# 1, ..., n - 1], such that for the subsequence denoted as [i_0, i_1, ...,
# i_k-1] having length k, the following holds:
#
# For adjacent indices in the subsequence, their corresponding groups are
# unequal, i.e., groups[i_j] != groups[i_j+1], for each j where 0 < j + 1
# < k.
#
# words[i_j] and words[i_j+1] are equal in length, and the hamming
# distance between them is 1, where 0 < j + 1 < k, for all indices in the
# subsequence.
#
# Return a string array containing the words corresponding to the indices
# (in order) in the selected subsequence. If there are multiple answers,
# return any of them.
#
# Note: strings in words may be unequal in length.
#
# Example 1:
#
# Input: words = ["bab","dab","cab"], groups = [1,2,2]
#
# Output: ["bab","cab"]
#
# Explanation: A subsequence that can be selected is [0,2].
#
# groups[0] != groups[2]
#
# words[0].length == words[2].length, and the hamming distance between
# them is 1.
#
# So, a valid answer is [words[0],words[2]] = ["bab","cab"].
#
# Another subsequence that can be selected is [0,1].
#
# groups[0] != groups[1]
#
# words[0].length == words[1].length, and the hamming distance between
# them is 1.
#
# So, another valid answer is [words[0],words[1]] = ["bab","dab"].
#
# It can be shown that the length of the longest subsequence of indices
# that satisfies the conditions is 2.
#
# Example 2:
#
# Input: words = ["a","b","c","d"], groups = [1,2,3,4]
#
# Output: ["a","b","c","d"]
#
# Explanation: We can select the subsequence [0,1,2,3].
#
# It satisfies both conditions.
#
# Hence, the answer is [words[0],words[1],words[2],words[3]] =
# ["a","b","c","d"].
#
# It has the longest length among all subsequences of indices that satisfy
# the conditions.
#
# Hence, it is the only answer.
#
# Constraints:
#
# 1 <= n == words.length == groups.length <= 1000
#
# 1 <= words[i].length <= 10
#
# 1 <= groups[i] <= n
#
# words consists of distinct strings.
#
# words[i] consists of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def getWordsInLongestSubsequence(
        self, words: List[str], groups: List[int]
    ) -> List[str]:
        """
        Interview explanation:
        Longest subsequence where adjacent groups differ, words same length,
        and Hamming distance exactly 1.

        Algorithm:
        - O(n^2) DP: dp[i] = best length ending at i; prev[i] predecessor.
          Transition from j < i when groups differ, equal length, Hamming 1.
        - Reconstruct from the best end index.

        Complexity: O(n^2 * L) time (L <= 10), O(n) space.
        """
        n = len(words)
        dp = [1] * n
        prev = [-1] * n
        best = 0

        def hamming1(a: str, b: str) -> bool:
            if len(a) != len(b):
                return False
            diff = 0
            for x, y in zip(a, b):
                if x != y:
                    diff += 1
                    if diff > 1:
                        return False
            return diff == 1

        for i in range(n):
            for j in range(i):
                if (
                    groups[i] != groups[j]
                    and hamming1(words[i], words[j])
                    and dp[j] + 1 > dp[i]
                ):
                    dp[i] = dp[j] + 1
                    prev[i] = j
            if dp[i] > dp[best]:
                best = i

        path = []
        i = best
        while i != -1:
            path.append(words[i])
            i = prev[i]
        path.reverse()
        return path
# @lc code=end
