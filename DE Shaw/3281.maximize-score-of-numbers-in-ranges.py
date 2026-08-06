#
# @lc app=leetcode id=3281 lang=python3
#
# [3281] Maximize Score of Numbers in Ranges
#
# https://leetcode.com/problems/maximize-score-of-numbers-in-ranges/description/
#
# algorithms
# Medium (35.99%)
# Likes:    229
# Dislikes: 50
# Total Accepted:    24.5K
# Total Submissions: 68.2K
# Testcase Example:  "[6,0,3]\n2"
#
#
# You are given an array of integers start and an integer d, representing
# n intervals [start[i], start[i] + d].
#
# You are asked to choose n integers where the i^th integer must belong to
# the i^th interval. The score of the chosen integers is defined as the
# minimum absolute difference between any two integers that have been
# chosen.
#
# Return the maximum possible score of the chosen integers.
#
# Example 1:
#
# Input: start = [6,0,3], d = 2
#
# Output: 4
#
# Explanation:
#
# The maximum possible score can be obtained by choosing integers: 8, 0,
# and 4. The score of these chosen integers is min(|8 - 0|, |8 - 4|, |0 -
# 4|) which equals 4.
#
# Example 2:
#
# Input: start = [2,6,13,13], d = 5
#
# Output: 5
#
# Explanation:
#
# The maximum possible score can be obtained by choosing integers: 2, 7,
# 13, and 18. The score of these chosen integers is min(|2 - 7|, |2 - 13|,
# |2 - 18|, |7 - 13|, |7 - 18|, |13 - 18|) which equals 5.
#
# Constraints:
#
# 2 <= start.length <= 10^5
#
# 0 <= start[i] <= 10^9
#
# 0 <= d <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maxPossibleScore(self, start: List[int], d: int) -> int:
        """
        Interview explanation:
        Choose one integer from each interval [start[i], start[i]+d] to maximize
        the minimum pairwise gap. Gaps are monotone in a candidate score.

        Algorithm:
        - Sort starts; binary-search the score.
        - Greedily place the next value at max(start[i], prev+score) if <= start[i]+d.
        - Alternate: same check with an explicit leftmost placement sweep.

        Complexity: O(n log n + n log D) time, O(n) space.
        """
        start = sorted(start)
        n = len(start)

        def ok(score: int) -> bool:
            prev = start[0]
            for i in range(1, n):
                nxt = max(start[i], prev + score)
                if nxt > start[i] + d:
                    return False
                prev = nxt
            return True

        lo, hi = 0, start[-1] + d - start[0]
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if ok(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
