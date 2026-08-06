#
# @lc app=leetcode id=3826 lang=python3
#
# [3826] Minimum Partition Score
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given nums and k. Partition nums into exactly k non-empty contiguous
# subarrays.
#
# For a subarray with sum:
#   sumArr
#
# its value is:
#   sumArr * (sumArr + 1) / 2
#
# The score of a partition is the sum of all subarray values. Return the minimum
# possible score.
#
# Example:
#   nums = [5, 1, 2, 1], k = 2
#
# Partition:
#   [5] has sum 5, value 5*6/2 = 15
#   [1,2,1] has sum 4, value 4*5/2 = 10
#   total = 25
#
#
# First simplification
# For a segment with sum S:
#   S * (S + 1) / 2 = (S^2 + S) / 2
#
# Across any partition, the sum of all segment sums is always:
#   total_sum(nums)
#
# Therefore the linear part:
#   sum(S) / 2
# is constant and does not affect which partition is optimal.
#
# So minimizing the original score is equivalent to minimizing:
#   sum(segment_sum^2)
#
# At the end:
#   answer = (minimum_square_sum + total_sum) // 2
#
#
# Prefix sums
# Let:
#   prefix[0] = 0
#   prefix[i] = nums[0] + ... + nums[i-1]
#
# Sum of segment nums[j..i-1] is:
#   prefix[i] - prefix[j]
#
#
# DP definition
# Let:
#   dp[t][i] = minimum sum of squared segment sums when partitioning
#              nums[0..i-1] into exactly t non-empty subarrays
#
# Transition:
#   dp[t][i] = min over j from t-1 to i-1:
#       dp[t-1][j] + (prefix[i] - prefix[j])^2
#
# where j is the start index of the last segment.
#
# Base:
#   dp[0][0] = 0
#   dp[0][i > 0] = impossible
#
# Direct DP would be O(k*n^2), which is too high for n = 1000 in Python.
#
#
# Convex Hull Trick transformation
# Expand the square:
#
#   dp[t-1][j] + (prefix[i] - prefix[j])^2
#
# = dp[t-1][j] + prefix[i]^2 - 2*prefix[i]*prefix[j] + prefix[j]^2
#
# For fixed i, prefix[i]^2 is constant. We need:
#
#   prefix[i]^2 + min over j:
#       (-2*prefix[j]) * prefix[i] + (dp[t-1][j] + prefix[j]^2)
#
# This is a line query:
#   x = prefix[i]
#   slope = -2 * prefix[j]
#   intercept = dp[t-1][j] + prefix[j]^2
#
# For each previous cut j, create one line:
#   y = slope * x + intercept
#
# Query the minimum y at x = prefix[i].
#
#
# Why monotonic CHT applies
# nums[i] >= 1, so prefix sums are strictly increasing.
#
# As j increases:
#   prefix[j] increases
#   slope = -2 * prefix[j] decreases
#
# As i increases:
#   query x = prefix[i] increases
#
# Therefore both line slopes and query points are monotonic. We can maintain a
# deque-like lower hull and answer each query amortized O(1).
#
#
# Hull details
# The hull stores lines in decreasing slope order.
#
# When adding a new line, the previous last line becomes useless if the
# intersection of (line1, line2) is not before the intersection of (line2,
# line3). Algebraically, for lines a, b, c:
#
#   x(a,b) >= x(b,c)
#
# means b is never the best line. We compare this with cross multiplication to
# avoid floating-point precision:
#
#   (b.b - a.b) / (a.m - b.m) >= (c.b - b.b) / (b.m - c.m)
#
# Since slopes are strictly decreasing, denominators are positive.
#
# During query, while the second line gives a value <= the first line at the
# current x, pop/advance the first line. Because query x only increases, a line
# removed from the front will never be useful again.
#
#
# Data structure choice
# We use:
#   - prefix array for O(1) segment sums,
#   - two 1D DP arrays prev and cur,
#   - a list plus head pointer as the monotonic hull.
#
# A full 2D/3D table is unnecessary because layer t only depends on layer t - 1.
# A Li Chao tree would also work, but the monotonic slopes and monotonic queries
# make the deque hull faster and simpler.
#
#
# Walkthrough of the code
# 1. Build prefix sums.
# 2. Initialize prev for t = 0:
#      prev[0] = 0, all other entries impossible.
# 3. For each number of parts t from 1 to k:
#      - create cur filled with infinity.
#      - scan i from t to n.
#      - before computing cur[i], add the candidate cut j = i - 1 from prev.
#        Over the scan this makes all valid cuts j in [t-1, i-1] available.
#      - query the hull at x = prefix[i].
#      - cur[i] = prefix[i]^2 + best_line_value.
# 4. After k layers, prev[n] is the minimum square sum.
# 5. Convert back to the original triangular score:
#      (prev[n] + prefix[n]) // 2
#
#
# Correctness proof
#
# Lemma 1: Minimizing the original partition score is equivalent to minimizing
# the sum of squared segment sums.
# Proof:
# Each segment value is (S^2 + S) / 2. Over any partition, sum(S) equals the
# total array sum, which is constant. Therefore only sum(S^2) affects the choice
# of optimal partition.
#
# Lemma 2: The DP recurrence correctly computes the minimum square sum.
# Proof:
# In any partition of nums[0..i-1] into t subarrays, let j be the start of the
# last subarray. Then nums[0..j-1] must be optimally partitioned into t-1
# subarrays, otherwise we could improve the whole solution. The last subarray
# contributes (prefix[i] - prefix[j])^2. Trying all valid j covers every possible
# last segment.
#
# Lemma 3: Each candidate cut j corresponds exactly to one line in the CHT
# transformation, and querying at x = prefix[i] gives the transition value minus
# prefix[i]^2.
# Proof:
# Expanding the recurrence gives:
#   dp[t-1][j] + prefix[j]^2 - 2*prefix[i]*prefix[j] + prefix[i]^2
# For fixed j, the part depending on prefix[i] is a line with slope
# -2*prefix[j] and intercept dp[t-1][j] + prefix[j]^2. The remaining
# prefix[i]^2 is added after the query.
#
# Lemma 4: The monotonic hull returns the minimum line value for every query.
# Proof:
# Lines are inserted in monotonic slope order and query x values are monotonic.
# The hull deletion rule removes exactly lines whose best interval is empty.
# During queries, if the next line is no worse at the current x, the current line
# will never become better again for any later x, so advancing the head is safe.
#
# Theorem: The algorithm returns the minimum possible partition score.
# Proof:
# By Lemma 2, the DP recurrence gives the optimal square sum. By Lemma 3 and
# Lemma 4, each DP layer is computed exactly by the convex hull. By Lemma 1, the
# final conversion from square sum to triangular score gives the original
# objective.
#
#
# Complexity analysis
#
# Let n = len(nums).
#
# Time:
#   For each of k layers, we scan i once from t to n.
#   Each line is added once and removed from the hull at most once.
#   Each query advances the head at most once amortized.
#   Overall time complexity: O(k*n).
#
# Space:
#   prefix: O(n)
#   prev and cur: O(n)
#   hull: O(n)
#   Overall space complexity: O(n).
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      nums = [5,1,2,1], k = 2 -> 25
#
# 2. k = 1:
#      nums = [1,2,3,4], k = 1 -> total sum 10, value 55
#
# 3. k = n:
#      nums = [1,1,1], k = 3 -> each segment is one element, answer 3
#
# 4. Uneven values:
#      Large values should often be split away to reduce square cost.
#
# 5. Random brute force:
#      For small n, enumerate all cut positions and compare with the optimized
#      DP. This validates the CHT transformation.
#
#
# Edge cases
#
# - k = 1: one segment containing the whole array.
# - k = n: every element is its own segment.
# - nums are positive, so prefix sums are strictly increasing. This is what makes
#   the monotonic CHT valid.
# - The result can be large; Python integers handle it.
#
#
# Possible improvements
#
# - Divide-and-conquer DP optimization also applies because this cost has the
#   required monotonic opt structure, giving O(k*n*log n) or O(k*n) depending on
#   implementation details.
# - The monotonic convex hull is simpler here because the transition expands
#   directly into line queries.
# - A naive O(k*n^2) DP is easier to write but may time out at n = 1000.
#
# -------------------------------------------------------------------------------

