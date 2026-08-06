/*
 * @lc app=leetcode id=1147 lang=java
 *
 * [1147] Longest Chunked Palindrome Decomposition
 */

/*
 * --- Interview notes (greedy shells, proof idea, complexity, tests, DP variant, pitfalls) ---
 *
 * Problem
 * Split `text` into k non-empty consecutive chunks (sub1, ..., subk) with sub1+...+subk == text and sub_i == sub_{k-i+1}
 * for all i (chunk-level palindrome). Maximize k.
 *
 * Structural fact
 * The leftmost chunk must equal the rightmost chunk as strings (same length). After removing that symmetric pair, the
 * remaining middle must again be a chunked palindrome — same problem on a shorter string.
 *
 * Greedy choice (shortest valid outer shell)
 * At each step, among all lengths k with text[i : i+k] == text[j-k+1 : j+1] and non-overlapping chunks (k <= (j-i+1)//2),
 * take the smallest such k. Peel those two chunks (count +2), shrink [i, j], repeat. If no k works, the remainder is one
 * center chunk (count +1) and stop.
 *
 * Why smallest k is globally optimal (exchange argument)
 * Suppose an optimal decomposition’s outer pair has length L (same on both sides). Any feasible outer match has length k
 * where 1 <= k <= L and the equal prefix/suffix property holds. Taking k < L removes a thinner shell and leaves a longer
 * middle *without* invalidating optimality: the inner part of the optimal solution can be rearranged — formally, any
 * decomposition that starts with a thick L-shell can be refined by splitting that shell into k + (L-k) ... Actually the
 * standard proof for this problem shows that an optimal k-count can be achieved by repeatedly taking the shortest
 * matching boundary; taking a longer first shell cannot increase the final chunk count versus peeling the minimal shell
 * first (otherwise one could interchange layers). Empirically, this greedy matches the optimal DP that tries every k on
 * random small instances.
 *
 * Why cap k at floor(window_length / 2)
 * Left and right chunks must be disjoint. If i == j (single center character), max_k == 0 — no pairing — fall through to
 * +1 chunk. Prevents counting the center twice (e.g. "aaa" must give 3 chunks, not 4).
 *
 * Algorithm (two pointers)
 * i = 0, j = n-1, ans = 0. While i <= j:
 *   For k = 1, 2, ... up to max_k = (j-i+1)//2, stop at first k with equality → ans += 2, i += k, j -= k.
 *   If no k works → ans += 1; break.
 *
 * Data structures
 * Only integer indices into `text` — O(1) extra space (input string itself is not counted as extra).
 *
 * Time complexity
 * Each outer iteration tries increasing k and compares substrings; worst-case ~O(n^3) for pathological patterns with
 * naive slicing (LeetCode n <= 1000 is fine). Rolling hash can reduce comparisons to O(1) per k after prep, often cited as
 * O(n^2) or better in similar writeups.
 *
 * Space complexity
 * O(1) auxiliary for this iterative greedy.
 *
 * Edge cases
 * • Single character → 1 chunk.
 * • All equal characters → n chunks (each char separate).
 * • No prefix–suffix match on full string except trivial overlap cases → whole string one chunk (e.g. "merchant").
 *
 * Official examples (LeetCode)
 * • "ghiabcdefhelloadamhelloabcdefghi" → 7  (e.g. ghi | abcdef | hello | adam | hello | abcdef | ghi)
 * • "merchant" → 1
 * • "antaprezatepzapreanta" → 11  — note spelling: ends with ...pzapreanta, not ...pzapanta.
 *
 * Alternative formulation (DP — same optimal value)
 * dp(i, j) = max chunks for text[i:j+1]. Base: i>j → 0; i==j → 1. Else default 1 (whole interval one chunk). For each
 * k in [1, (j-i+1)//2] with matching prefix/suffix: dp(i,j) = max(dp(i,j), 2 + dp(i+k, j-k)). Optional cross-check vs greedy.
 *
 * Improvements
 * • Polynomial rolling hash (double hash) for O(1) substring equality checks.
 * • Precompute Z-function / suffix automaton rarely needed here; two-pointer + hash is the usual interview upgrade path.
 *
 * --- end notes ---
 */

// @lc code=start
public class Solution {

    public int longestDecomposition(String text) {
        int i = 0;
        int j = text.length() - 1;
        int ans = 0;
        while (i <= j) {
            int maxK = (j - i + 1) / 2;
            boolean matched = false;
            for (int k = 1; k <= maxK; k++) {
                if (text.substring(i, i + k).equals(text.substring(j - k + 1, j + 1))) {
                    ans += 2;
                    i += k;
                    j -= k;
                    matched = true;
                    break;
                }
            }
            if (!matched) {
                ans += 1;
                break;
            }
        }
        return ans;
    }
}
// @lc code=end
