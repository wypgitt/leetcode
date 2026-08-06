#
# @lc app=leetcode id=3802 lang=python3
#
# [3802] Number of Ways to Paint Sheets
#
# https://leetcode.com/problems/number-of-ways-to-paint-sheets/description/
#
# algorithms
# Hard (67.29%)
# Likes:    4
# Dislikes: 2
# Total Accepted:    467
# Total Submissions: 694
# Testcase Example:  "4\n[3,1,2]"
#
#
# You are given an integer n representing the number of sheets.
#
# You are also given an integer array limit of size m, where limit[i] is
# the maximum number of sheets that can be painted using color i.
#
# You must paint all n sheets under the following conditions:
#
# Exactly two distinct colors are used.
#
# Each color must cover a single contiguous segment of sheets.
#
# The number of sheets painted with color i cannot exceed limit[i].
#
# Return an integer denoting the number of distinct ways to paint all
# sheets. Since the answer may be large, return it modulo 10^9 + 7.
#
# Note: Two ways differ if at least one sheet is painted with a different
# color.
#
# Example 1:
#
# Input: n = 4, limit = [3,1,2]
#
# Output: 6
#
# Explanation:​​​​​​​
#
# For each ordered pair (i, j), where color i is used for the first
# segment and color j for the second segment (i != j), a split of x and 4
# - x is valid if 1 <= x <= limit[i] and 1 <= 4 - x <= limit[j].
#
# Valid pairs and counts are:
#
# (0, 1): x = 3
#
# (0, 2): x = 2, 3
#
# (1, 0): x = 1
#
# (2, 0): x = 1, 2
#
# Therefore, there are 6 valid ways in total.
#
# Example 2:
#
# Input: n = 3, limit = [1,2]
#
# Output: 2
#
# Explanation:
#
# For each ordered pair (i, j), where color i is used for the first
# segment and color j for the second segment (i != j), a split of x and 3
# - x is valid if 1 <= x <= limit[i] and 1 <= 3 - x <= limit[j].
#
# Valid pairs and counts are:
#
# (0, 1): x = 1
#
# (1, 0): x = 2
#
# Hence, there are 2 valid ways in total.
#
# Example 3:
#
# Input: n = 3, limit = [2,2]
#
# Output: 4
#
# Explanation:
#
# For each ordered pair (i, j), where color i is used for the first
# segment and color j for the second segment (i != j), a split of x and 3
# - x is valid if 1 <= x <= limit[i] and 1 <= 3 - x <= limit[j].
#
# Valid pairs and counts are:
#
# (0, 1): x = 1, 2
#
# (1, 0): x = 1, 2
#
# Therefore, there are 4 valid ways in total.
#
# Constraints:
#
# 2 <= n <= 10^9
#
# 2 <= m == limit.length <= 10^5
#
# 1 <= limit[i] <= 10^9
#

# @lc code=start
from bisect import bisect_left
from typing import List


class Solution:
    MOD = 1_000_000_007

    def numberOfWays(self, n: int, limit: List[int]) -> int:
        """
        Interview explanation:
        Paint n sheets with exactly two colors in two contiguous segments.
        Count ordered color pairs and valid split lengths, modulo 10^9+7.

        Algorithm:
        - Sort limits; critical split points come from each limit[i] and n-limit[i].
        - Sweep contiguous ranges of the same (first, second) eligibility counts.
        - For split length x, ways = (#colors >= x) * (#colors >= n-x) - (# both).
        - Multiply by the length of each constant-eligibility range.

        Complexity: O(m log m) time, O(m) space.
        """
        limits = sorted(limit)
        m = len(limits)

        boundaries = {1, n}
        for value in limits:
            for point in (value, value + 1, n - value, n - value + 1):
                if 1 <= point <= n:
                    boundaries.add(point)

        points = sorted(boundaries)
        answer = 0

        for left, right in zip(points, points[1:]):
            if left > n - 1:
                break

            length = min(right, n) - left
            if length <= 0:
                continue

            first_choices = self._count_at_least(limits, left, m)
            second_choices = self._count_at_least(limits, n - left, m)
            same_color = self._count_at_least(limits, max(left, n - left), m)

            per_split = first_choices * second_choices - same_color
            answer = (answer + per_split * length) % self.MOD

        return answer

    def _count_at_least(self, limits: List[int], need: int, size: int) -> int:
        return size - bisect_left(limits, need)
# @lc code=end