# @lc code=start
from typing import List, Tuple


class Solution:
    def minPartitionScore(self, nums: List[int], k: int) -> int:
        n = len(nums)
        prefix = [0] * (n + 1)
        for i, value in enumerate(nums, 1):
            prefix[i] = prefix[i - 1] + value

        inf = 10**60
        prev = [inf] * (n + 1)
        prev[0] = 0

        for parts in range(1, k + 1):
            cur = [inf] * (n + 1)
            hull: List[Tuple[int, int]] = []
            head = 0

            for i in range(parts, n + 1):
                cut = i - 1
                self._add_line(
                    hull,
                    -2 * prefix[cut],
                    prev[cut] + prefix[cut] * prefix[cut],
                )

                x = prefix[i]
                while head + 1 < len(hull) and self._value(hull[head + 1], x) <= self._value(hull[head], x):
                    head += 1

                cur[i] = x * x + self._value(hull[head], x)

            prev = cur

        return (prev[n] + prefix[n]) // 2

    def _add_line(self, hull: List[Tuple[int, int]], slope: int, intercept: int) -> None:
        line = (slope, intercept)
        while len(hull) >= 2 and self._is_bad(hull[-2], hull[-1], line):
            hull.pop()
        hull.append(line)

    def _is_bad(
        self,
        first: Tuple[int, int],
        second: Tuple[int, int],
        third: Tuple[int, int],
    ) -> bool:
        m1, b1 = first
        m2, b2 = second
        m3, b3 = third
        return (b2 - b1) * (m2 - m3) >= (b3 - b2) * (m1 - m2)

    def _value(self, line: Tuple[int, int], x: int) -> int:
        slope, intercept = line
        return slope * x + intercept


# @lc code=end
