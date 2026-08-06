#
# @lc app=leetcode id=4007 lang=python3
#
# [4007] Widest Possible Fence
#
# https://leetcode.com/problems/widest-possible-fence/description/
#
# algorithms
# Medium (15.89%)
# Likes:    73
# Dislikes: 15
# Total Accepted:    12.2K
# Total Submissions: 76.6K
# Testcase Example:  "[1,3,2,5,7,5,4,2,1]"
#
#
# You are given an integer array planks, where planks[i] represents the
# height of the i^th wooden plank. Each plank has a width of 1 unit.
#
# You want to build a fence consisting of planks that all have the same
# height.
#
# You may either use a plank as is, or combine exactly two distinct
# original planks into a single plank whose height equals the sum of their
# heights. Each original plank can be used at most once, and not all
# original planks need to be used.
#
# Return the maximum possible width of the fence that can be built.
#
# Example 1:
#
# Input: planks = [1,3,2,5,7,5,4,2,1]
#
# Output: 4
#
# Explanation:
#
# We can have four planks of height 5.
#
# planks[3] = 5
#
# planks[5] = 5
#
# planks[0] + planks[6] = 1 + 4 = 5
#
# planks[1] + planks[2] = 3 + 2 = 5
#
# Hence, the maximum width is 4.
#
# Example 2:
#
# Input: planks = [2,3,7]
#
# Output: 1
#
# Explanation:
#
# It is impossible to form two planks of the same height, even after
# combining two distinct original planks.
#
# Since not all original planks need to be used, we can choose any one
# plank as the fence.
#
# Therefore, the maximum possible width is 1.
#
# Constraints:
#
# 1 <= planks.length <= 1000
#
# 1 <= planks[i] <= 10^9
#

# @lc code=start
from collections import Counter, defaultdict


class Solution:
    def maximumWidth(self, planks: list[int]) -> int:
        """
        Interview explanation:
        All fence planks must share one height H. Each original plank is used
        at most once, either alone (if equal to H) or paired with another
        whose heights sum to H.

        Algorithm:
        - Frequency map of heights.
        - For each possible H: count singles + pairs of H/2 + pairs (x, H-x)
          for x < H-x (value classes are disjoint, so no double-booking).
        - Answer is the max count over H (at least 1).

        Complexity: O(u^2) time for u distinct heights (≤ n ≤ 1000), O(u) space.
        """
        cnt = Counter(planks)
        t: dict[int, int] = defaultdict(int)
        for x, v1 in cnt.items():
            t[x] += v1
            t[x * 2] += v1 // 2
            for y, v2 in cnt.items():
                if y > x:
                    t[x + y] += min(v1, v2)
        return max(t.values())
# @lc code=end
