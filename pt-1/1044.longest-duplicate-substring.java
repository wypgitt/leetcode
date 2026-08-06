/*
 * @lc app=leetcode id=1044 lang=java
 *
 * [1044] Longest Duplicate Substring
 */

/*
 * --- Interview notes (objective, binary search + Rabin–Karp, collision, complexity, edges, tests) ---
 *
 * Problem
 * Given lowercase string s, find any substring that appears at least twice (overlaps allowed) with maximum
 * length. Return "" if none exists for positive length.
 *
 * Why not enumerate all O(n^2) substrings
 * n up to 3e4 → Ω(n^2) substrings — too slow to scan explicitly.
 *
 * Monotonicity ⇒ binary search on length L
 * If some substring of length L appears twice, then some substring of length L−1 also appears twice (take the
 * same occurrence and shorten by one character — actually careful: duplicate for L implies duplicate for any
 * smaller length exists inside those occurrences — standard argument). Thus feasibility of length L is monotone
 * in L: we binary-search the maximum L such that a duplicate of length L exists.
 *
 * Decision problem check(L)
 * “Does there exist a length-L substring that occurs ≥ 2 times?” Scan all length-L windows in O(n), comparing
 * windows naively is O(L) each → O(nL) per check → too slow inside binary search.
 *
 * Rolling hash (Rabin–Karp)
 * Map each length-L window to a polynomial hash in O(1) amortized using prefix hashes:
 *   H[k] = hash of s[0:k), P[k] = BASE^k mod M.
 *   subhash(i, L) = H[i+L] − H[i]·P[L]  (mod M).
 * Store seen hashes in a hash set; collision ⇒ duplicate candidate — verify with optional extra modulus.
 *
 * Double hashing
 * Two coprime moduli M1, M2 (and fixed BASE) reduce collision probability to negligible for contest constraints;
 * store pairs (h1, h2). Rare false positives could be eliminated by storing indices + strcmp — rarely coded on LC.
 *
 * Alternative algorithms (mention only)
 * - Suffix array + LCP → O(n log n) or O(n); heavier to implement in interview.
 * - Suffix automaton — powerful but niche in timed interviews.
 *
 * Time complexity
 * Build prefixes O(n). Binary search O(log n) iterations × check O(n) → O(n log n).
 *
 * Space complexity
 * O(n) for prefix/pow arrays + O(n) window hashes worst-case in a check (actually set holds up to n entries).
 *
 * Edge cases
 * - No duplicate character: answer "".
 * - Entire string repeated pattern: answer approaches n−1 max duplicate length (e.g., "aaaa" → "aaa").
 *
 * Tests (statement)
 * "banana" → "ana" (any longest dup acceptable).
 * "abcd" → "".
 *
 * Improvements
 * - Randomized base + mod (Miller-style) or 64-bit modulo 2^61−1 with fast mul trick for fewer collisions / speed.
 * - On collision of hashes, compare substring bytes once — deterministic correctness.
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.HashMap;
import java.util.Map;

public class Solution {

    public String longestDupSubstring(String s) {
        int n = s.length();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) {
            nums[i] = s.charAt(i) - 'a';
        }
        int base = 131;
        long m1 = 1_000_000_007L;
        long m2 = 1_000_000_009L;

        long[] pow1 = new long[n + 1];
        long[] pow2 = new long[n + 1];
        long[] pref1 = new long[n + 1];
        long[] pref2 = new long[n + 1];
        pow1[0] = 1;
        pow2[0] = 1;
        for (int i = 0; i < n; i++) {
            pow1[i + 1] = pow1[i] * base % m1;
            pow2[i + 1] = pow2[i] * base % m2;
            pref1[i + 1] = (pref1[i] * base + nums[i]) % m1;
            pref2[i + 1] = (pref2[i] * base + nums[i]) % m2;
        }

        int lo = 0;
        int hi = n;
        String best = "";
        while (lo < hi) {
            int mid = (lo + hi + 1) / 2;
            String cand = existsDuplicate(s, n, mid, pref1, pref2, pow1, pow2, m1, m2);
            if (!cand.isEmpty()) {
                lo = mid;
                best = cand;
            } else {
                hi = mid - 1;
            }
        }
        return best;
    }

    private String existsDuplicate(
            String s,
            int n,
            int length,
            long[] pref1,
            long[] pref2,
            long[] pow1,
            long[] pow2,
            long m1,
            long m2) {
        if (length == 0) {
            return "";
        }
        Map<Long, Integer> seen = new HashMap<>();
        for (int i = 0; i <= n - length; i++) {
            long h1 = (pref1[i + length] - pref1[i] * pow1[length] % m1 + m1) % m1;
            long h2 = (pref2[i + length] - pref2[i] * pow2[length] % m2 + m2) % m2;
            long key = h1 << 32 | (h2 & 0xffffffffL);
            if (seen.containsKey(key)) {
                return s.substring(i, i + length);
            }
            seen.put(key, i);
        }
        return "";
    }
}
// @lc code=end
