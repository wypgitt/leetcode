#
# @lc app=leetcode id=3869 lang=python3
#
# [3869] Count Fancy Numbers in a Range
#

# @lc code=start
class Solution:
    pass


# @lc code=end

#
# @lc app=leetcode id=3869 lang=python3
#
# [3869] Count Fancy Numbers in a Range
#
# --- Notes (definitions, digit-sum check shortcut, digit DP, complexity, interview) ---
#
# Definitions
# GOOD integer: decimal digits are STRICTLY increasing OR STRICTLY decreasing (single-digit
# counts as good). Example: 10 is good (1>0); 11 is not (equal digits).
# FANCY integer: GOOD, OR the SUM OF DIGITS (once, no recursion in statement) is good.
# Count fancy numbers in [l, r] inclusive.
#
# Range answer trick
# Let F(x) = count of fancy numbers in [0, x]. Answer = F(r) - F(l - 1).
#
# check(s) — is nonnegative integer s "good" as a decimal number?
# Used when the full number is NOT good (strict monotonicity broken, state st == 3) but we
# still need to know if DIGIT SUM s is good to mark fancy.
# - For s < 100: two-digit "bad" pattern is repeated digits 11, 22, ..., 99, i.e. multiples of
#   11 with two digits (and 0). Single digits pass. So s % 11 != 0 matches the editorial test.
# - For s >= 100: digit sums coming from up to 16 nines are bounded (~144); the solution uses
#   the simplified predicate in the statement code: strict increase on the last two decimal
#   digits of s (contest algebra); keep the same logic as official solutions.
#
# Digit DP state (process bound string num from high to low)
# dfs(pos, s, prev, st, lim):
#   pos   — index in num.
#   s     — running digit sum of the number being built.
#   prev  — previous digit placed (0 for leading-zero phase).
#   st    — monotonicity of the decimal string so far:
#           0 = only leading zeros / compatible prefix (see transitions),
#           1 = strict increase chain,
#           2 = strict decrease chain,
#           3 = already impossible to be strictly monotone.
#   lim   — tight to upper bound num (standard digit DP).
# Terminal: if st != 3, the number itself is good -> count 1. If st == 3, fancy iff check(s).
#
# Leading zeros: prev == 0 and st == 0 allow leading zeros until first nonzero digit; transitions
# match the official implementation.
#
# Caching: @cache on dfs MUST be cleared when switching bound string (l-1 vs r) because num is
# read from closure and is not part of the memo key.
#
# Time complexity
# O(states * 10) per bound with memo; digit positions O(log10 r), sum s up to 9 * digits,
# prev in 0..9, st in 0..3 — polynomial in digit count; effectively ~O(D * S * 10) with small D.
#
# Space complexity
# Memo table proportional to reachable states for one bound.
#
# Edge cases
# l = 1: use F(r) - F(0). String "0" works with DP for zero.
# Single-element range: still two F evaluations.
#
# Tests (examples)
# [8,10] -> 3; [12340,12341] -> 1; singleton non-fancy -> 0.
#
# Possible improvements
# - Iterative DP table instead of recursion; same states.
# - Explicit memo dimensions instead of cache_clear if you pass num as tuple key (larger memory).
# --- end notes ---

# @lc code=start
from functools import cache


class Solution:
    def countFancy(self, l: int, r: int) -> int:
        num = ""

        def check(s: int) -> bool:
            if s < 100:
                return s % 11 != 0
            return 1 < s // 10 % 10 < s % 10

        @cache
        def dfs(pos: int, s: int, prev: int, st: int, lim: bool) -> int:
            if pos >= len(num):
                if st != 3:
                    return 1
                return int(check(s))
            up = int(num[pos]) if lim else 9
            res = 0
            for i in range(up + 1):
                nxt_st = st
                if st == 0:
                    if prev == 0:
                        nxt_st = 0
                    elif i > prev:
                        nxt_st = 1
                    elif i < prev:
                        nxt_st = 2
                    else:
                        nxt_st = 3
                elif st == 1:
                    if i > prev:
                        nxt_st = 1
                    else:
                        nxt_st = 3
                elif st == 2:
                    if i < prev:
                        nxt_st = 2
                    else:
                        nxt_st = 3
                else:
                    nxt_st = 3
                res += dfs(pos + 1, s + i, i, nxt_st, lim and i == up)
            return res

        def calc(x: int) -> int:
            nonlocal num
            num = str(x)
            dfs.cache_clear()
            return dfs(0, 0, 0, 0, True)

        return calc(r) - calc(l - 1)


# @lc code=end
