#
# @lc app=leetcode id=3414 lang=python3
#
# [3414] Maximum Score of Non-overlapping Intervals
#
# https://leetcode.com/problems/maximum-score-of-non-overlapping-intervals/description/
#
# algorithms
# Hard (30.83%)
# Likes:    56
# Dislikes: 7
# Total Accepted:    4.7K
# Total Submissions: 15.1K
# Testcase Example:  "[[1,3,2],[4,5,2],[1,5,5],[6,9,3],[6,7,1],[8,9,1]]"
#
#
# You are given a 2D integer array intervals, where intervals[i] = [l_i,
# r_i, weight_i]. Interval i starts at position l_i and ends at r_i, and
# has a weight of weight_i. You can choose up to 4 non-overlapping
# intervals. The score of the chosen intervals is defined as the total sum
# of their weights.
#
# Return the lexicographically smallest array of at most 4 indices from
# intervals with maximum score, representing your choice of
# non-overlapping intervals.
#
# Two intervals are said to be non-overlapping if they do not share any
# points. In particular, intervals sharing a left or right boundary are
# considered overlapping.
#
# Example 1:
#
# Input: intervals = [[1,3,2],[4,5,2],[1,5,5],[6,9,3],[6,7,1],[8,9,1]]
#
# Output: [2,3]
#
# Explanation:
#
# You can choose the intervals with indices 2, and 3 with respective
# weights of 5, and 3.
#
# Example 2:
#
# Input: intervals =
# [[5,8,1],[6,7,7],[4,7,3],[9,10,6],[7,8,2],[11,14,3],[3,5,5]]
#
# Output: [1,3,5,6]
#
# Explanation:
#
# You can choose the intervals with indices 1, 3, 5, and 6 with respective
# weights of 7, 6, 3, and 5.
#
# Constraints:
#
# 1 <= intevals.length <= 5 * 10^4
#
# intervals[i].length == 3
#
# intervals[i] = [l_i, r_i, weight_i]
#
# 1 <= l_i <= r_i <= 10^9
#
# 1 <= weight_i <= 10^9
#

# @lc code=start
import bisect
import math
from functools import lru_cache
from typing import List, Tuple


class Solution:
    def maximumWeight(self, intervals: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Choose up to 4 non-overlapping intervals (touching counts as
        overlap) maximizing total weight; break ties by lexicographically
        smallest index list.

        Algorithm:
        - Sort by left endpoint with original indices.
        - DP(i, quota): skip intervals[i], or take it and jump to first
          interval starting after its right (bisect).
        - Compare (weight, index-tuple) for best.

        Complexity: O(n log n + n*4) with memo; O(n) space.
        """
        arr = sorted((*interval, i) for i, interval in enumerate(intervals))
        n = len(arr)

        @lru_cache(None)
        def dp(i: int, quota: int) -> Tuple[int, Tuple[int, ...]]:
            if i == n or quota == 0:
                return (0, ())
            skip_w, skip_sel = dp(i + 1, quota)
            _, r, weight, original_index = arr[i]
            j = bisect.bisect_right(arr, (r, math.inf))
            next_w, next_sel = dp(j, quota - 1)
            pick_sel = tuple(sorted((original_index,) + next_sel))
            pick_w = weight + next_w
            if pick_w > skip_w or (pick_w == skip_w and pick_sel < skip_sel):
                return (pick_w, pick_sel)
            return (skip_w, skip_sel)

        return list(dp(0, 4)[1])
# @lc code=end
