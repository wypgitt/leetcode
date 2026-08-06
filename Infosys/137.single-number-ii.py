#
# @lc app=leetcode id=137 lang=python3
#
# [137] Single Number II
#
# =============================================================================
# INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
# =============================================================================
#
# 30 seconds:
#   "Every number except one appears three times. Count each bit position across
#   all numbers: if the total count of 1s is not divisible by 3, that bit is
#   set in the unique answer. Rebuild the integer from those bits."
#
# 2–4 minutes — two standard angles:
#
#   (A) Bit-count / modulo 3 (usually easiest to derive live):
#       - For bit position i, each triple contributes either 0 or 3 to the sum
#         of bits; the singleton contributes 0 or 1. So (sum of bits at i) % 3
#         equals the i-th bit of the answer.
#       - Do this for i = 0..31, OR the bits into `ans`.
#       - At the end, interpret `ans` as a signed 32-bit int for languages /
#         Python big-int quirks (see EDGE CASES).
#
#   (B) “Digital logic” / state machine (one pass, same complexity):
#       - For each bit position, count occurrences mod 3 using two masks:
#         `once` = bits seen 1 mod 3 times; `twice` = bits seen 2 mod 3 times.
#       - Update rules (derived from truth table or small FSM):
#             once = (once ^ x) & ~twice
#             twice = (twice ^ x) & ~once
#       - After all numbers, `once` holds the unique value; `twice` is 0.
#
# =============================================================================
# ALGORITHM (implemented below: approach B)
# =============================================================================
#
# We maintain two integers `once` and `twice` such that, independently for
# every bit index, the pair encodes count(x) mod 3 for that bit as we stream
# through `nums`:
#   count ≡ 0 (mod 3) → bit off in both once and twice
#   count ≡ 1 (mod 3) → bit on in once only
#   count ≡ 2 (mod 3) → bit on in twice only
#
# Processing `x`, the updates XOR in the new number (toggle) but AND with a
# complement mask clears transitions that would violate the mod-3 discipline.
# This is equivalent to a tiny 3-state FSM per bit, SIMD-packed into ints.
#
# Why XOR: toggles presence of a bit; combined with & ~other mask it enforces
# “third occurrence resets to zero,” matching triple-cancel behavior.
#
# =============================================================================
# DATA STRUCTURES
# =============================================================================
#
# - nums: input list (read-only conceptually; we don’t mutate it).
# - once, twice: two integers acting as parallel bit vectors (no auxiliary
#   arrays). Space O(1) beyond input.
#
# Alternative (approach A): no extra state beyond an accumulator `ans`; inner
# loop counts bits — still O(1) extra space, O(32 · n) time.
#
# =============================================================================
# COMPLEXITY
# =============================================================================
#
# Time:  O(n) — single pass over nums; bitwise ops are O(1) per element.
# Space: O(1) — two integer registers (32-bit conceptual; Python ints are
#        bigger but constant-sized for fixed bit-width reasoning in interviews).
#
# Approach A is O(32 · n) time, still O(n) asymptotically; often easier to code
# under pressure.
#
# =============================================================================
# EDGE CASES
# =============================================================================
#
# - n == 1: loop runs once; `once == nums[0]`, return it.
# - All duplicates except one: guaranteed by problem statement.
# - Negative values / 32-bit range: LeetCode uses signed 32-bit values. The FSM
#   solution operates on full Python ints; XOR / & / ~ behave consistently with
#   the problem tests (we verified sample negatives).
# - Approach A only: after OR-ing bits, if the unsigned value is ≥ 2^31,
#   subtract 2^32 to interpret as signed 32-bit (Python users often need this).
# - Overflow: not an issue for 32-bit constraints when using int32 reasoning.
#
# =============================================================================
# TESTING (what you’d say or code in a take-home)
# =============================================================================
#
# Unit tests:
#   - Minimal: [2,2,2,3] → 3
#   - With zero: [0,0,0,5] → 5
#   - Mixed: published LC examples (positive singleton).
#   - Negative singleton (if allowed by platform): e.g. mix of negatives with
#     triples; compare result to brute-force Counter (frequency mod 3).
# Property:
#   - Result XOR’d three times with triples conceptually “disappears”; easier
#     to sanity-check with bit-count method mentally on tiny vectors.
# Stress:
#   - Random valid arrays (generate value appearing once, others thrice);
#     compare O(n) solution vs Counter-mod-3 reference for many seeds.
#
# =============================================================================

# @lc code=start
from typing import List


class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        """
        Every element appears three times except one element appears once.

        Implementation: two-mask finite-state machine (see module docstring).
        `once` collects bits whose cumulative count mod 3 is 1 — that is the
        unique number after processing all inputs.
        """
        once = 0
        twice = 0

        for x in nums:
            # Encourage interviewer narration:
            # - XOR toggles current bit into `once` unless blocked by `twice`.
            # - `& ~twice`: if this bit already appeared twice, don't put it in
            #   `once` from this XOR step (third arrival clears via cooperation
            #   with second line).
            once = (once ^ x) & ~twice
            # Symmetric update for “two mod three” register.
            twice = (twice ^ x) & ~once

        # Bits never settle in `twice` alone as the final answer — singleton
        # lives in `once`.
        return once


# Alternative reference (approach A) — often easier to derive in interview:
#
#     ans = 0
#     for i in range(32):
#         bit_sum = sum((num >> i) & 1 for num in nums)
#         if bit_sum % 3:
#             ans |= 1 << i
#     if ans >= 2**31:
#         ans -= 2**32
#     return ans
#
# @lc code=end
