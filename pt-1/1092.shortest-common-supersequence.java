/*
 * @lc app=leetcode id=1092 lang=java
 *
 * [1092] Shortest Common Supersequence
 */

/*
 * --- Interview notes (SCS length, LCS DP, backtracking, complexity, edges, tests) ---
 *
 * Problem
 * Return any shortest string T such that str1 and str2 are both subsequences of T.
 *
 * Length formula
 * |SCS(str1, str2)| = |str1| + |str2| − |LCS(str1, str2)|.
 * Reason: start with str1 and str2 concatenated; each character that belongs to a common subsequence was counted
 * twice but should appear once — merging along one longest common subsequence removes exactly |LCS| duplicates.
 *
 * Why compute LCS length first
 * The LCS dynamic-programming table encodes *which* matches are aligned; backtracking from (m, n) to (0, 0)
 * following that table emits characters in an order that realizes one shortest supersequence.
 *
 * LCS DP
 * f[i][j] = LCS length of prefixes str1[:i] and str2[:j].
 *   If str1[i−1] == str2[j−1]: f[i][j] = f[i−1][j−1] + 1.
 *   Else: f[i][j] = max(f[i−1][j], f[i][j−1]).
 *
 * Reconstructing one SCS (walk from (m, n))
 * Think of tracing an optimal path that builds T from right to left (we append to a list then reverse).
 * • If one prefix is exhausted, append the rest of the other string (only one choice).
 * • Otherwise compare f[i][j] with f[i−1][j] and f[i][j−1]:
 *   – If f[i][j] == f[i−1][j]: an optimal LCS alignment does not match str1[i−1] at column j; emit str1[i−1] now and
 *     move to (i−1, j) — that character must still appear in T but is not part of the match at this column.
 *   – Else if f[i][j] == f[i][j−1]: symmetric, emit str2[j−1], move to (i, j−1).
 *   – Else: characters match (diagonal step in LCS); emit that character once and move to (i−1, j−1).
 * When f[i−1][j] == f[i][j−1] (tie), either branch yields a valid shortest supersequence — picking the first rule
 * preserves determinism.
 *
 * Data structures
 * 2D table f with (m+1)×(n+1) ints — fits constraints (≤1001 × 1001).
 * Output built as list of chars then reversed join — O(|str1|+|str2|) characters.
 *
 * Time complexity
 * O(m · n) for DP + O(m + n) backtrack.
 *
 * Space complexity
 * O(m · n) for the table (can be reduced to O(min(m,n)) for LCS length only, but then extra parent bookkeeping is
 * needed to reconstruct — full table is simpler to explain in interviews).
 *
 * Edge cases
 * Identical strings: output equals either string.
 * No common characters: T is str1 + str2 in an order consistent with the walk (effectively interleaving as forced
 * by LCS = 0).
 *
 * Tests (statement)
 * str1 = "abac", str2 = "cab" → one answer is "cabac".
 * str1 = str2 = "aaaaaaaa" → "aaaaaaaa".
 *
 * Improvements
 * - Hirschberg’s algorithm can recover LCS / SCS in O(m·n) time and O(min(m,n)) space — heavier implementation.
 *
 * --- end notes ---
 */

// @lc code=start
public class Solution {

    public String shortestCommonSupersequence(String str1, String str2) {
        int m = str1.length();
        int n = str2.length();
        int[][] f = new int[m + 1][n + 1];
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (str1.charAt(i - 1) == str2.charAt(j - 1)) {
                    f[i][j] = f[i - 1][j - 1] + 1;
                } else {
                    f[i][j] = Math.max(f[i - 1][j], f[i][j - 1]);
                }
            }
        }
        StringBuilder ans = new StringBuilder();
        int i = m;
        int j = n;
        while (i > 0 || j > 0) {
            if (i == 0) {
                j--;
                ans.append(str2.charAt(j));
            } else if (j == 0) {
                i--;
                ans.append(str1.charAt(i));
            } else {
                if (f[i][j] == f[i - 1][j]) {
                    i--;
                    ans.append(str1.charAt(i));
                } else if (f[i][j] == f[i][j - 1]) {
                    j--;
                    ans.append(str2.charAt(j));
                } else {
                    i--;
                    j--;
                    ans.append(str1.charAt(i));
                }
            }
        }
        return ans.reverse().toString();
    }
}
// @lc code=end
