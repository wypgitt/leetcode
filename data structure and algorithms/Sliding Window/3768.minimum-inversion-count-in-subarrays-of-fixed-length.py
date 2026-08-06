#
# @lc app=leetcode id=3768 lang=python3
#
# [3768] Minimum Inversion Count in Subarrays of Fixed Length
#
# https://leetcode.com/problems/minimum-inversion-count-in-subarrays-of-fixed-length/description/
#
# algorithms
# Hard (42.73%)
# Likes:    50
# Dislikes: 4
# Total Accepted:    5.1K
# Total Submissions: 11.9K
# Testcase Example:  '[3,1,2,5,4]\n3'
#
# You are given an integer array nums of length n and an integer k.
# 
# An inversion is a pair of indices (i, j) from nums such that i < j and
# nums[i] > nums[j].
# 
# The inversion count of a subarray is the number of inversions within it.
# 
# Return the minimum inversion count among all subarrays of nums with length
# k.
# 
# 
# Example 1:
# 
# 
# Input: nums = [3,1,2,5,4], k = 3
# 
# Output: 0
# 
# Explanation:
# 
# We consider all subarrays of length k = 3 (indices below are relative to each
# subarray):
# 
# 
# [3, 1, 2] has 2 inversions: (0, 1) and (0, 2).
# [1, 2, 5] has 0 inversions.
# [2, 5, 4] has 1 inversion: (1, 2).
# 
# 
# The minimum inversion count among all subarrays of length 3 is 0, achieved by
# subarray [1, 2, 5].
# 
# 
# Example 2:
# 
# 
# Input: nums = [5,3,2,1], k = 4
# 
# Output: 6
# 
# Explanation:
# 
# There is only one subarray of length k = 4: [5, 3, 2, 1].
# Within this subarray, the inversions are: (0, 1), (0, 2), (0, 3), (1, 2), (1,
# 3), and (2, 3).
# Total inversions is 6, so the minimum inversion count is 6.
# 
# 
# Example 3:
# 
# 
# Input: nums = [2,1], k = 1
# 
# Output: 0
# 
# Explanation:
# 
# All subarrays of length k = 1 contain only one element, so no inversions are
# possible.
# The minimum inversion count is therefore 0.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n == nums.length <= 10^5
# 1 <= nums[i] <= 10^9
# 1 <= k <= n
# 
# 
#

# @lc code=start
from bisect import bisect_left
from typing import List


class FenwickTree:
    def __init__(self, size: int):
        self.size = size
        self.tree = [0] * (size + 1)

    def add(self, index: int, delta: int) -> None:
        while index <= self.size:
            self.tree[index] += delta
            index += index & -index

    def prefix_sum(self, index: int) -> int:
        total = 0
        while index > 0:
            total += self.tree[index]
            index -= index & -index
        return total

    def range_sum(self, left: int, right: int) -> int:
        if left > right:
            return 0
        return self.prefix_sum(right) - self.prefix_sum(left - 1)


