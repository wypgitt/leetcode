#
# @lc app=leetcode id=3877 lang=python3
#
# [3877] Minimum Removals to Achieve Target XOR
#
# https://leetcode.com/problems/minimum-removals-to-achieve-target-xor/description/
#
# algorithms
# Medium (41.71%)
# Likes:    92
# Dislikes: 4
# Total Accepted:    21.5K
# Total Submissions: 51.6K
# Testcase Example:  '[1,2,3]\n2'
#
# You are given an integer array nums and an integer target.
# 
# You may remove any number of elements from nums (possibly zero).
# 
# Return the minimum number of removals required so that the bitwise XOR of the
# remaining elements equals target. If it is impossible to achieve target,
# return -1.
# 
# The bitwise XOR of an empty array is 0.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,2,3], target = 2
# 
# Output: 1
# 
# Explanation:
# 
# 
# Removing nums[1] = 2 leaves [nums[0], nums[2]] = [1, 3].
# The XOR of [1, 3] is 2, which equals target.
# It is not possible to achieve XOR = 2 in less than one removal, therefore the
# answer is 1.
# 
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,4], target = 1
# 
# Output: -1
# 
# Explanation:
# 
# It is impossible to remove elements to achieve target. Thus, the answer is
# -1.
# 
# 
# Example 3:
# 
# 
# Input: nums = [7], target = 7
# 
# Output: 0
# 
# Explanation:
# 
# The XOR of all elements is nums[0] = 7, which equals target. Thus, no removal
# is needed.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 40
# 0 <= nums[i] <= 10^4
# 0 <= target <= 10^4
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def minRemovals(self, nums: List[int], target: int) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given an array `nums` and a `target`.

        We may remove any elements.  After removals, the XOR of the remaining
        elements must equal `target`.  We need the minimum number of removed
        elements.  The XOR of an empty array is defined as 0.

        Reframe the goal
        ----------------
        Instead of asking:

            "What is the minimum number of elements to remove?"

        ask:

            "What is the maximum number of elements we can keep while making the
             kept elements XOR to target?"

        If the largest valid kept subset has size `best_kept`, then:

            removals = len(nums) - best_kept

        If no subset can produce `target`, return -1.

        Key observation: XOR state space is small
        -----------------------------------------
        The constraints say:

            nums[i] <= 10^4
            target <= 10^4

        Since 10^4 < 2^14 = 16384, every number uses at most 14 bits.  XOR of
        14-bit numbers is still a 14-bit number, so every possible subset XOR is
        in:

            0..16383

        That gives us only 16384 possible XOR states.

        DP definition
        -------------
        Let:

            dp[x] = maximum number of kept elements among processed numbers
                    whose XOR equals x

        If XOR `x` is not reachable, `dp[x] = -infinity`.

        Start:

            dp[0] = 0

        because keeping no elements gives XOR 0 with size 0.

        Transition
        ----------
        For each number `value`, we have two choices:

        1. Remove it / do not keep it:

               XOR stays the same
               kept size stays the same

        2. Keep it:

               old_xor becomes old_xor ^ value
               kept size increases by 1

        So for every reachable `old_xor`:

            next_dp[old_xor] = max(next_dp[old_xor], dp[old_xor])
            next_dp[old_xor ^ value] =
                max(next_dp[old_xor ^ value], dp[old_xor] + 1)

        At the end:

            if dp[target] is unreachable -> -1
            otherwise -> len(nums) - dp[target]

        Data structure choice
        ---------------------
        We use a list of length `16384`.

        Why a list instead of a dictionary?

        * The full XOR universe is small and fixed.
        * List indexing is fast.
        * It keeps every state explicit and simple to reason about.

        A dictionary of reachable states would also work, but with only 16384
        states the array DP is straightforward and efficient.

        Correctness proof
        -----------------
        Lemma 1: After processing some prefix of `nums`, `dp[x]` equals the
        maximum number of kept elements from that prefix whose XOR is `x`, or is
        unreachable if no such subset exists.
        Initially, before processing any numbers, the only possible kept subset
        is the empty subset, which has XOR 0 and size 0.  This matches `dp[0]`.
        When processing a new value, every subset of the new prefix either does
        not keep that value, in which case it comes from the old same-XOR state,
        or keeps that value, in which case it comes from an old state whose XOR
        becomes `old_xor ^ value`.  The transition considers both choices and
        keeps the maximum size for each XOR.  Therefore the invariant holds by
        induction.

        Lemma 2: At the end, `dp[target]` is the maximum possible number of
        elements that can remain with XOR equal to `target`.
        This follows directly from Lemma 1 after all elements have been
        processed.

        Lemma 3: If the maximum kept size is `best_kept`, the minimum removals
        needed is `len(nums) - best_kept`.
        Any valid final array is exactly a kept subset.  Removing fewer elements
        is equivalent to keeping more elements.  Therefore the minimum removals
        are achieved by the valid subset with maximum size.

        Theorem: The algorithm returns the required minimum number of removals,
        or -1 if impossible.
        By Lemma 2, the algorithm knows the largest valid kept subset size.  If
        no such subset exists, `target` is unreachable and the correct answer is
        -1.  Otherwise, by Lemma 3, `len(nums) - dp[target]` is exactly the
        minimum number of removals.

        Complexity analysis
        -------------------
        Let:

            n = len(nums)
            X = 16384

        For each number, we scan all possible XOR states.

        Total time:  O(n * X) = O(n * 16384)
        Total space: O(X) = O(16384)

        With n <= 40, this is very small.

        Edge cases
        ----------
        * target is already the XOR of the whole array:
          The DP can keep all n elements, so the answer is 0.

        * target = 0:
          The empty subset always has XOR 0, so it is always possible.  The DP
          still tries to keep as many elements as possible with XOR 0.

        * Impossible target:
          If no subset XOR equals target, return -1.

        * Single element:
          If nums[0] == target, answer is 0.  If target == 0, answer is 1 by
          removing the element.  Otherwise answer is -1.

        * Duplicate values:
          Each occurrence is a separate element and may be kept or removed
          independently.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              nums = [1,2,3], target = 2 -> 1
              nums = [2,4],   target = 1 -> -1
              nums = [7],     target = 7 -> 0

        * Empty kept subset:
              nums = [5], target = 0 -> 1

        * Duplicates:
              nums = [4,4], target = 0 -> 0, because keeping both gives 0

        * Random small arrays:
          Compare the DP against brute-force enumeration of all subsets.

        Possible improvement?
        ---------------------
        A linear XOR basis can decide reachability very efficiently, but this
        problem asks for the maximum subset size for a target XOR, not just
        whether the target is reachable.  Tracking cardinality with a basis is
        more subtle.  Given the tiny 14-bit XOR state space, this DP is simpler,
        safer, and fast enough.
        """

        max_xor = 1 << 14
        unreachable = -10**9

        dp = [unreachable] * max_xor
        dp[0] = 0

        for value in nums:
            next_dp = dp[:]
            for xor_value, kept_count in enumerate(dp):
                if kept_count == unreachable:
                    continue

                new_xor = xor_value ^ value
                if kept_count + 1 > next_dp[new_xor]:
                    next_dp[new_xor] = kept_count + 1

            dp = next_dp

        if dp[target] == unreachable:
            return -1

        return len(nums) - dp[target]
# @lc code=end
