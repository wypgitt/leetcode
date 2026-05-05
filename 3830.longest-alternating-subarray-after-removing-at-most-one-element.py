#
# @lc app=leetcode id=3830 lang=python3
#
# [3830] Longest Alternating Subarray After Removing At Most One Element
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given an array nums.
#
# A subarray is alternating if every adjacent comparison is strict and the
# comparison directions alternate:
#
#   nums[l] < nums[l+1] > nums[l+2] < ...
# or
#   nums[l] > nums[l+1] < nums[l+2] > ...
#
# We may remove at most one element from the whole array. After that, choose one
# alternating subarray. Return the maximum possible length.
#
# A length-1 subarray is always alternating.
#
#
# Important interpretation of deletion
# Removing one element from nums can join the elements immediately before and
# after it. Therefore the chosen subarray after deletion corresponds to:
#
#   - an ordinary contiguous subarray of the original array, or
#   - a contiguous original segment with exactly one internal element skipped.
#
# Removing an element outside the chosen subarray has no effect, and removing an
# endpoint is equivalent to just choosing a shorter subarray. So the only
# interesting deletion is deleting one internal element and bridging its
# neighbors.
#
#
# Work with comparison signs
# Define:
#   sign[i] = comparison between nums[i] and nums[i+1]
#
# Use:
#   +1 if nums[i] < nums[i+1]
#   -1 if nums[i] > nums[i+1]
#    0 if nums[i] == nums[i+1]
#
# A subarray is alternating exactly when its signs are all nonzero and adjacent
# signs are opposite.
#
# Example:
#   nums = [2, 1, 3, 2]
#   signs = [-1, +1, -1]
#   Signs alternate, so the whole array has length 4.
#
#
# No-deletion lengths
# Compute:
#   end_len[i] = length of the longest alternating subarray ending at index i
#   start_len[i] = length of the longest alternating subarray starting at index i
#
# Recurrence for end_len:
#   If nums[i-1] == nums[i], then end_len[i] = 1.
#   Else if the previous sign exists and is opposite to current sign,
#      end_len[i] = end_len[i-1] + 1.
#   Else
#      end_len[i] = 2.
#
# start_len is the same idea from right to left.
#
# The best no-deletion answer is:
#   max(end_len)
#
#
# Combining around one deleted element
# Suppose we delete index p, where 1 <= p <= n - 2.
#
# The new bridge comparison is between:
#   nums[p-1] and nums[p+1]
#
# Let:
#   bridge = cmp(nums[p-1], nums[p+1])
#
# If bridge == 0, we cannot build an alternating subarray that uses both sides,
# because equal adjacent values are not allowed.
#
# Otherwise, we can combine:
#   a left alternating subarray ending at p-1
#   the bridge comparison
#   a right alternating subarray starting at p+1
#
# But the signs next to the bridge must alternate with it.
#
# Left side:
#   If the left part has length >= 2, its last sign is sign[p-2].
#   To connect with bridge, we need:
#      sign[p-2] == -bridge
#
#   If that condition holds, we can use all of end_len[p-1].
#   Otherwise, the only safe left part is the single element nums[p-1].
#
# Right side:
#   If the right part has length >= 2, its first sign is sign[p+1].
#   To connect with bridge, we need:
#      sign[p+1] == -bridge
#
#   If that condition holds, we can use all of start_len[p+1].
#   Otherwise, the only safe right part is the single element nums[p+1].
#
# Candidate length after deleting p:
#   left_part_length + right_part_length
#
# Notice we do not add 1 for nums[p], because it is deleted.
#
#
# Why this is sufficient
# If an optimal answer uses a deletion, let p be the deleted internal element.
# The remaining selected elements on the left of p must form an alternating
# suffix ending at p-1, and the remaining selected elements on the right of p
# must form an alternating prefix starting at p+1. The only extra condition is
# whether those two pieces alternate correctly through the new bridge. That is
# exactly what the combine rule checks.
#
#
# Data structures
# We only need arrays:
#   sign      length n - 1
#   end_len   length n
#   start_len length n
#
# Arrays are the right choice because:
#   - every state is indexed directly by position,
#   - transitions are local,
#   - we need O(1) lookup while testing each deletion position.
#
#
# Walkthrough of the code
# 1. Build sign for every adjacent pair.
# 2. Fill end_len from left to right.
# 3. Fill start_len from right to left.
# 4. Initialize answer with max(end_len), the no-deletion case.
# 5. For every internal deletion p:
#      - compute bridge sign between nums[p-1] and nums[p+1]
#      - if bridge is zero, skip
#      - choose the largest compatible left piece
#      - choose the largest compatible right piece
#      - update the answer
# 6. Return answer.
#
#
# Correctness proof
#
# Lemma 1: end_len[i] is the longest alternating subarray ending at i without any
# deletion.
# Proof:
# If nums[i-1] == nums[i], no length-2 alternating subarray can end at i, so the
# best length is 1. Otherwise there is at least a length-2 subarray. It can extend
# the best subarray ending at i-1 exactly when the previous adjacent sign exists
# and is opposite to the current sign. If not, any longer suffix would contain two
# adjacent equal-direction signs, so the best length is 2.
#
# Lemma 2: start_len[i] is the longest alternating subarray starting at i without
# any deletion.
# Proof:
# Symmetric to Lemma 1, scanning from right to left.
#
# Lemma 3: For a fixed deleted index p, the combine rule gives the longest
# alternating subarray that uses elements from both sides of p.
# Proof:
# The bridge sign between nums[p-1] and nums[p+1] must be nonzero. On the left,
# any chosen piece of length at least 2 has the same final sign sign[p-2], so it
# can connect to the bridge iff sign[p-2] is opposite to bridge. If it can
# connect, Lemma 1 says end_len[p-1] is the longest possible left piece. If it
# cannot connect, the only valid left piece using p-1 is length 1. The same
# argument using Lemma 2 applies to the right side.
#
# Lemma 4: Every optimal solution is considered by the algorithm.
# Proof:
# If it uses no deletion, it is counted by max(end_len). If it uses a deletion at
# an internal index p and uses both sides, Lemma 3 says the algorithm considers
# the best such solution for p. If the deletion is outside the selected subarray
# or at its endpoint, the result is just an ordinary subarray and is already
# covered by max(end_len).
#
# Theorem: The algorithm returns the maximum possible length after removing at
# most one element.
# Proof:
# By Lemma 4, every possible optimal form is considered. By Lemmas 1, 2, and 3,
# every considered candidate length is computed correctly. Taking the maximum
# over all candidates gives the desired answer.
#
#
# Complexity analysis
#
# Let n = len(nums).
#
# Time:
#   - Build sign: O(n)
#   - Build end_len: O(n)
#   - Build start_len: O(n)
#   - Try each deleted index: O(n)
# Overall time complexity: O(n).
#
# Space:
#   - sign, end_len, and start_len are O(n).
# Overall space complexity: O(n).
#
#
# Tests to discuss in an interview
#
# 1. Already alternating:
#      nums = [2,1,3,2] -> 4
#
# 2. Deletion helps:
#      nums = [3,2,1,2,3,2,1] -> 4
#      Delete the middle 2 and choose [2,1,3,2].
#
# 3. Equal adjacent values:
#      nums = [100000,100000] -> 1
#
# 4. Strictly increasing:
#      nums = [1,2,3,4] -> 2
#      Deleting one element cannot make a longer alternating subarray.
#
# 5. Bridge equality:
#      nums = [1,3,2,3,1]
#      Some deletions create equal bridged neighbors, so those cannot combine
#      both sides.
#
# 6. Random brute force:
#      For small n, try every possible deletion and every subarray after deletion
#      to compare with this O(n) algorithm.
#
#
# Edge cases
#
# - n == 2: answer is 2 if nums[0] != nums[1], otherwise 1.
# - length-1 subarrays are always valid.
# - duplicate values break alternation because comparisons must be strict.
# - removing an element is optional; no-deletion answer must always be included.
#
#
# Possible improvements
#
# - Space can be reduced by avoiding the sign array or compressing one of the
#   length arrays, but O(n) space is simple and safe for n <= 10^5.
# - A sliding-window approach handles the no-deletion case, but deletion creates
#   a bridge comparison, making prefix/suffix DP clearer and less error-prone.
#
# -------------------------------------------------------------------------------

