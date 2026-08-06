#
# @lc app=leetcode id=763 lang=python3
#
# [763] Partition Labels
#
# https://leetcode.com/problems/partition-labels/description/
#
# algorithms
# Medium (81.99%)
# Likes:    11323
# Dislikes: 446
# Total Accepted:    824K
# Total Submissions: 1.0M
# Testcase Example:  "\"ababcbacadefegdehijhklij\""
#
# You are given a string s. We want to partition the string into as many parts
# as possible so that each letter appears in at most one part. For example, the
# string "ababcc" can be partitioned into ["abab", "cc"], but partitions such
# as ["aba", "bcc"] or ["ab", "ab", "cc"] are invalid.
#
# Note that the partition is done so that after concatenating all the parts in
# order, the resultant string should be s.
#
# Return a list of integers representing the size of these parts.
#
# Example 1:
#
# Input: s = "ababcbacadefegdehijhklij"
# Output: [9,7,8]
# Explanation:
# The partition is "ababcbaca", "defegde", "hijhklij".
# This is a partition so that each letter appears in at most one part.
# A partition like "ababcbacadefegde", "hijhklij" is incorrect, because it
# splits s into less parts.
#
# Example 2:
#
# Input: s = "eccbbbbdec"
# Output: [10]
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of lowercase English letters.
#


# @lc code=start
from typing import List


class Solution:
    def partitionLabels(self, s: str) -> List[int]:
        """
        Interview explanation:
        Greedy: each letter's last occurrence bounds how far a partition must
        extend. Grow end to the max last-index of letters seen; when i == end,
        cut a partition.

        Algorithm:
        - last[c] = last index of c
        - start = end = 0; for i,c: end = max(end, last[c]); if i==end: emit

        Complexity: O(n) time, O(1) space (alphabet).
        """
        last = {c: i for i, c in enumerate(s)}
        ans = []
        start = end = 0
        for i, c in enumerate(s):
            end = max(end, last[c])
            if i == end:
                ans.append(end - start + 1)
                start = i + 1
        return ans
# @lc code=end

