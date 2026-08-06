#
# @lc app=leetcode id=757 lang=python3
#
# [757] Set Intersection Size At Least Two
#
# https://leetcode.com/problems/set-intersection-size-at-least-two/description/
#
# algorithms
# Hard (58.1%)
# Likes:    1133
# Dislikes: 110
# Total Accepted:    99.2K
# Total Submissions: 171K
# Testcase Example:  "[[1,3],[3,7],[8,9]]"
#
# You are given a 2D integer array intervals where intervals[i] = [start_i,
# end_i] represents all the integers from start_i to end_i inclusively.
#
# A containing set is an array nums where each interval from intervals has at
# least two integers in nums.
#
# For example, if intervals = [[1,3], [3,7], [8,9]], then [1,2,4,7,8,9] and
# [2,3,4,8,9] are containing sets.
#
# Return the minimum possible size of a containing set.
#
# Example 1:
#
# Input: intervals = [[1,3],[3,7],[8,9]]
# Output: 5
# Explanation: let nums = [2, 3, 4, 8, 9].
# It can be shown that there cannot be any containing array of size 4.
#
# Example 2:
#
# Input: intervals = [[1,3],[1,4],[2,5],[3,5]]
# Output: 3
# Explanation: let nums = [2, 3, 4].
# It can be shown that there cannot be any containing array of size 2.
#
# Example 3:
#
# Input: intervals = [[1,2],[2,3],[2,4],[4,5]]
# Output: 5
# Explanation: let nums = [1, 2, 3, 4, 5].
# It can be shown that there cannot be any containing array of size 4.
#
# Constraints:
#
# 1 <= intervals.length <= 3000
#
# intervals[i].length == 2
#
# 0 <= start_i < end_i <= 10^8
#


# @lc code=start
from typing import List


class Solution:
    def intersectionSizeTwo(self, intervals: List[List[int]]) -> int:
        """
        Interview explanation:
        Greedy: sort intervals by end ascending (then start descending). Maintain
        the two largest chosen points that cover previous intervals; when an
        interval is not covered enough, add its end (and end-1 if needed).

        Algorithm:
        - Sort by (end, -start)
        - chosen max two points tracked as p1 < p2 (or -1)
        - For each [s,e]: count how many of {p1,p2} lie in [s,e]
          - 0: add e-1 and e; size += 2
          - 1: add e; size += 1
          - 2: nothing

        Complexity: O(n log n) time, O(1) extra space.
        """
        intervals.sort(key=lambda x: (x[1], -x[0]))
        size = 0
        p1 = p2 = -1
        for s, e in intervals:
            cnt = (p1 >= s) + (p2 >= s)
            if cnt == 0:
                size += 2
                p1, p2 = e - 1, e
            elif cnt == 1:
                size += 1
                p1, p2 = p2 if p2 >= s else p1, e
        return size
# @lc code=end

