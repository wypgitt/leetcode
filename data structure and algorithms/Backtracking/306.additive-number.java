/*
 * @lc app=leetcode id=306 lang=java
 *
 * [306] Additive Number
 */

/*
 * =============================================================================
 * INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
 * =============================================================================
 *
 * 30 seconds:
 *   "Split the digit string into a Fibonacci-like sequence: after the first two
 *   numbers, each segment must equal the sum of the previous two. I try every
 *   valid split for the first two numbers; once chosen, the rest of the string
 *   is forced — greedily match each next sum left-to-right. Leading zeros are
 *   illegal except for the single digit '0'."
 *
 * 2–4 minutes:
 *   - Brute structure: backtracking could branch heavily; key observation is that
 *     after fixing n1 and n2, every later term is uniquely determined (must equal
 *     n_{k-2}+n_{k-1}), so we only branch on where the first two numbers end.
 *   - Loop split positions: first number num[0:i], second num[i:j]; both must be
 *     valid numeric segments (no multi-digit token starting with '0').
 *   - From position j, repeatedly expect next = add(prev2, prev1) as a decimal
 *     string prefix of the remainder; advance pointer by len(next). Success iff we
 *     consume the whole string and extended beyond j (≥ 3 numbers total).
 *   - Arithmetic: use Python int (arbitrary precision). In languages with 64-bit
 *     limits, use BigInteger or implement schoolbook string addition.
 *
 * =============================================================================
 * ALGORITHM
 * =============================================================================
 *
 * For each i in [1, n-2] (length of first number) and j in [i+1, n-1] (end of
 * second number exclusive):
 *   a = num[0:i], b = num[i:j]
 *   If invalid segment(s), continue.
 *   k = j; x, y = a, b
 *   While k < n:
 *       z = decimal string for int(x) + int(y)   # next Fibonacci term
 *       If num does not have prefix z at k, break.
 *       k += len(z); x, y = y, z
 *   If k == n and k > j, return True   # used at least one term after b
 * Return False
 *
 * =============================================================================
 * DATA STRUCTURES
 * =============================================================================
 *
 * - Only indices into `num` and a few string slices; no auxiliary containers.
 * - Optional: cache int(x) if profiling; not required for LC sizes.
 *
 * =============================================================================
 * COMPLEXITY
 * =============================================================================
 *
 * Let L = len(num). Try O(L^2) pairs (i, j). Verification is O(L) per pair in
 * the worst case (linear scan with possibly growing digit lengths).
 * Overall time O(L^3); space O(L) for slices / recursion stack if any (here O(1)
 * extra besides input).
 *
 * =============================================================================
 * EDGE CASES
 * =============================================================================
 *
 * - Length < 3: cannot form three numbers → False.
 * - Leading zeros: "01", "001" as a segment invalid unless the segment is exactly
 *   "0".
 * - "000": valid as 0 + 0 = 0 (three numbers).
 * - "111": no valid additive split → False.
 * - Large integers: Python int OK; mention BigInteger in Java-style interviews.
 *
 * =============================================================================
 * TESTING
 * =============================================================================
 *
 * Known cases:
 *   - "112358" → True (classic Fibonacci digits).
 *   - "199100199" → True (1, 99, 100, 199).
 *   - "1023" → False.
 * Property: if True, simulate parsing and verify each sum from prior two.
 *
 * =============================================================================
 */

// @lc code=start
import java.math.BigInteger;

class Solution {
    /**
     * Return true iff `num` can be split into ≥ 3 parts forming an additive
     * sequence (Fibonacci-like), with no illegal leading zeros on segments.
     */
    public boolean isAdditiveNumber(String num) {
        int n = num.length();
        if (n < 3) {
            return false;
        }

        for (int i = 1; i < n - 1; i++) {
            for (int j = i + 1; j < n; j++) {
                String first = num.substring(0, i);
                String second = num.substring(i, j);
                if (!validSegment(first) || !validSegment(second)) {
                    continue;
                }

                int k = j;
                String x = first;
                String y = second;
                while (k < n) {
                    String nxt = new BigInteger(x).add(new BigInteger(y)).toString();
                    if (k + nxt.length() > n || !num.startsWith(nxt, k)) {
                        break;
                    }
                    k += nxt.length();
                    x = y;
                    y = nxt;
                }

                if (k == n && k > j) {
                    return true;
                }
            }
        }
        return false;
    }

    private static boolean validSegment(String s) {
        return s.length() > 0 && (s.length() == 1 || s.charAt(0) != '0');
    }
}
// @lc code=end
