#
# @lc app=leetcode id=646 lang=python3
#
# [646] Maximum Length of Pair Chain
#
# https://leetcode.com/problems/maximum-length-of-pair-chain/description/
#
# algorithms
# Medium (62.04%)
# Likes:    4979
# Dislikes: 136
# Total Accepted:    328K
# Total Submissions: 529K
# Testcase Example:  "[[1,2],[2,3],[3,4]]"
#
# You are given an array of n pairs pairs where pairs[i] = [left_i, right_i]
# and left_i < right_i.
#
# A pair p2 = [c, d] follows a pair p1 = [a, b] if b < c. A chain of pairs can
# be formed in this fashion.
#
# Return the length longest chain which can be formed.
#
# You do not need to use up all the given intervals. You can select pairs in
# any order.
#
# Example 1:
#
# Input: pairs = [[1,2],[2,3],[3,4]]
# Output: 2
# Explanation: The longest chain is [1,2] -> [3,4].
#
# Example 2:
#
# Input: pairs = [[1,2],[7,8],[4,5]]
# Output: 3
# Explanation: The longest chain is [1,2] -> [4,5] -> [7,8].
#
# Constraints:
#
# n == pairs.length
#
# 1 <= n <= 1000
#
# -1000 <= left_i < right_i <= 1000
#

# @lc code=start

from typing import List


class Solution:
    def findLongestChain(self, pairs: List[List[int]]) -> int:
        """
        Interview explanation:
        Longest chain where pairs[i][1] < pairs[j][0]. Greedy: sort by end;
        take next pair that starts after previous end (like activity selection).

        Algorithm:
        - Sort by second element.
        - cur_end = -inf; count pairs with start > cur_end; update cur_end.

        Complexity: O(N log N) time, O(1)/sort space.
        """
        pairs.sort(key=lambda p: p[1])
        cur = float("-inf")
        ans = 0
        for a, b in pairs:
            if a > cur:
                ans += 1
                cur = b
        return ans
# @lc code=end
