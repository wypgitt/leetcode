#
# @lc app=leetcode id=354 lang=python3
#
# [354] Russian Doll Envelopes
#
# https://leetcode.com/problems/russian-doll-envelopes/description/
#
# algorithms
# Hard (38.09%)
# Likes:    6535
# Dislikes: 173
# Total Accepted:    305K
# Total Submissions: 801K
# Testcase Example:  "[[5,4],[6,4],[6,7],[2,3]]"
#
# You are given a 2D array of integers envelopes where envelopes[i] = [w_i,
# h_i] represents the width and the height of an envelope.
#
# One envelope can fit into another if and only if both the width and height of
# one envelope are greater than the other envelope's width and height.
#
# Return the maximum number of envelopes you can Russian doll (i.e., put one
# inside the other).
#
# Note: You cannot rotate an envelope.
#
# Example 1:
#
# Input: envelopes = [[5,4],[6,4],[6,7],[2,3]]
# Output: 3
# Explanation: The maximum number of envelopes you can Russian doll is 3 ([2,3]
# => [5,4] => [6,7]).
#
# Example 2:
#
# Input: envelopes = [[1,1],[1,1],[1,1]]
# Output: 1
#
# Constraints:
#
# 1 <= envelopes.length <= 10^5
#
# envelopes[i].length == 2
#
# 1 <= w_i, h_i <= 10^5
#

# @lc code=start
import bisect
from typing import List


class Solution:
    def maxEnvelopes(self, envelopes: List[List[int]]) -> int:
        """
        Interview explanation:
        Sort by width ascending, height descending (so equal widths cannot
        nest). Then LIS on heights via patience sorting (bisect) — classic
        Russian-doll reduction to 1D LIS.

        Algorithm:
        - Sort key=(w, -h).
        - Maintain increasing tails of heights; bisect_left replace/append.
        - Length of tails is answer.

        Complexity: O(n log n) time, O(n) space.
        """
        envelopes.sort(key=lambda e: (e[0], -e[1]))
        tails: List[int] = []
        for _, h in envelopes:
            i = bisect.bisect_left(tails, h)
            if i == len(tails):
                tails.append(h)
            else:
                tails[i] = h
        return len(tails)
# @lc code=end
