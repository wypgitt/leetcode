/*
 * @lc app=leetcode id=1121 lang=java
 *
 * [1121] Divide Array Into Increasing Sequences
 */

/*
 * --- Interview notes (problem restatement, necessity of cnt·k ≤ n, counting, complexity, edges, tests) ---
 *
 * Problem
 * nums is sorted non-decreasing. Decide whether we can partition nums into disjoint subsequences (each preserves
 * relative order from nums), each subsequence strictly increasing, each of length >= k. (“Partition” here means
 * every element appears in exactly one subsequence.)
 *
 * Key observation — lower bound on how many subsequences we need
 * In a strictly increasing sequence, equal values cannot appear twice in the same subsequence. Therefore each
 * duplicate value must sit in a different subsequence at that value’s positions. If the maximum frequency of any
 * value is cnt, any valid construction uses at least cnt nonempty subsequences — call that minimum number m, so
 * m >= cnt. In fact we may assume exactly m = cnt subsequences when minimizing count (each frequent value forces a
 * distinct chain).
 *
 * Length accounting
 * If there are m subsequences and each has length at least k, the total number of elements is n >= m·k. Combining
 * with m >= cnt gives n >= cnt·k, i.e. cnt·k <= n.
 *
 * Sufficiency (why this inequality is enough)
 * With nums sorted, this necessary condition is also sufficient for the existence of such a partition (contest /
 * editorial fact). Interviews usually present the counting argument for necessity; remembering sufficiency as the
 * stated lemma finishes the one-line decision rule.
 *
 * Algorithm
 * Compute cnt = maximum run length of equal values in the sorted array (maximum frequency of any element).
 * Return cnt * k <= len(nums).
 *
 * Why not simulate greedy assignment
 * Unnecessary — the closed form avoids simulation and is easier to justify under time pressure.
 *
 * Time complexity
 * O(n) single scan.
 *
 * Space complexity
 * O(1) extra besides input (only counters).
 *
 * Edge cases
 * k == 1: always feasible (cnt * 1 <= n always).
 * All distinct: cnt == 1, condition becomes k <= n.
 *
 * Tests (statement)
 * nums = [1,2,2,3,3,4,4], k = 3 → cnt = 2, 2*3 <= 7 → True.
 * nums = [5,6,6,7,8], k = 3 → cnt = 2, 2*3 > 5 → False.
 *
 * Improvements
 * Early exit while scanning run lengths if current_run * k > n — optional micro-optimization (same asymptotics).
 *
 * --- end notes ---
 */

// @lc code=start
public class Solution {

    public boolean canDivideIntoSubsequences(int[] nums, int k) {
        int n = nums.length;
        int mx = 1;
        int run = 1;
        for (int i = 1; i < n; i++) {
            if (nums[i] == nums[i - 1]) {
                run++;
            } else {
                run = 1;
            }
            mx = Math.max(mx, run);
        }
        return mx * k <= n;
    }
}
// @lc code=end
