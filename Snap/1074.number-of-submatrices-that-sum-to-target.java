/*
 * @lc app=leetcode id=1074 lang=java
 *
 * [1074] Number of Submatrices That Sum to Target
 */

/*
 * --- Interview notes (2D→1D, prefix sum + map, complexity, edges, tests) ---
 *
 * Problem
 * Count submatrices (contiguous rows and columns) whose element sum equals target. Overlapping / different
 * positions count separately.
 *
 * Key idea — compress a vertical band to one row
 * Fix a top row index i and a bottom row index j (i <= j). For each column c, let
 *   col[c] = sum of matrix[t][c] for t in [i, j].
 * Any submatrix that uses exactly rows i..j and columns a..b has total sum
 *   col[a] + col[a+1] + ... + col[b].
 * So for fixed (i, j) the 2D problem becomes: number of subarrays of the 1D array col whose sum is target.
 *
 * Subproblem — subarray sum = target (LeetCode 560 style)
 * For array nums, use prefix sums S[0]=0, S[k]= nums[0]+...+nums[k-1]. Subarray nums[p..k-1] sums to target iff
 *   S[k] - S[p] = target  ⟺  S[p] = S[k] - target.
 * Scan k from 1 to n with running sum s = S[k]: add to answer the number of earlier indices with prefix sum
 * s - target. A hash map stores frequency of each prefix sum seen so far; initialize count[0] = 1.
 *
 * Why a hash map
 * O(1) average update and lookup of how many times a needed prefix sum has appeared.
 *
 * Full algorithm
 * ans = 0
 * for each top row i:
 *   col = [0] * n
 *   for bottom row j from i to m-1:
 *       col[k] += matrix[j][k]  for all k
 *       ans += subarray_count(col, target)
 * return ans
 *
 * Time complexity
 * O(m^2 * n) where m = rows, n = cols: O(m^2) pairs (i, j) and each 1D pass is O(n) with hash map.
 * With m, n <= 100 → ~10^8 worst-case operations acceptable in Python with tight constants.
 *
 * Space complexity
 * O(n) for col plus O(distinct prefix sums) for the map — O(n) typical worst-case storage per inner loop.
 *
 * Edge cases
 * Negative numbers allowed — prefix sums are not monotone; hash-map approach still works (no two-pointer shortcut).
 * Single cell matrix — one iteration of f(col).
 *
 * Tests (statement)
 * [[0,1,0],[1,1,1],[0,1,0]], target 0 → 4
 * [[1,-1],[-1,1]], target 0 → 5
 * [[904]], target 0 → 0
 *
 * Improvements / variants
 * - If columns >> rows, transpose first so the inner dimension is min(m,n) — same asymptotics here since both ≤100.
 * - Fenwick tree unnecessary — cumulative col[k] already computed incrementally when extending j.
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.HashMap;
import java.util.Map;

public class Solution {

    public int numSubmatrixSumTarget(int[][] matrix, int target) {
        int m = matrix.length;
        int n = matrix[0].length;
        int ans = 0;
        for (int top = 0; top < m; top++) {
            int[] col = new int[n];
            for (int bot = top; bot < m; bot++) {
                for (int k = 0; k < n; k++) {
                    col[k] += matrix[bot][k];
                }
                ans += countSubarrays(col, target);
            }
        }
        return ans;
    }

    private int countSubarrays(int[] nums, int target) {
        Map<Integer, Integer> freq = new HashMap<>();
        freq.put(0, 1);
        int cnt = 0;
        int pref = 0;
        for (int x : nums) {
            pref += x;
            cnt += freq.getOrDefault(pref - target, 0);
            freq.merge(pref, 1, Integer::sum);
        }
        return cnt;
    }
}
// @lc code=end
