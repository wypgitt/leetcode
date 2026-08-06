/*
 * @lc app=leetcode id=3878 lang=java
 *
 * [3878] Count Good Subarrays
 *
 * Count subarrays whose OR equals some element in the subarray via two monotonic passes for left/right
 * bounds; sum (i - L[i]) * (R[i] - i) with 64-bit accumulator.
 */

import java.util.ArrayDeque;
import java.util.Deque;

// @lc code=start
class Solution {
    public long countGoodSubarrays(int[] nums) {
        int n = nums.length;
        int[] left = new int[n];
        Deque<Integer> stk = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            int x = nums[i];
            while (!stk.isEmpty()) {
                int j = stk.peekLast();
                if (nums[j] < x && (nums[j] | x) == x) {
                    stk.pollLast();
                } else {
                    break;
                }
            }
            left[i] = stk.isEmpty() ? -1 : stk.peekLast();
            stk.addLast(i);
        }

        int[] right = new int[n];
        stk.clear();
        for (int i = n - 1; i >= 0; i--) {
            while (!stk.isEmpty()) {
                int j = stk.peekLast();
                if ((nums[j] | nums[i]) == nums[i]) {
                    stk.pollLast();
                } else {
                    break;
                }
            }
            right[i] = stk.isEmpty() ? n : stk.peekLast();
            stk.addLast(i);
        }

        long ans = 0;
        for (int i = 0; i < n; i++) {
            ans += (long) (i - left[i]) * (right[i] - i);
        }
        return ans;
    }
}
// @lc code=end
