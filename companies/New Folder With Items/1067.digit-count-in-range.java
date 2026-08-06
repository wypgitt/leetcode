/*
 * @lc app=leetcode id=1067 lang=java
 *
 * [1067] Digit Count in Range
 */

/*
 * --- Interview notes (range reduction, digit DP state machine, leading zeros, complexity, edges, tests) ---
 *
 * Problem
 * Given digit d ∈ [0,9] and integers low ≤ high, count how many times digit d appears in the decimal writing of
 * all integers x with low ≤ x ≤ high (count multiplicity per integer, e.g. 11 contributes two 1’s).
 *
 * Range reduction
 * Let F(N) = total occurrences of digit d in all integers x with 0 ≤ x ≤ N (decimal, no leading zeros except the
 * number 0 itself handled via leading-zero mechanics).
 * Answer = F(high) − F(low − 1).
 *
 * Why digit DP instead of iterating [low, high]
 * high − low can be ~2·10^8 — scanning every integer is too slow.
 *
 * Digit DP model (count occurrences, not count numbers)
 * Decompose N into digits a[1..L] with a[1] = least significant digit (editorial indexing). DFS processes from
 * position L down to 1 (most significant → least).
 * State:
 *   pos   — next digit position to fix.
 *   cnt   — how many copies of digit d have been placed so far on this path.
 *   lead  — still placing leading zeros before the number truly starts (important when d = 0).
 *   limit — tight to prefix of N (cannot exceed N).
 * Transition: try digit i ∈ [0, up] where up = a[pos] if limit else 9.
 *   • If i == 0 and lead: still “no real digit yet” → recurse with lead True (still flexible), cnt unchanged.
 *   • Else the number has started; count += 1 if i == d; lead becomes False.
 * Base pos ≤ 0: return cnt.
 *
 * Memoization
 * Python functools.cache on dfs; states bounded by pos ≤ 10, cnt ≤ 10, booleans — tiny graph.
 * (Java editorial memoizes only when ¬lead ∧ ¬limit for speed; cache-all is fine here.)
 *
 * Special role of digit 0
 * Leading zeros before the first non-zero digit must not be counted as occurrences of ‘0’ (otherwise every
 * shorter-length padding would inflate zeros). The lead flag suppresses those.
 *
 * Time complexity
 * O(log10 N) positions × O(10) digit choices × memo hits → effectively O(log N) per F(N), two calls total.
 *
 * Space complexity
 * O(log N) recursion depth + memo table negligible.
 *
 * Alternative (mention only)
 * Closed-form digit enumeration (“rotate factor” method from CS interviews) counts occurrences in O(log N)
 * without recursion — useful when memo limits matter; digit DP is easier to derive under pressure.
 *
 * Edge cases
 * low = 1 ⇒ low − 1 = 0 ⇒ F(0) = 0 with our extraction loop (no digits → dfs returns 0 immediately).
 * d = 0 needs correct leading-zero handling (validated via brute tests).
 *
 * Tests (statement)
 * d = 1, low = 1, high = 13 → 6.
 * d = 3, low = 100, high = 250 → 35.
 *
 * Improvements
 * - Iterative DP table instead of recursion if stack depth ever matters (not here).
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.Arrays;

public class Solution {

    private int d;
    private int[] digits;
    private int[][][][] memo;

    public int digitsCount(int d, int low, int high) {
        this.d = d;
        return upto(high) - upto(low - 1);
    }

    private int upto(int n) {
        if (n < 0) {
            return 0;
        }
        int[] a = new int[12];
        int l = 0;
        int t = n;
        while (t > 0) {
            l++;
            a[l] = t % 10;
            t /= 10;
        }
        this.digits = a;
        memo = new int[12][12][2][2];
        for (int i = 0; i < 12; i++) {
            for (int j = 0; j < 12; j++) {
                for (int k = 0; k < 2; k++) {
                    Arrays.fill(memo[i][j][k], -1);
                }
            }
        }
        return dfs(l, 0, 1, 1);
    }

    private int dfs(int pos, int cnt, int lead, int limit) {
        if (pos <= 0) {
            return cnt;
        }
        if (memo[pos][cnt][lead][limit] != -1) {
            return memo[pos][cnt][lead][limit];
        }
        int up = limit == 1 ? digits[pos] : 9;
        int total = 0;
        for (int i = 0; i <= up; i++) {
            if (i == 0 && lead == 1) {
                total += dfs(pos - 1, cnt, 1, limit == 1 && i == up ? 1 : 0);
            } else {
                total +=
                        dfs(
                                pos - 1,
                                cnt + (i == d ? 1 : 0),
                                0,
                                limit == 1 && i == up ? 1 : 0);
            }
        }
        memo[pos][cnt][lead][limit] = total;
        return total;
    }
}
// @lc code=end
