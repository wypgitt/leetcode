#
# @lc app=leetcode id=3802 lang=python3
#
# [3802] Number of Ways to Paint Sheets
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We have n sheets in a row and m colors. limit[i] is the maximum number of
# sheets color i can paint.
#
# We must paint all sheets using exactly two distinct colors. Each color must
# occupy one contiguous segment.
#
# Therefore every valid painting is determined by:
#   - a split position x, where the first segment has length x and the second
#     segment has length n - x
#   - an ordered pair of distinct colors (i, j)
#
# Conditions:
#   1 <= x <= n - 1
#   x <= limit[i]
#   n - x <= limit[j]
#   i != j
#
# Return the number of valid paintings modulo 1_000_000_007.
#
#
# Direct counting formula for one split
# Fix the split x.
#
# Let:
#   A(x) = number of colors with limit >= x
#   B(x) = number of colors with limit >= n - x
#
# If colors were allowed to be the same, there would be:
#   A(x) * B(x)
# ordered choices.
#
# But the two colors must be distinct. A color is counted as both first and
# second if:
#   limit >= x and limit >= n - x
# which is the same as:
#   limit >= max(x, n - x)
#
# Let:
#   Same(x) = number of colors with limit >= max(x, n - x)
#
# Valid ordered pairs for split x:
#   A(x) * B(x) - Same(x)
#
# Answer:
#   sum over x = 1..n-1 of A(x) * B(x) - Same(x)
#
#
# Challenge
# n can be as large as 1e9, so we cannot iterate every split x.
#
# We need to exploit the fact that A(x), B(x), and Same(x) are step functions
# that change only near values from limit.
#
#
# Sort limits and query counts by binary search
# Sort limit.
#
# Number of colors with limit >= need is:
#   m - lower_bound(limit, need)
#
# This gives A(x), B(x), and Same(x) in O(log m).
#
#
# Piecewise constant intervals
# The expression:
#   A(x) * B(x) - Same(x)
#
# can change only when one of these thresholds changes:
#
#   A(x) changes when x passes a limit value.
#   B(x) = count(limit >= n - x) changes when n - x passes a limit value,
#          i.e. when x passes n - limit.
#   Same(x) uses max(x, n - x), so it can change when x or n - x crosses a
#          limit value.
#
# A simple robust way:
#   collect candidate boundary points:
#      1, n
#      a, a + 1, n - a, n - a + 1 for every limit a
#   keep only points in [1, n - 1]
#   sort them
#
# Between two consecutive boundary points p and q, all relevant counts are
# constant for every x in [p, q - 1].
#
# So we evaluate the contribution once at p and multiply by interval length:
#   q - p
#
# This avoids iterating up to n.
#
#
# Why include both a and a+1?
# For count(limit >= x), the value changes after x moves from a to a+1.
# Including both sides of the jump ensures no interval crosses that change.
#
# Similarly, for n - x thresholds, changes happen around x = n - a, so we add
# n - a and n - a + 1.
#
#
# Data structure choice
# We use:
#   - sorted limit array for binary search,
#   - a set of boundary points to deduplicate,
#   - a sorted list of boundary points for interval scanning.
#
# This is enough because we only need counts of limits above thresholds, not
# updates or range modifications.
#
#
# Walkthrough of the code
# 1. Sort limit.
# 2. Create boundary set with 1 and n.
#    n is used as a sentinel endpoint so the last real interval can end at n-1.
# 3. For every limit a, add:
#      a, a+1, n-a, n-a+1
#    if the point lies in [1, n].
# 4. Sort boundaries.
# 5. For each consecutive pair (left, right):
#      x values are [left, right-1]
#      if left <= n-1:
#          contribution_per_split = count_ge(left) * count_ge(n-left)
#                                   - count_ge(max(left, n-left))
#          add contribution_per_split * (right-left)
# 6. Return modulo MOD.
#
#
# Correctness proof
#
# Lemma 1: For a fixed split x, the number of valid ordered color pairs is
# A(x) * B(x) - Same(x).
# Proof:
# A(x) choices can paint the first segment and B(x) choices can paint the second
# segment. This counts ordered pairs, including pairs where both colors are the
# same. A color can appear in both positions exactly when it can paint both
# segment lengths, i.e. limit >= max(x, n-x). Subtracting Same(x) removes exactly
# those invalid same-color choices.
#
# Lemma 2: The total answer is the sum of the fixed-split count over
# x = 1..n-1.
# Proof:
# Every valid painting has exactly one boundary between the two contiguous
# segments, so it has exactly one split x. For that x, it corresponds to exactly
# one ordered color pair. Conversely, every valid split and ordered color pair
# defines one painting.
#
# Lemma 3: On every scanned interval [left, right-1], the fixed-split count is
# constant.
# Proof:
# The functions count_ge(x), count_ge(n-x), and count_ge(max(x,n-x)) can change
# only when their threshold crosses some limit value. The boundary construction
# inserts both sides of every such crossing: a/a+1 and n-a/n-a+1. Therefore no
# interval between consecutive boundaries crosses a change point.
#
# Theorem: The algorithm returns the number of valid paintings.
# Proof:
# By Lemma 1 and Lemma 2, the desired answer is the sum of the fixed-split count
# over all valid x. By Lemma 3, the algorithm groups x values into intervals on
# which that count is constant, evaluates once per interval, and multiplies by
# the interval length. Thus it computes exactly the same sum.
#
#
# Complexity analysis
#
# Let m = len(limit).
#
# Time:
#   - Sorting limits: O(m log m)
#   - Building O(m) boundary points: O(m)
#   - Sorting boundaries: O(m log m)
#   - Scanning boundaries with O(log m) binary searches each: O(m log m)
#
# Overall time complexity: O(m log m).
#
# Space:
#   - Sorted limits and boundary set/list use O(m).
# Overall space complexity: O(m).
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      n = 4, limit = [3,1,2] -> 6
#
# 2. Example 2:
#      n = 3, limit = [1,2] -> 2
#
# 3. Example 3:
#      n = 3, limit = [2,2] -> 4
#
# 4. No valid painting:
#      n = 10, limit = [1,1] -> 0
#
# 5. Large limits:
#      n = 5, limit = [10,10] -> 8
#      There are 4 splits and 2 ordered color pairs.
#
# 6. Random brute force:
#      For small n and m, iterate all splits and ordered color pairs and compare
#      with the interval algorithm.
#
#
# Edge cases
#
# - limit[i] may exceed n. A color that can paint more than n sheets simply can
#   paint any segment length.
# - n can be 1e9, so never loop over split positions directly.
# - Exactly two distinct colors means subtract same-color choices.
# - Ordered color pairs matter because first segment and second segment are
#   different positions in the row.
#
#
# Possible improvements
#
# - Instead of binary searching for each boundary interval, one could sweep
#   counts with pointers. The binary-search version is simpler and already fast.
# - Inclusion-exclusion by color pairs is possible but would be O(m^2), too slow.
# - Iterating all split lengths is O(n), impossible when n is 1e9.
#
# -------------------------------------------------------------------------------

# @lc code=start
from bisect import bisect_left
from typing import List


class Solution:
    MOD = 1_000_000_007

    def numberOfWays(self, n: int, limit: List[int]) -> int:
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
