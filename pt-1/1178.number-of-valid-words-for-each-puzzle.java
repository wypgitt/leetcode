/*
 * @lc app=leetcode id=1178 lang=java
 *
 * [1178] Number Of Valid Words For Each Puzzle
 */

/*
 * --- Interview notes (bitmask, frequency map, submask enumeration, complexity, constraints, edges) ---
 *
 * Problem
 * For each puzzle string `p`, count words `w` such that:
 * (1) Every letter appearing in `w` also appears in `p` (letters of `w` form a subset of `p`’s letters — multiset of `w`
 *     uses only letters allowed by `p`).
 * (2) The word **contains the first letter of the puzzle** (`p[0]` must occur in `w`).
 *
 * Observations
 * • Order and multiplicity inside `w` do not matter for validity — only the **set** of distinct letters in `w`.
 * • `puzzles[i]` has length **7** and **no repeated characters** (seven distinct letters per puzzle).
 * • A word with more than **7** distinct letters can never satisfy (1) for any puzzle — safe to ignore when building counts.
 *
 * Bitmask encoding
 * Map `a..z` → bits `0..25`. For any string, mask = OR of `1 << (ord(c) - ord('a'))` over its characters (duplicates are
 * idempotent). Then “letters(w) ⊆ letters(p)” ↔ `(mask_w & ~mask_p) == 0` ↔ `mask_w` is a **submask** of `mask_p`.
 * “`w` contains `p[0]`” ↔ `mask_w` includes bit `f = 1 << (ord(p[0]) - ord('a'))` ↔ `(mask_w & f) == f`.
 * Together: valid words for puzzle `p` are exactly those whose masks equal `f | s` where `s` is any submask of
 * `(mask_p & ~f)` (choose any subset of the other six puzzle letters to accompany the mandatory first letter).
 *
 * Why not scan every word per puzzle?
 * Up to 10⁵ words × 10⁴ puzzles is too large. **Aggregate words once**, then answer each puzzle by summing over at most
 * **2⁶ = 64** candidate masks (subsets of six letters).
 *
 * Algorithm
 * 1. **Frequency map** `cnt[mask]` = number of words whose distinct-letter bitmask is `mask` (skip words with >7 bits set).
 * 2. For each puzzle with full mask `P` and first-letter bit `f`, let `rest = P & ~f` (other six letters).
 * 3. Enumerate every submask `sub` of `rest` (standard loop: start `sub = rest`, then `sub = (sub - 1) & rest` until `0`).
 *    Each valid word mask for this puzzle is `word_mask = sub | f`. Add `cnt[word_mask]` to the puzzle’s answer.
 *
 * Data structures
 * • **Counter / dict** from int bitmask → frequency — O(number of distinct word masks), ≤ number of words.
 * • Integer bit ops — no explicit graph; masks fit in one machine word.
 *
 * Time complexity
 * • Building masks and counts: **O(total characters in words)** ≈ O(W · L).
 * • Per puzzle: **O(2^k)** submasks where `k = popcount(rest) ≤ 6`, so **O(64)** worst case per puzzle.
 * • Total: **O(|words| chars + |puzzles| · 2⁶)** — dominated by scanning words for typical constraints.
 *
 * Space complexity
 * **O(U)** distinct word bitmasks stored (U ≤ min(words, 2²⁶ practical bucket); worst list size O(|words|)).
 *
 * Edge cases
 * • Words sharing the same letter set count together (`cnt[mask]` aggregates duplicates).
 * • Puzzle first letter must appear in word — enforced by OR-ing `f` into every enumerated candidate mask.
 * • No valid words → 0 for that puzzle (e.g. no word contains required first letter `g`).
 *
 * Tests (LeetCode examples)
 * Example 1: words `["aaaa","asas","able","ability","actt","actor","access"]`,
 * puzzles `["aboveyz","abrodyz","abslute","absoryz","actresz","gaswxyz"]` → `[1,1,3,2,4,0]`.
 * Example 2: `["apple","pleas","please"]` with five puzzles → `[0,1,3,2,0]`.
 *
 * Improvements / variants
 * • Replace `m.bit_count()` with `bin(m).count('1')` on Python before 3.10.
 * • If memory tight: stream words and update Counter without storing full word list twice.
 * • For extremely skewed data, defaultdict(int) instead of Counter is equivalent.
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Solution {

    private static int bitmask(String s) {
        int m = 0;
        for (int i = 0; i < s.length(); i++) {
            m |= 1 << (s.charAt(i) - 'a');
        }
        return m;
    }

    public List<Integer> findNumOfValidWords(String[] words, String[] puzzles) {
        Map<Integer, Integer> cnt = new HashMap<>();
        for (String w : words) {
            int m = bitmask(w);
            if (Integer.bitCount(m) > 7) {
                continue;
            }
            cnt.merge(m, 1, Integer::sum);
        }
        List<Integer> out = new ArrayList<>();
        for (String p : puzzles) {
            int full = bitmask(p);
            int fbit = 1 << (p.charAt(0) - 'a');
            int rest = full & ~fbit;
            int total = 0;
            int sub = rest;
            while (true) {
                total += cnt.getOrDefault(sub | fbit, 0);
                if (sub == 0) {
                    break;
                }
                sub = (sub - 1) & rest;
            }
            out.add(total);
        }
        return out;
    }
}
// @lc code=end