# @lc code=start
from typing import List


class Solution:
    def longestAlternating(self, nums: List[int]) -> int:
        n = len(nums)

        sign = [self._cmp(nums[i], nums[i + 1]) for i in range(n - 1)]

        end_len = [1] * n
        for i in range(1, n):
            if sign[i - 1] == 0:
                end_len[i] = 1
            elif i >= 2 and sign[i - 2] == -sign[i - 1]:
                end_len[i] = end_len[i - 1] + 1
            else:
                end_len[i] = 2

        start_len = [1] * n
        for i in range(n - 2, -1, -1):
            if sign[i] == 0:
                start_len[i] = 1
            elif i + 2 < n and sign[i] == -sign[i + 1]:
                start_len[i] = start_len[i + 1] + 1
            else:
                start_len[i] = 2

        ans = max(end_len)

        for removed in range(1, n - 1):
            bridge = self._cmp(nums[removed - 1], nums[removed + 1])
            if bridge == 0:
                continue

            if removed >= 2 and sign[removed - 2] == -bridge:
                left = end_len[removed - 1]
            else:
                left = 1

            if removed + 1 <= n - 2 and sign[removed + 1] == -bridge:
                right = start_len[removed + 1]
            else:
                right = 1

            ans = max(ans, left + right)

        return ans

    def _cmp(self, a: int, b: int) -> int:
        if a < b:
            return 1
        if a > b:
            return -1
        return 0


# @lc code=end
