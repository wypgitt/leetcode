#
# @lc app=leetcode id=3821 lang=python3
#
# [3821] Find Nth Smallest Integer With K One Bits
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given positive integers n and k.
#
# Return the n-th smallest positive integer whose binary representation contains
# exactly k one bits.
#
# It is guaranteed that the answer is strictly less than 2^50.
#
# Example:
#   n = 4, k = 2
#   Numbers with exactly two 1 bits:
#     3  = 0b11
#     5  = 0b101
#     6  = 0b110
#     9  = 0b1001
#   Answer = 9
#
#
# Key observation
# A positive integer with exactly k one bits is the same thing as choosing k bit
# positions to set.
#
# Since the answer is < 2^50, only bit positions 0..49 matter.
#
# Numbers are ordered by numeric value, which is the same as lexicographic order
# of their 50-bit binary strings from most significant bit to least significant
# bit:
#
#   smaller high bit first -> smaller number
#
# We can construct the answer bit by bit from high to low.
#
#
# Counting completions with combinations
# Suppose we are deciding bit b, and there are b lower bit positions remaining:
#   0, 1, ..., b-1
#
# If we put 0 at bit b, and still need rem one bits total, then the number of
# valid completions is:
#   C(b, rem)
#
# because we must choose rem positions among those b lower bits.
#
# If the n-th number lies inside that block, keep bit b = 0.
# Otherwise, skip that whole block:
#   n -= C(b, rem)
# and set bit b = 1.
#
# This is the standard unranking technique for combinations in numeric order.
#
#
# Why start from bit 49?
# The answer is guaranteed below 2^50, so the highest possible bit is 49.
# Leading zeros are allowed in our internal 50-bit view; they do not affect the
# integer value.
#
# Example with k = 1:
#   1, 2, 4, 8, ...
#
# The algorithm keeps high bits at 0 until the rank passes all numbers that fit
# in smaller lower-bit positions.
#
#
# Algorithm
# rem = k
# ans = 0
#
# For bit from 49 down to 0:
#   count_without_this_bit = C(bit, rem)
#
#   If n <= count_without_this_bit:
#       bit stays 0
#   Else:
#       n -= count_without_this_bit
#       set this bit in ans
#       rem -= 1
#
#   If rem == 0:
#       all required one bits are placed, so remaining bits are 0.
#       break
#
# Return ans.
#
#
# Data structure choice
# We only need binomial coefficients C(a, b) for 0 <= a <= 50.
#
# Python's math.comb is exact and fast for such tiny values, so no custom
# Pascal table is necessary. If implementing in a language without a built-in
# combination function, a small 51 x 51 Pascal table is ideal.
#
#
# Walkthrough for n = 4, k = 2
# We skip very high bits because C(bit, 2) is large enough to contain rank 4.
#
# At bit 3:
#   count with bit 3 = 0 is C(3, 2) = 3
#   These are:
#     3 = 0011
#     5 = 0101
#     6 = 0110
#
# n = 4 is not in those 3 numbers, so:
#   set bit 3
#   n = 4 - 3 = 1
#   rem = 1
#
# At bits 2 and 1:
#   keeping them 0 leaves enough completions for rank 1.
#
# At bit 0:
#   set bit 0
#
# Answer:
#   1001b = 9
#
#
# Correctness proof
#
# Lemma 1: Among numbers with a fixed already-chosen high-bit prefix, all numbers
# with current bit 0 are smaller than all numbers with current bit 1.
# Proof:
# Numeric comparison of binary strings is decided by the first bit where they
# differ from most significant to least significant. A 0 at that bit is always
# smaller than a 1 at that bit, regardless of lower bits.
#
# Lemma 2: If the current bit is set to 0, the number of valid completions is
# C(bit, rem).
# Proof:
# There are exactly bit lower positions remaining, and we still need rem one
# bits. Choosing which rem of those positions are 1 uniquely determines a valid
# completion, so the count is C(bit, rem).
#
# Lemma 3: The greedy decision at each bit preserves the target rank among
# numbers matching the current prefix.
# Proof:
# By Lemma 1, the 0-bit completions form one contiguous block before the 1-bit
# completions. By Lemma 2, the block size is C(bit, rem). If n is inside that
# block, the answer must have 0 at this bit. Otherwise, the answer has 1 at this
# bit, and subtracting the 0-block size gives its rank inside the 1-bit block.
#
# Theorem: The algorithm returns the n-th smallest positive integer with exactly
# k one bits.
# Proof:
# Starting from the empty prefix, repeatedly applying Lemma 3 chooses the unique
# next bit that contains the desired rank. After all k one bits are placed, the
# remaining lower bits must be 0. Therefore the constructed number is exactly the
# n-th number in sorted order.
#
#
# Complexity analysis
#
# The algorithm checks at most 50 bit positions.
#
# Time:
#   O(50), which is O(1) for the given constraints.
#
# Space:
#   O(1), ignoring the tiny internal work done by math.comb.
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      n = 4, k = 2 -> 9
#
# 2. Example 2:
#      n = 3, k = 1 -> 4
#
# 3. First number for any k:
#      n = 1, k = 3 -> 7
#      The smallest number with 3 ones is 0b111.
#
# 4. k = 1:
#      Sequence is powers of two: 1, 2, 4, 8, ...
#
# 5. High-bound behavior:
#      Cases where the answer uses bit 49 are handled because we scan from 49.
#
# 6. Brute force for small values:
#      Generate integers, filter by bit_count() == k, and compare early ranks.
#
#
# Edge cases
#
# - k = 1: still works; C(bit, 1) counts powers below the current bit.
# - n = 1: keeps every unnecessary high bit 0 and returns (1 << k) - 1.
# - k = 50: only possible answer under 2^50 is 2^50 - 1 for rank 1; constraints
#   guarantee valid input.
# - The result is positive because k >= 1.
#
#
# Possible improvements
#
# - Precomputing a Pascal triangle can avoid repeated calls to comb, but with
#   only 50 bits this is unnecessary in Python.
# - Binary searching the answer and counting numbers <= x with k bits is another
#   valid approach, but direct unranking is simpler and O(50).
#
# -------------------------------------------------------------------------------

# @lc code=start
from math import comb


class Solution:
    def nthSmallest(self, n: int, k: int) -> int:
        ans = 0
        remaining = k

        for bit in range(49, -1, -1):
            count_with_zero = comb(bit, remaining)

            if n > count_with_zero:
                n -= count_with_zero
                ans |= 1 << bit
                remaining -= 1
                if remaining == 0:
                    break

        return ans


# @lc code=end
