/*
 * @lc app=leetcode id=932 lang=java
 *
 * [932] Beautiful Array
 */

/*
 * --- Interview notes (no arithmetic progression in index order, divide & conquer, doubling trick) ---
 *
 * Problem
 * Permutation of 1..n such that no three indices i < j < k have A[i] + A[k] = 2*A[j] (no 3-term AP in value order).
 *
 * Construction: start [1], repeatedly replace ans with odds then evens [2x-1 for x in ans] + [2x for x in ans] until length >= n,
 * then take first n values <= n in order.
 *
 * Time O(n), Space O(n).
 *
 * --- end notes ---
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public int[] beautifulArray(int n) {
        List<Integer> ans = new ArrayList<>();
        ans.add(1);
        while (ans.size() < n) {
            List<Integer> nxt = new ArrayList<>();
            for (int x : ans) {
                nxt.add(2 * x - 1);
            }
            for (int x : ans) {
                nxt.add(2 * x);
            }
            ans = nxt;
        }
        int[] out = new int[n];
        int t = 0;
        for (int x : ans) {
            if (x <= n && t < n) {
                out[t++] = x;
            }
        }
        return out;
    }
}
// @lc code=end
