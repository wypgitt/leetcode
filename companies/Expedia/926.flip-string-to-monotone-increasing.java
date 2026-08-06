/*
 * @lc app=leetcode id=926 lang=java
 *
 * [926] Flip String To Monotone Increasing
 */

/*
 * --- Interview notes (split point, prefix/suffix costs, one pass, DP variant, complexity) ---
 *
 * Problem
 * Binary string s. Minimum flips so string becomes monotone increasing: some zeros then some ones (0*1*).
 *
 * Structural observation — choose a split k: [0,k) all '0', [k,n) all '1'.
 * cost(k) = ones in prefix [0,k) + zeros in suffix [k,n).
 * Answer = min over k.
 *
 * Algorithm: O(n), O(1) space — maintain ones_prefix and zeros_suffix while scanning k.
 *
 * Time O(n), Space O(1).
 *
 * --- end notes ---
 */

// @lc code=start
class Solution {
    public int minFlipsMonoIncr(String s) {
        int onesPrefix = 0;
        int zerosSuffix = 0;
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) == '0') {
                zerosSuffix++;
            }
        }
        int best = Integer.MAX_VALUE;
        int n = s.length();
        for (int k = 0; k <= n; k++) {
            best = Math.min(best, onesPrefix + zerosSuffix);
            if (k < n) {
                if (s.charAt(k) == '1') {
                    onesPrefix++;
                } else {
                    zerosSuffix--;
                }
            }
        }
        return best;
    }
}
// @lc code=end
