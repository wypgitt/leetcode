#
# @lc app=leetcode id=673 lang=python3
#
# [673] Number of Longest Increasing Subsequence
#
# https://leetcode.com/problems/number-of-longest-increasing-subsequence/description/
#
# algorithms
# Medium (51.85%)
# Likes:    7323
# Dislikes: 288
# Total Accepted:    339.1K
# Total Submissions: 654K
# Testcase Example:  '[1,3,5,4,7]'
#
# Given an integer array nums, return the number of longest increasing
# subsequences.
# 
# Notice that the sequence has to be strictly increasing.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,3,5,4,7]
# Output: 2
# Explanation: The two longest increasing subsequences are [1, 3, 4, 7] and [1,
# 3, 5, 7].
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,2,2,2,2]
# Output: 5
# Explanation: The length of the longest increasing subsequence is 1, and there
# are 5 increasing subsequences of length 1, so output 5.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 2000
# -10^6 <= nums[i] <= 10^6
# The answer is guaranteed to fit inside a 32-bit integer.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def findNumberOfLIS(self, nums: List[int]) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given an integer array `nums`. A subsequence is formed by deleting
        zero or more elements without changing the order of the remaining
        elements.

        We need return the number of longest strictly increasing subsequences.

        Strictly increasing means:

            nums[i1] < nums[i2] < ... < nums[ik]

        for chosen indices:

            i1 < i2 < ... < ik

        Example:

            nums = [1, 3, 5, 4, 7]

        The LIS length is 4. There are two such subsequences:

            [1, 3, 5, 7]
            [1, 3, 4, 7]

        so the answer is 2.

        Key observation
        ---------------
        This is not only asking for the length of the LIS. It asks how many
        subsequences achieve the maximum length.

        For each index `i`, we track two pieces of information:

        1. `lengths[i]`
           The length of the longest increasing subsequence that ends exactly
           at index `i`.

        2. `counts[i]`
           The number of increasing subsequences of length `lengths[i]` that
           end exactly at index `i`.

        Why "ends at i"?
        ----------------
        Dynamic programming becomes natural when each state has a clear ending
        point.

        If a subsequence ends at `i`, then the previous element in that
        subsequence must be some index `j < i` with:

            nums[j] < nums[i]

        Therefore, every valid predecessor `j` can extend its best subsequences
        by appending `nums[i]`.

        Recurrence
        ----------
        Initialize:

            lengths[i] = 1
            counts[i] = 1

        because each element by itself is an increasing subsequence of length 1,
        and there is exactly one such subsequence ending at that element.

        For every pair `j < i`:

            if nums[j] < nums[i]:
                candidate_length = lengths[j] + 1

        There are two cases:

        Case 1: Found a longer way to end at `i`

            candidate_length > lengths[i]

        Then we replace the old best length:

            lengths[i] = candidate_length
            counts[i] = counts[j]

        Why reset the count?
        Because all shorter previous ways are no longer relevant. We only count
        subsequences that achieve the best length ending at `i`.

        Case 2: Found another way with the same best length

            candidate_length == lengths[i]

        Then we add:

            counts[i] += counts[j]

        Why add?
        Because every best subsequence ending at `j` can be extended by
        `nums[i]`, and these produce additional distinct index subsequences
        ending at `i`.

        Final answer
        ------------
        After filling the DP arrays:

            longest = max(lengths)

        The answer is the sum of `counts[i]` over all indices where:

            lengths[i] == longest

        Why sum across endpoints?
        The global LIS can end at different indices. Each endpoint owns the
        subsequences that end there, so summing those counts gives the total
        number of longest increasing subsequences.

        Data structure choice
        ---------------------
        We use two arrays:

        * `lengths`: list[int]
          Stores the best LIS length ending at each index.

        * `counts`: list[int]
          Stores how many best subsequences end at each index.

        Arrays are the right data structure here because:

        * each DP state is tied directly to an index
        * lookups by index are O(1)
        * we need all earlier states when processing the current index
        * the constraints are small enough for O(n^2)

        Why choose O(n^2) DP?
        ---------------------
        `nums.length <= 2000`, so checking every pair of indices is acceptable:

            2000 * 2000 = 4,000,000 pair checks

        That is easily fine in Python.

        This DP is also the cleanest interview solution because it explains both
        length and count in one direct recurrence.

        Correctness proof
        -----------------
        Lemma 1:
        After processing index `i`, `lengths[i]` is the length of the longest
        increasing subsequence ending at `i`.

        Proof:
        Any increasing subsequence ending at `i` either contains only `nums[i]`,
        giving length 1, or has a previous final index `j < i` with
        `nums[j] < nums[i]`. The algorithm checks every such valid predecessor
        and takes the maximum value of `lengths[j] + 1`. Therefore `lengths[i]`
        is exactly the best possible length ending at `i`.

        Lemma 2:
        After processing index `i`, `counts[i]` is the number of increasing
        subsequences of length `lengths[i]` ending at `i`.

        Proof:
        Initially, the single-element subsequence `[nums[i]]` gives one way of
        length 1. For every valid predecessor `j`, each best subsequence ending
        at `j` can be extended by `nums[i]`.

        If this creates a longer length than the current best ending at `i`, the
        old shorter counts are discarded and `counts[i]` becomes `counts[j]`.

        If it creates the same best length, those subsequences are additional
        distinct ways, so `counts[j]` is added.

        Since all valid predecessors are checked exactly once, `counts[i]`
        counts exactly the best subsequences ending at `i`.

        Lemma 3:
        Summing `counts[i]` for all indices with `lengths[i] == longest` gives
        the number of global longest increasing subsequences.

        Proof:
        Every longest increasing subsequence has exactly one final index `i`.
        By Lemma 2, `counts[i]` counts the longest subsequences ending at that
        specific index. Different final indices represent disjoint groups, so
        summing all endpoints with global maximum length counts every LIS once.

        Theorem:
        The algorithm returns the number of longest increasing subsequences.

        Proof:
        Lemma 1 gives correct LIS lengths for every endpoint. Lemma 2 gives
        correct counts for those endpoint-best lengths. Lemma 3 combines the
        counts for all endpoints that achieve the global maximum. Therefore the
        returned value is correct.

        Complexity analysis
        -------------------
        Let `n = len(nums)`.

        Time:

            O(n^2)

        Reason:
        For each index `i`, we scan all earlier indices `j < i`. The total
        number of pair checks is:

            0 + 1 + 2 + ... + (n - 1) = n(n - 1) / 2

        which is O(n^2).

        Space:

            O(n)

        Reason:
        We store two arrays of length n: `lengths` and `counts`.

        Edge cases
        ----------
        * Single element:
          `lengths = [1]`, `counts = [1]`, answer is 1.

        * All equal values:
          Example: `[2, 2, 2, 2, 2]`
          No value can extend another because the subsequence must be strictly
          increasing. Every single element is an LIS of length 1, so answer is 5.

        * Strictly increasing array:
          Example: `[1, 2, 3, 4]`
          There is one LIS using all elements, so answer is 1.

        * Strictly decreasing array:
          Example: `[4, 3, 2, 1]`
          Every single element is an LIS of length 1, so answer is 4.

        * Duplicate values mixed with increasing values:
          Example: `[1, 2, 2, 3]`
          The two different `2` indices create two different LIS:
          `[1, first 2, 3]` and `[1, second 2, 3]`, so answer is 2.

        Test strategy
        -------------
        Useful tests:

            [1, 3, 5, 4, 7] -> 2
            [2, 2, 2, 2, 2] -> 5
            [1] -> 1
            [1, 2, 3, 4] -> 1
            [4, 3, 2, 1] -> 4
            [1, 2, 2, 3] -> 2
            [1, 3, 2, 4, 3, 5] -> 3

        The last example has LIS length 4:

            [1, 3, 4, 5]
            [1, 2, 4, 5]
            [1, 2, 3, 5]

        Possible improvements
        ---------------------
        There is a more advanced O(n log n) approach using coordinate
        compression plus a Fenwick tree or segment tree. Each tree node stores:

            (best_length, number_of_ways)

        For every number `x`, query values strictly smaller than `x`, then update
        the coordinate of `x`.

        That approach is useful for much larger constraints, but it is harder to
        explain and easier to implement incorrectly. Since n <= 2000, the O(n^2)
        DP is the best interview choice here: simple, reliable, and comfortably
        within limits.
        """

        n = len(nums)
        lengths = [1] * n
        counts = [1] * n

        for i in range(n):
            for j in range(i):
                if nums[j] >= nums[i]:
                    continue

                candidate_length = lengths[j] + 1

                if candidate_length > lengths[i]:
                    lengths[i] = candidate_length
                    counts[i] = counts[j]
                elif candidate_length == lengths[i]:
                    counts[i] += counts[j]

        longest = max(lengths)
        return sum(count for length, count in zip(lengths, counts) if length == longest)
# @lc code=end
