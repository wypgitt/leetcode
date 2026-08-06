#
# @lc app=leetcode id=956 lang=python3
#
# [956] Tallest Billboard
#
# https://leetcode.com/problems/tallest-billboard/description/
#
# algorithms
# Hard (51.86%)
# Likes:    2506
# Dislikes: 64
# Total Accepted:    73.7K
# Total Submissions: 142K
# Testcase Example:  "[1,2,3,6]"
#
# You are installing a billboard and want it to have the largest height. The
# billboard will have two steel supports, one on each side. Each steel support
# must be an equal height.
#
# You are given a collection of rods that can be welded together. For example,
# if you have rods of lengths 1, 2, and 3, you can weld them together to make a
# support of length 6.
#
# Return the largest possible height of your billboard installation. If you
# cannot support the billboard, return 0.
#
# Example 1:
#
# Input: rods = [1,2,3,6]
# Output: 6
# Explanation: We have two disjoint subsets {1,2,3} and {6}, which have the
# same sum = 6.
#
# Example 2:
#
# Input: rods = [1,2,3,4,5,6]
# Output: 10
# Explanation: We have two disjoint subsets {2,3,5} and {4,6}, which have the
# same sum = 10.
#
# Example 3:
#
# Input: rods = [1,2]
# Output: 0
# Explanation: The billboard cannot be supported, so we return 0.
#
# Constraints:
#
# 1 <= rods.length <= 20
#
# 1 <= rods[i] <= 1000
#
# sum(rods[i]) <= 5000
#

# @lc code=start
from typing import Dict, List


class Solution:
    def tallestBillboard(self, rods: List[int]) -> int:
        """
        Interview explanation:
        Split rods into left/right stands (diff = L-R, height = min(L,R) goal
        is max L when L==R). DP on difference: dp[d] = max common height
        achievable with difference d (left-right). For each rod, add to left,
        add to right, or discard — update map of diffs.

        Algorithm (DP on difference):
        - dp = {0: 0}  # diff -> max height of the shorter? actually max sum of
          the taller side's paired common? Standard: dp[d] = max left height
          among states with left-right = d (right height = left-d).
        - Actually classic: dp[diff] = max score (sum of rods used on both
          stands that contribute to equal part). Simpler formulation:
          dp[d] = largest possible sum of the left stand for difference d.
        - For each rod x, for each (d,y) in old dp:
            # add to taller/left: nd=d+x, left becomes y+x
            # add to right: nd=d-x, ...
        - Return dp[0]

        Complexity: O(n * S) time/space, S = sum(rods).
        """
        # dp[diff] = max height of the left stand achieving this left-right diff
        dp: Dict[int, int] = {0: 0}
        for r in rods:
            cur = dict(dp)
            for d, left in cur.items():
                # place on left
                nd = d + r
                dp[nd] = max(dp.get(nd, 0), left + r)
                # place on right
                nd = d - r
                dp[nd] = max(dp.get(nd, 0), left)
        return dp.get(0, 0)
# @lc code=end