class Solution:
    def minInversionCount(self, nums: List[int], k: int) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given an array `nums` and a fixed length `k`.

        For every contiguous subarray of length `k`, compute its inversion
        count:

            number of pairs (i, j) such that i < j and nums[i] > nums[j]

        Return the minimum inversion count among all length-`k` subarrays.

        Why not recompute each window from scratch?
        -------------------------------------------
        There are O(n) windows.  A naive inversion count for one window costs
        O(k^2), so the total would be O(n * k^2), which is too slow for
        `n <= 10^5`.

        We need to update the inversion count as the window slides by one
        position.

        Sliding-window idea
        -------------------
        Suppose the current window is:

            nums[left..right]

        and we know its inversion count.

        When sliding to the next window:

        1. Remove `nums[left]`, the leftmost value.
        2. Add `nums[right + 1]`, the new rightmost value.

        We only need to adjust the inversions involving these two values.

        Removing the leftmost value
        ---------------------------
        Let:

            outgoing = nums[left]

        Since it is the leftmost element of the current window, it can only be
        the first index of an inversion.  Its inversions are exactly the elements
        to its right that are smaller than it:

            count of values < outgoing in the rest of the window

        So we subtract that count from the current inversion count.

        Adding the new rightmost value
        ------------------------------
        Let:

            incoming = nums[right + 1]

        Since it is appended to the right end of the window, it can only be the
        second index of a new inversion.  New inversions are exactly existing
        window elements greater than it:

            count of values > incoming in the current window

        So we add that count.

        Data structure choice
        ---------------------
        We need a multiset of the current window that supports:

        * insert one value
        * delete one value
        * count values smaller than x
        * count values greater than x

        Python does not have a built-in balanced binary search tree.  A sorted
        list would make middle insert/delete O(k), which can be too slow.

        A Fenwick tree gives O(log n) updates and prefix-count queries after
        coordinate compression.

        Coordinate compression
        ----------------------
        Values can be as large as `10^9`, but only their relative order matters.

        We map each distinct value to a rank:

            smallest value -> 1
            next value     -> 2
            ...

        Then the Fenwick tree stores counts by rank.

        For a value with rank `r`:

        * count of values < value:

              fenwick.prefix_sum(r - 1)

        * count of values <= value:

              fenwick.prefix_sum(r)

        * count of values > value in a window of size `window_size`:

              window_size - fenwick.prefix_sum(r)

        Strict inequality matters.  Equal values do not form inversions, so we
        use `<` and `>` rather than `<=` and `>=`.

        Algorithm
        ---------
        1. Coordinate-compress all values in `nums`.
        2. Build the first window from left to right:
              * when adding value `x`, all previous elements are to its left
              * it creates inversions with previous elements greater than `x`
        3. Store this as the current answer candidate.
        4. For each next window:
              a. Let `outgoing` be the value leaving on the left.
              b. Subtract the number of smaller values still in the window.
              c. Remove `outgoing` from the Fenwick tree.
              d. Let `incoming` be the value entering on the right.
              e. Add the number of existing values greater than `incoming`.
              f. Insert `incoming` into the Fenwick tree.
              g. Update the minimum answer.

        Correctness proof
        -----------------
        Lemma 1: While building a window from left to right, adding a value `x`
        increases the inversion count by the number of already-added values
        greater than `x`.
        In an inversion `(i, j)`, the new value is at the rightmost position, so
        it can only serve as `j`.  The pair is an inversion exactly when the
        earlier value is greater than `x`.

        Lemma 2: When removing the leftmost value `x` from a window, the number
        of removed inversions is the number of remaining values smaller than
        `x`.
        Since `x` is leftmost, it cannot be the second index of an inversion
        inside the window.  It is involved only in pairs `(x, y)` where `y`
        appears to its right, and such a pair is an inversion exactly when
        `x > y`.

        Lemma 3: When adding a new rightmost value `x`, the number of added
        inversions is the number of current window values greater than `x`.
        This is the same reasoning as Lemma 1: the new value is the second index
        of every new pair.

        Lemma 4: After each slide, `current_inversions` equals the inversion
        count of the current window.
        The previous value is correct by induction.  Lemma 2 subtracts exactly
        the inversions that disappear when the leftmost value is removed.
        Lemma 3 adds exactly the inversions created by the new rightmost value.
        No other pair changes membership or relative order.

        Theorem: The algorithm returns the minimum inversion count among all
        length-`k` subarrays.
        By Lemma 1, the first window count is correct.  By Lemma 4, every
        subsequent window count is correct after sliding.  The algorithm takes
        the minimum over exactly all length-`k` windows, so the returned value is
        correct.

        Complexity analysis
        -------------------
        Let:

            n = len(nums)
            D = number of distinct values, D <= n

        Coordinate compression:

            O(n log n)

        Each insert/delete/count query costs:

            O(log D)

        We do O(n) such operations while building and sliding windows.

        Total time:

            O(n log n)

        Space:

            O(n)

        for compressed values and the Fenwick tree.

        Edge cases
        ----------
        * k = 1:
          A single element has no pairs, so the answer is 0.

        * k = n:
          There is only one window; we return the inversion count of the whole
          array.

        * Duplicate values:
          Equal values are not inversions.  The rank queries use strict
          smaller/greater counts.

        * Already sorted window:
          Inversion count is 0, the minimum possible.

        * Reverse-sorted window:
          A length-k reverse sorted window has `k * (k - 1) / 2` inversions.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              [3,1,2,5,4], k = 3 -> 0
              [5,3,2,1],   k = 4 -> 6
              [2,1],       k = 1 -> 0

        * Duplicates.
        * `k == n`.
        * Small random arrays compared with brute force.

        Possible improvement
        --------------------
        This O(n log n) method is the standard robust solution.  If values were
        already in a small range, coordinate compression could be skipped, but
        with values up to `10^9`, compression is the right general approach.
        """

        if k == 1:
            return 0

        sorted_values = sorted(set(nums))
        ranks = [bisect_left(sorted_values, value) + 1 for value in nums]
        fenwick = FenwickTree(len(sorted_values))

        current_inversions = 0

        for index in range(k):
            rank = ranks[index]
            previous_count = index
            greater_count = previous_count - fenwick.prefix_sum(rank)
            current_inversions += greater_count
            fenwick.add(rank, 1)

        answer = current_inversions

        for right in range(k, len(nums)):
            left = right - k

            outgoing_rank = ranks[left]
            smaller_count = fenwick.prefix_sum(outgoing_rank - 1)
            current_inversions -= smaller_count
            fenwick.add(outgoing_rank, -1)

            incoming_rank = ranks[right]
            window_size_before_insert = k - 1
            greater_count = (
                window_size_before_insert - fenwick.prefix_sum(incoming_rank)
            )
            current_inversions += greater_count
            fenwick.add(incoming_rank, 1)

            answer = min(answer, current_inversions)

        return answer
# @lc code=end


if __name__ == "__main__":
    def brute_force_min_inversion_count(values: List[int], length: int) -> int:
        best = 10**18

        for left in range(0, len(values) - length + 1):
            window = values[left:left + length]
            inversions = 0

            for i in range(length):
                for j in range(i + 1, length):
                    if window[i] > window[j]:
                        inversions += 1

            best = min(best, inversions)

        return best

    solution = Solution()

    fixed_tests = [
        ([3, 1, 2, 5, 4], 3, 0),
        ([5, 3, 2, 1], 4, 6),
        ([2, 1], 1, 0),
        ([1, 1, 1], 2, 0),
        ([3, 2, 1, 3, 2, 1], 3, 1),
        ([4, 3, 2, 1], 2, 1),
    ]

    for test_nums, test_k, expected in fixed_tests:
        assert solution.minInversionCount(test_nums, test_k) == expected

    brute_force_cases = [
        ([2, 2, 1, 3, 1], 3),
        ([5, 1, 4, 2, 3], 4),
        ([1, 3, 2, 3, 1], 2),
        ([9, 8, 7, 6, 5], 5),
    ]

    for test_nums, test_k in brute_force_cases:
        expected = brute_force_min_inversion_count(test_nums, test_k)
        assert solution.minInversionCount(test_nums, test_k) == expected
