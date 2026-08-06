/*
 * @lc app=leetcode id=3859 lang=java
 *
 * [3859] Count Subarrays With K Distinct Integers
 *
 * Count contiguous subarrays nums[L..R] with exactly k distinct values, each appearing at least m
 * times. Answer = G(k) - G(k-1) where G(K) counts subarrays with at most K distinct and all
 * positive frequencies >= m. Implemented G(K) in O(n^2) by fixing r and extending l backward
 * with freq / distinct / bad counters.
 */

import java.util.HashMap;
import java.util.Map;

// @lc code=start
class Solution {
    public long countSubarrays(int[] nums, int k, int m) {
        if (k <= 0) {
            return 0;
        }
        return atMost(nums, k, m) - atMost(nums, k - 1, m);
    }

    private long atMost(int[] nums, int k, int m) {
        if (k <= 0) {
            return 0;
        }
        int n = nums.length;
        long ans = 0;
        for (int r = 0; r < n; r++) {
            Map<Integer, Integer> freq = new HashMap<>();
            int distinct = 0;
            int bad = 0;
            for (int l = r; l >= 0; l--) {
                int x = nums[l];
                int old = freq.getOrDefault(x, 0);
                if (old == 0) {
                    distinct++;
                } else if (old < m) {
                    bad--;
                }
                int nw = old + 1;
                freq.put(x, nw);
                if (nw < m) {
                    bad++;
                }
                if (distinct > k) {
                    break;
                }
                if (bad == 0) {
                    ans++;
                }
            }
        }
        return ans;
    }
}
// @lc code=end
