#
# @lc app=leetcode id=3900 lang=python3
#
# [3900] Longest Balanced Substring After One Swap
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given a binary string s.
#
# A string is balanced if it has the same number of '0' and '1' characters.
#
# We may perform at most one swap between any two characters in s. After that,
# choose a balanced substring. Return the maximum possible length.
#
# The empty substring is allowed, so if no non-empty balanced substring exists,
# the answer is 0.
#
# Example:
#   s = "100001"
#   With one swap, the best balanced substring has length 4.
#
#
# Key observation: what can one swap change for one chosen substring?
# Fix a substring interval [l, r].
#
# A swap can affect the substring count in only three meaningful ways:
#
# 1. Swap two characters both inside the substring:
#      The substring still contains the same multiset of characters.
#
# 2. Swap two characters both outside the substring:
#      The substring is unchanged.
#
# 3. Swap one character inside with one character outside:
#      If they are different characters, the substring changes by:
#        - one more '1' and one fewer '0', or
#        - one more '0' and one fewer '1'
#
# Therefore, if we define:
#
#   balance = (# of '1') - (# of '0')
#
# then one useful swap can change a substring's balance by exactly +2 or -2.
#
# So a substring can become balanced iff its original balance is:
#   0, 2, or -2
#
# with an extra availability condition for the +/-2 cases.
#
#
# Availability conditions
# Case 1: balance = 0
#   Already balanced. No swap needed.
#
# Case 2: balance = 2
#   The substring has two more ones than zeros.
#   To balance it, swap an inside '1' with an outside '0'.
#   Therefore, there must be at least one zero outside the substring.
#
# Case 3: balance = -2
#   The substring has two more zeros than ones.
#   To balance it, swap an inside '0' with an outside '1'.
#   Therefore, there must be at least one one outside the substring.
#
#
# Convert availability to a length cap
# Let L be the substring length.
#
# If balance = 2:
#   ones - zeros = 2
#   L = ones + zeros = 2 * zeros + 2
#
# Need at least one zero outside:
#   zeros_in_substring < total_zeros
#
# So:
#   zeros_in_substring <= total_zeros - 1
#   L = 2 * zeros_in_substring + 2 <= 2 * total_zeros
#
# Thus, balance = 2 is fixable iff:
#   L <= 2 * total_zeros
#
# Similarly, balance = -2 is fixable iff:
#   L <= 2 * total_ones
#
#
# Prefix balance
# Let:
#   pref[0] = 0
#   pref[i+1] = pref[i] + 1 if s[i] == '1'
#             = pref[i] - 1 if s[i] == '0'
#
# For substring s[l..r-1]:
#   balance = pref[r] - pref[l]
#   length = r - l
#
# We need the longest interval satisfying one of:
#
#   pref[r] - pref[l] = 0
#   pref[r] - pref[l] = 2  and r-l <= 2*total_zeros
#   pref[r] - pref[l] = -2 and r-l <= 2*total_ones
#
#
# Data structure choice
# Store all prefix indices for each prefix-balance value:
#
#   positions[balance] = sorted list of prefix indices with that balance
#
# The lists are naturally sorted because we build them from left to right.
#
# For each right endpoint r:
#
#   balance 0:
#      use the earliest previous same-balance prefix.
#
#   balance 2 or -2 with length cap:
#      find the smallest prefix index l with the required balance and
#      l >= r - cap.
#
# This is a lower_bound / binary search query in positions[needed_balance].
#
#
# Algorithm
# 1. Count total zeros and ones.
# 2. Build prefix balances and positions lists.
# 3. Compute the best already-balanced substring:
#      maximum distance between equal prefix balances.
# 4. For every right prefix index r:
#      - For balance = 2, need pref[l] = pref[r] - 2 and length <= 2*zeros.
#      - For balance = -2, need pref[l] = pref[r] + 2 and length <= 2*ones.
#      Use binary search to find the earliest valid l inside the length cap.
# 5. Return the maximum length found.
#
#
# Correctness proof
#
# Lemma 1: A substring can become balanced after at most one swap only if its
# original balance is 0, 2, or -2.
# Proof:
# A swap entirely inside or outside the substring does not change its counts.
# A useful inside/outside swap of different characters changes one zero to one
# one, or one one to one zero. That changes (#ones - #zeros) by +2 or -2.
# Therefore the original balance must be 0, 2, or -2.
#
# Lemma 2: A substring with balance 2 is fixable iff it has a zero outside the
# substring. Equivalently, its length is at most 2*total_zeros.
# Proof:
# Balance 2 means it has too many ones. The only way to fix it with one swap is
# to bring in an outside zero and send out an inside one. This requires a zero
# outside. The algebra above shows this is equivalent to length <= 2*total_zeros.
#
# Lemma 3: A substring with balance -2 is fixable iff its length is at most
# 2*total_ones.
# Proof:
# Symmetric to Lemma 2, swapping an inside zero with an outside one.
#
# Lemma 4: Prefix balances characterize substring balances correctly.
# Proof:
# pref[r] - pref[l] is the sum of +1 for ones and -1 for zeros over s[l..r-1],
# which is exactly (#ones - #zeros) in that substring.
#
# Lemma 5: For every right endpoint r and target balance condition, the binary
# search query finds the longest valid substring ending at r for that condition.
# Proof:
# A longer substring has smaller l. The length cap requires l >= r - cap. Among
# prefix indices with the required balance, the smallest l satisfying that lower
# bound gives the maximum length. lower_bound returns exactly that index.
#
# Theorem: The algorithm returns the maximum balanced substring length after at
# most one swap.
# Proof:
# By Lemmas 1, 2, and 3, every achievable substring belongs to exactly one of the
# three tested cases: balance 0, fixable balance 2, or fixable balance -2. By
# Lemma 4, these cases translate to prefix-balance differences. By Lemma 5, the
# algorithm finds the best interval for each right endpoint and each case.
# Taking the maximum over all endpoints gives the global optimum.
#
#
# Complexity analysis
#
# Let n = len(s).
#
# Time:
#   - Build prefix balances and positions: O(n)
#   - Balanced case with earliest positions: O(n)
#   - For every prefix endpoint, do at most two binary searches: O(n log n)
# Overall time complexity: O(n log n).
#
# Space:
#   - prefix array and positions dictionary store O(n) indices.
# Overall space complexity: O(n).
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      s = "100001" -> 4
#
# 2. Example 2:
#      s = "111" -> 0
#
# 3. Already balanced:
#      s = "1010" -> 4
#
# 4. One swap extends:
#      s = "00111" -> 4
#
# 5. All zeros:
#      s = "0000" -> 0
#
# 6. Random brute force:
#      For small n, try every possible swap and every substring, then compare
#      with this prefix-balance solution.
#
#
# Edge cases
#
# - Empty substring is allowed, so answer can be 0.
# - If the string has no zeros or no ones, no non-empty balanced substring exists.
# - Swapping equal characters has no effect and is covered by the no-swap case.
# - The chosen substring after swapping is still an interval of indices in the
#   final string, which corresponds to the same interval positions in the
#   original string with possibly one inside/outside character exchanged.
#
#
# Possible improvements
#
# - The binary searches can be replaced by sliding pointers per balance to get
#   O(n), but O(n log n) is already excellent for n <= 1e5 and much simpler.
# - Another view is to binary search the answer length and test feasibility, but
#   direct prefix-balance enumeration is cleaner.
#
# -------------------------------------------------------------------------------

