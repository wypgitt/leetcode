#
# @lc app=leetcode id=1044 lang=python3
#
# [1044] Longest Duplicate Substring
#

# --- Interview notes (objective, binary search + Rabin–Karp, collision, complexity, edges, tests) ---
#
# Problem
# Given lowercase string s, find any substring that appears at least twice (overlaps allowed) with maximum
# length. Return "" if none exists for positive length.
#
# Why not enumerate all O(n^2) substrings
# n up to 3e4 → Ω(n^2) substrings — too slow to scan explicitly.
#
# Monotonicity ⇒ binary search on length L
# If some substring of length L appears twice, then some substring of length L−1 also appears twice (take the
# same occurrence and shorten by one character — actually careful: duplicate for L implies duplicate for any
# smaller length exists inside those occurrences — standard argument). Thus feasibility of length L is monotone
# in L: we binary-search the maximum L such that a duplicate of length L exists.
#
# Decision problem check(L)
# “Does there exist a length-L substring that occurs ≥ 2 times?” Scan all length-L windows in O(n), comparing
# windows naively is O(L) each → O(nL) per check → too slow inside binary search.
#
# Rolling hash (Rabin–Karp)
# Map each length-L window to a polynomial hash in O(1) amortized using prefix hashes:
#   H[k] = hash of s[0:k), P[k] = BASE^k mod M.
#   subhash(i, L) = H[i+L] − H[i]·P[L]  (mod M).
# Store seen hashes in a hash set; collision ⇒ duplicate candidate — verify with optional extra modulus.
#
# Double hashing
# Two coprime moduli M1, M2 (and fixed BASE) reduce collision probability to negligible for contest constraints;
# store pairs (h1, h2). Rare false positives could be eliminated by storing indices + strcmp — rarely coded on LC.
#
# Alternative algorithms (mention only)
# - Suffix array + LCP → O(n log n) or O(n); heavier to implement in interview.
# - Suffix automaton — powerful but niche in timed interviews.
#
# Time complexity
# Build prefixes O(n). Binary search O(log n) iterations × check O(n) → O(n log n).
#
# Space complexity
# O(n) for prefix/pow arrays + O(n) window hashes worst-case in a check (actually set holds up to n entries).
#
# Edge cases
# - No duplicate character: answer "".
# - Entire string repeated pattern: answer approaches n−1 max duplicate length (e.g., "aaaa" → "aaa").
#
# Tests (statement)
# "banana" → "ana" (any longest dup acceptable).
# "abcd" → "".
#
# Improvements
# - Randomized base + mod (Miller-style) or 64-bit modulo 2^61−1 with fast mul trick for fewer collisions / speed.
# - On collision of hashes, compare substring bytes once — deterministic correctness.
#
# --- end notes ---

# @lc code=start
class Solution:
    def longestDupSubstring(self, s: str) -> str:
        n = len(s)
        nums = [ord(c) - 97 for c in s]
        base = 131
        m1 = 10**9 + 7
        m2 = 10**9 + 9

        pow1 = [1] * (n + 1)
        pow2 = [1] * (n + 1)
        pref1 = [0] * (n + 1)
        pref2 = [0] * (n + 1)
        for i in range(n):
            pow1[i + 1] = pow1[i] * base % m1
            pow2[i + 1] = pow2[i] * base % m2
            pref1[i + 1] = (pref1[i] * base + nums[i]) % m1
            pref2[i + 1] = (pref2[i] * base + nums[i]) % m2

        def sub_hash(i: int, length: int):
            h1 = (pref1[i + length] - pref1[i] * pow1[length]) % m1
            h2 = (pref2[i + length] - pref2[i] * pow2[length]) % m2
            return (h1, h2)

        def exists_duplicate(length: int) -> str:
            if length == 0:
                return ""
            seen = set()
            for i in range(n - length + 1):
                key = sub_hash(i, length)
                if key in seen:
                    return s[i : i + length]
                seen.add(key)
            return ""

        lo, hi = 0, n
        best = ""
        while lo < hi:
            mid = (lo + hi + 1) // 2
            cand = exists_duplicate(mid)
            if cand:
                lo = mid
                best = cand
            else:
                hi = mid - 1
        return best


# @lc code=end
