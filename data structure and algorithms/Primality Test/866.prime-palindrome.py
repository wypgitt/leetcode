#
# @lc app=leetcode id=866 lang=python3
#
# [866] Prime Palindrome
#

# =============================================================================
# INTERVIEW: ELEVATOR PITCH (~30 seconds)
# =============================================================================
#
# "We need the smallest prime ≥ n that is a palindrome. Scanning every integer is
# slow; instead generate **only palindromes** in increasing order by length. A classic
# number-theory fact: every **even-length** palindrome (except 11) is divisible by **11**,
# so no even-digit prime palindrome beyond 11 — we generate **odd-length** palindromes
# by mirroring a left half. Trial divide for primality on each candidate — digit count
# stays small under problem bounds."
#
# =============================================================================
# PROBLEM (PRECISE)
# =============================================================================
#
# Given integer **`n`**, return the **smallest** integer **`x ≥ n`** such that **`x`** is
# both **prime** and a **decimal palindrome** (reads same forwards/backwards).
#
# =============================================================================
# WHY NOT BRUTE-FORCE `x = n, n+1, …` FOR LARGE `n`
# =============================================================================
#
# Primality + palindrome check per integer is cheap, but **gaps** between palindromes
# grow quickly — worst-case attempts approach **`10⁸`** regime from constraints. Generating
# palindromes **directly** skips almost all integers.
#
# =============================================================================
# STRUCTURAL FACT — EVEN-LENGTH PALINDROMES AND 11 (EXCEPT 11)
# =============================================================================
#
# Write a **`2k`-digit** palindrome **`P`** in decimal. Alternating-sum divisibility rule
# for **11** implies **`11 | P`** for **`k ≥ 2`** (standard digit-pattern proof). So **no**
# prime palindrome has **even** length **≥ 4**. The only **even-length** prime palindrome
# is **`11`** (handled as a **small case**).
#
# Therefore for **`n > 11`**, candidates may be restricted to **odd** digit lengths **≥ 3**
# (and single-digit primes already covered by early returns if **`n` ≤ 7**).
#
# =============================================================================
# GENERATING ODD-LENGTH PALINDROMES
# =============================================================================
#
# An odd-length palindrome is determined by its **first `(L+1)//2` digits** — call that
# string **`s`**. The full palindrome is:
#
#       **`int(s + s[:-1][::-1])`**
#
# Example: **`s = "123"`** → **`"123" + "21"`** = **`"12321"`**.
#
# For fixed **`L`** odd, iterate **`s`** numerically from **`10^{(L-1)/2}`** to **`10^{(L+1)/2}-1`**
# (all valid left halves of length **`(L+1)//2`**).
#
# =============================================================================
# PRIMALITY — TRIAL DIVISION
# =============================================================================
#
# For integers up to about **`10⁹`**, trial division up to **`√x`** with **2** then odd
# steps is sufficient here (constraints modest). **Miller–Rabin** is optional overhead
# unless ranges explode.
#
# =============================================================================
# DATA STRUCTURES
# =============================================================================
#
# **Scalars and strings only** — no graphs, heaps, or arrays besides loop counters.
# Building **`s`** as string avoids manual digit reversal arithmetic bugs.
#
# =============================================================================
# TIME & SPACE COMPLEXITY
# =============================================================================
#
# Let **`P`** be the number of palindromes tried until the answer (problem-dependent).
# Each candidate: **`O(√x)`** trial division, **`O(1)`** extra space aside from **`√x`**
# iteration.
#
# Palindromes generated grow slowly vs scanning all integers — overall comfortably within
# limits for **`n ≤ 10⁸`** style bounds.
#
# =============================================================================
# EDGE CASES
# =============================================================================
#
# • **`n ≤ 2`** → **`2`** (only even prime).
# • **`n ∈ {3,4,5}`** → **`5`** or **`7`** per chain.
# • **`n ∈ {6,7,8,9,10}`** → **`7`** or **`11`** as applicable.
# • **`n = 11`** → **`11`**.
# • **`n > 11`** → search odd-length palindromes only ( **`11`** already excluded by **`n`** ).
#
# =============================================================================
# TESTING (SANITY)
# =============================================================================
#
# • **`n = 6`** → **`7`**.
# • **`n = 12` or `13`** → **`101`** (first prime palindrome **`≥ 12`** is **`101`**).
# • **`n = 998`** → **`10301`** (scan jumps past non-prime **`999`**, even-length palindromes
#   divisible by **`11`**, etc.).
# • Cross-check: brute scan small **`n`** with naive prime test for **`n ≤ 10⁴`**.
#
# =============================================================================
# IMPROVEMENTS / VARIANTS
# =============================================================================
#
# • **Next-permutation style** palindrome walk — rarely needed.
# • **Sieve** precomputation — only wins if many queries; single **`n`** here.
#
# =============================================================================

# @lc code=start
class Solution:
    def primePalindrome(self, n: int) -> int:
        """
        Smallest prime palindrome >= n.

        Small primes handled explicitly. For n > 11, only odd-length palindromes are
        candidates (even-length palindromes with >= 4 digits are divisible by 11).
        """

        def is_prime(x: int) -> bool:
            if x < 2:
                return False
            if x % 2 == 0:
                return x == 2
            limit = int(x**0.5) + 1
            for d in range(3, limit, 2):
                if x % d == 0:
                    return False
            return True

        if n <= 2:
            return 2
        if n <= 3:
            return 3
        if n <= 5:
            return 5
        if n <= 7:
            return 7
        if n <= 11:
            return 11

        # Odd total length L only (even-length palindromes with L >= 4 are multiples of 11).
        L = len(str(n))
        if L % 2 == 0:
            L += 1

        while True:
            half_lo = 10 ** ((L - 1) // 2)
            half_hi = 10 ** ((L + 1) // 2)
            for half in range(half_lo, half_hi):
                s = str(half)
                cand = int(s + s[:-1][::-1])
                if cand >= n and is_prime(cand):
                    return cand
            L += 2


# @lc code=end