# @lc code=start
from bisect import bisect_left
from collections import defaultdict


class Solution:
    def longestBalanced(self, s: str) -> int:
        total_zeros = s.count("0")
        total_ones = len(s) - total_zeros

        prefix = [0]
        positions = defaultdict(list)
        positions[0].append(0)

        balance = 0
        for index, ch in enumerate(s, 1):
            balance += 1 if ch == "1" else -1
            prefix.append(balance)
            positions[balance].append(index)

        answer = 0
        earliest = {}
        for index, balance in enumerate(prefix):
            if balance in earliest:
                answer = max(answer, index - earliest[balance])
            else:
                earliest[balance] = index

        cap_too_many_ones = 2 * total_zeros
        cap_too_many_zeros = 2 * total_ones

        for right, balance in enumerate(prefix):
            if right == 0:
                continue

            # Original balance is +2: swap an inside '1' with an outside '0'.
            answer = max(
                answer,
                self._best_with_cap(
                    positions[balance - 2],
                    right,
                    cap_too_many_ones,
                ),
            )

            # Original balance is -2: swap an inside '0' with an outside '1'.
            answer = max(
                answer,
                self._best_with_cap(
                    positions[balance + 2],
                    right,
                    cap_too_many_zeros,
                ),
            )

        return answer

    def _best_with_cap(self, starts: list[int], right: int, cap: int) -> int:
        if cap <= 0:
            return 0

        index = bisect_left(starts, right - cap)
        if index < len(starts) and starts[index] < right:
            return right - starts[index]
        return 0


# @lc code=end
