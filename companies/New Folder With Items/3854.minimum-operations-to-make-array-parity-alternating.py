#
# @lc app=leetcode id=3854 lang=python3
#
# [3854] Minimum Operations to Make Array Parity Alternating
#
# https://leetcode.com/problems/minimum-operations-to-make-array-parity-alternating/description/
#
# algorithms
# Medium (16.95%)
# Likes:    83
# Dislikes: 13
# Total Accepted:    8.2K
# Total Submissions: 48.2K
# Testcase Example:  '[-2,-3,1,4]'
#
# You are given an integer array nums.
# 
# An array is called parity alternating if for every index i where 0 <= i < n -
# 1, nums[i] and nums[i + 1] have different parity (one is even and the other
# is odd).
# 
# In one operation, you may choose any index i and either increase nums[i] by 1
# or decrease nums[i] by 1.
# 
# Return an integer array answer of length 2 where:
# 
# 
# answer[0] is the minimum number of operations required to make the array
# parity alternating.
# answer[1] is the minimum possible value of max(nums) - min(nums) taken over
# all arrays that are parity alternating and can be obtained by performing
# exactly answer[0] operations.
# 
# 
# An array of length 1 is considered parity alternating.
# 
# 
# Example 1:
# 
# 
# Input: nums = [-2,-3,1,4]
# 
# Output: [2,6]
# 
# Explanation:
# 
# Applying the following operations:
# 
# 
# Increase nums[2] by 1, resulting in nums = [-2, -3, 2, 4].
# Decrease nums[3] by 1, resulting in nums = [-2, -3, 2, 3].
# 
# 
# The resulting array is parity alternating, and the value of max(nums) -
# min(nums) = 3 - (-3) = 6 is the minimum possible among all parity alternating
# arrays obtainable using exactly 2 operations.
# 
# 
# Example 2:
# 
# 
# Input: nums = [0,2,-2]
# 
# Output: [1,3]
# 
# Explanation:
# 
# Applying the following operation:
# 
# 
# Decrease nums[1] by 1, resulting in nums = [0, 1, -2].
# 
# 
# The resulting array is parity alternating, and the value of max(nums) -
# min(nums) = 1 - (-2) = 3 is the minimum possible among all parity alternating
# arrays obtainable using exactly 1 operation.
# 
# 
# Example 3:
# 
# 
# Input: nums = [7]
# 
# Output: [0,0]
# 
# Explanation:
# 
# No operations are required. The array is already parity alternating, and the
# value of max(nums) - min(nums) = 7 - 7 = 0, which is the minimum
# possible.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10^5
# -10^9 <= nums[i] <= 10^9
# 
# 
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def makeParityAlternating(self, nums: List[int]) -> List[int]:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given an integer array `nums`.

        The array is parity alternating if every adjacent pair has different
        parity:

            even, odd, even, odd, ...

        or:

            odd, even, odd, even, ...

        In one operation, we choose one index and either add 1 or subtract 1.
        Adding or subtracting 1 always flips the parity of that element.

        We must return:

            [minimum_operations, minimum_possible_range]

        where:

        * `minimum_operations` is the fewest operations needed to make the array
          parity alternating.
        * `minimum_possible_range` is the minimum possible value of
          `max(nums) - min(nums)` among arrays reachable using exactly
          `minimum_operations` operations.

        Key observation 1: only two target parity patterns exist
        --------------------------------------------------------
        A parity alternating array must be one of:

            pattern 0: even at index 0, odd at index 1, even at index 2, ...
            pattern 1: odd  at index 0, even at index 1, odd  at index 2, ...

        For each pattern, an element either already has the correct parity or it
        does not.

        If it is wrong, one operation is necessary and sufficient:

            x -> x + 1

        or:

            x -> x - 1

        Both choices flip parity.

        Therefore, for a fixed target pattern:

            operations = number of indices whose parity does not match

        The minimum operation count is the smaller mismatch count across the two
        patterns.

        Key observation 2: after fixing the operation count, values have options
        -----------------------------------------------------------------------
        Suppose we choose one target pattern that achieves the minimum operation
        count.

        For each index:

        * If `nums[i]` already has the target parity:
              it must stay unchanged.

          Why?
          We are required to use exactly the minimum number of operations. Every
          mismatched index already needs one operation. Spending any operation on
          an already-correct index would exceed the minimum.

          So its possible final values are:

              {nums[i]}

        * If `nums[i]` has the wrong parity:
              it must be changed exactly once.

          It can become either:

              nums[i] - 1
              nums[i] + 1

          Both have the needed opposite parity.

          So its possible final values are:

              {nums[i] - 1, nums[i] + 1}

        Now the second objective becomes:

            choose one value from each index's option set
            minimize max(chosen_values) - min(chosen_values)

        This is a classic shortest range covering all groups problem.

        Data structure choice for the range problem
        -------------------------------------------
        Build a list of points:

            (possible_value, index)

        For each array index:

        * add one point if the value is fixed
        * add two points if the value can be `x - 1` or `x + 1`

        Then sort all points by `possible_value`.

        We need the shortest value interval `[L, R]` that contains at least one
        possible value for every index. If such an interval exists, choose one
        contained option per index, and every chosen value lies between `L` and
        `R`.

        To find the shortest covering interval, use a sliding window over the
        sorted points:

        * expand the right pointer and count which indices are covered
        * once all indices are covered, shrink the left pointer while preserving
          coverage
        * update the best width `points[right].value - points[left].value`

        This is the same idea as "smallest range covering elements from k
        lists", except each index has a tiny list of one or two possible final
        values.

        Algorithm
        ---------
        Define `evaluate(start_parity)`:

        1. `start_parity = 0` means target parity at index 0 is even.
           `start_parity = 1` means target parity at index 0 is odd.

        2. For each index `i`, target parity is:

               start_parity ^ (i % 2)

           because parity alternates every step.

        3. Count mismatches.

        4. Build option points:

               if nums[i] matches target:
                   options: nums[i]
               else:
                   options: nums[i] - 1 and nums[i] + 1

        5. Sort points and run sliding window to compute the smallest range.

        Then:

        * evaluate both target patterns
        * keep the smaller operation count
        * if both patterns tie on operations, take the smaller range

        Correctness proof
        -----------------
        Lemma 1:
        For a fixed target parity pattern, the minimum number of operations is
        exactly the number of mismatched indices.

        Proof:
        Every operation changes the parity of exactly one chosen element. If an
        index has the wrong parity, at least one operation must be applied to
        that index. One operation is enough because either `+1` or `-1` flips
        parity. Correct-parity indices need zero operations. Therefore the
        minimum operation count for that pattern is exactly the mismatch count.

        Lemma 2:
        The global minimum operation count is the smaller mismatch count of the
        two alternating patterns.

        Proof:
        Every parity alternating array must match exactly one of the two
        patterns: starting even or starting odd. By Lemma 1, each pattern's
        minimum cost is its mismatch count. Taking the smaller of the two gives
        the global minimum.

        Lemma 3:
        For a pattern that achieves the global minimum operation count, the
        option sets described above are exactly the values reachable using
        exactly that many operations.

        Proof:
        A matched index cannot be changed, because all minimum operations are
        already needed for mismatched indices; changing it would exceed the
        allowed operation count. A mismatched index must be changed once, and
        exactly one `+1` or `-1` operation produces `nums[i] + 1` or
        `nums[i] - 1`. These are the only possibilities under exactly one
        operation. Therefore the option sets are exact.

        Lemma 4:
        The sliding-window procedure returns the minimum possible range for one
        fixed target pattern.

        Proof:
        After sorting all option points by value, any final choice has a minimum
        chosen value `L` and maximum chosen value `R`. The sorted point interval
        between those two values contains at least one option for every index.
        Thus every valid final array corresponds to some covering window.

        Conversely, every covering window contains at least one option for each
        index, so choosing one covered option per index creates a valid final
        array whose range is at most the window width.

        The sliding window enumerates all minimal left boundaries for each right
        boundary while maintaining full coverage, so it finds the smallest
        covering width. Therefore it returns the optimal range for that pattern.

        Lemma 5:
        Among all arrays reachable with the global minimum operation count, the
        algorithm returns the smallest possible range.

        Proof:
        By Lemma 2, only patterns whose mismatch count equals the global minimum
        can be used. For each such pattern, Lemma 4 computes the best range. The
        algorithm takes the minimum range across those eligible patterns, so it
        returns the best possible range under exactly the minimum number of
        operations.

        Theorem:
        The algorithm returns the required answer.

        Proof:
        Lemmas 1 and 2 prove the first returned value is the minimum number of
        operations. Lemmas 3 through 5 prove the second returned value is the
        minimum possible `max - min` among arrays reachable using exactly that
        many operations. Therefore the returned pair is correct.

        Complexity analysis
        -------------------
        Let `n = len(nums)`.

        For each of two patterns, we build at most `2n` option points and sort
        them.

        Time:

            O(n log n)

        Reason:
        Sorting the option points dominates the linear mismatch count and
        sliding-window scan.

        Space:

            O(n)

        Reason:
        The points list has at most `2n` entries, and the sliding window stores
        counts for covered indices.

        Edge cases
        ----------
        * Length 1:
          The array is already parity alternating. Minimum operations are 0, and
          the range is `max - min = 0`.

        * Already alternating:
          Operation count is 0 for the matching pattern. All values are fixed,
          so the range is the original `max(nums) - min(nums)`.

        * Both patterns tie:
          This can happen for even `n`. We must evaluate the range for both
          patterns and choose the smaller second value.

        * Negative numbers:
          Parity checks with `x % 2` work in Python for negative values:
          even numbers give 0, odd numbers give 1.

        * Large values:
          Adding or subtracting 1 is safe with Python integers, and values are
          within normal integer ranges.

        Test strategy
        -------------
        Useful tests:

            [-2, -3, 1, 4] -> [2, 6]
            [0, 2, -2]     -> [1, 3]
            [7]            -> [0, 0]
            [1, 2, 3]      -> [0, 2]
            [2, 4]         -> [1, 1]
            [1, 1]         -> [1, 1]
            [2, 2, 2]      -> [1, 1]

        For brute-force confidence on small arrays, enumerate both parity
        patterns and all `-1/+1` choices for mismatched indices, then compare
        against this algorithm.

        Possible improvements
        ---------------------
        Because each index has only one or two options, there may be specialized
        ways to avoid sorting with coordinate tricks. But values can be as large
        as `10^9` and negative, so sorting the explicit option points is simple,
        robust, and easily fast enough for `n <= 10^5`.
        """

        n = len(nums)

        def evaluate(start_parity: int) -> tuple[int, int]:
            points: list[tuple[int, int]] = []
            operations = 0

            for i, value in enumerate(nums):
                target_parity = start_parity ^ (i & 1)
                if value % 2 == target_parity:
                    points.append((value, i))
                else:
                    operations += 1
                    points.append((value - 1, i))
                    points.append((value + 1, i))

            points.sort()

            counts: dict[int, int] = defaultdict(int)
            covered = 0
            best_range = float("inf")
            left = 0

            for right, (right_value, right_index) in enumerate(points):
                if counts[right_index] == 0:
                    covered += 1
                counts[right_index] += 1

                while covered == n:
                    left_value, left_index = points[left]
                    best_range = min(best_range, right_value - left_value)

                    counts[left_index] -= 1
                    if counts[left_index] == 0:
                        covered -= 1
                    left += 1

            return operations, int(best_range)

        even_start = evaluate(0)
        odd_start = evaluate(1)

        min_operations = min(even_start[0], odd_start[0])
        min_range = min(
            range_value
            for operations, range_value in (even_start, odd_start)
            if operations == min_operations
        )

        return [min_operations, min_range]
# @lc code=end
