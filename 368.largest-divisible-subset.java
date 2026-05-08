/*
 * @lc app=leetcode id=368 lang=java
 *
 * [368] Largest Divisible Subset
 *
 * Sort numbers and run longest-chain DP: dp[i] is the largest divisible subset
 * ending at nums[i]. A parent array reconstructs the actual subset.
 *
 * Java note: ArrayList is used for reconstruction because appending while
 * following parent pointers is natural; Collections.reverse restores order.
 *
 * Time: O(n^2). Space: O(n).
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

// @lc code=start
class Solution {
    public List<Integer> largestDivisibleSubset(int[] nums) {
        Arrays.sort(nums);
        int n = nums.length;
        int[] dp = new int[n];
        int[] parent = new int[n];
        Arrays.fill(dp, 1);
        Arrays.fill(parent, -1);

        int bestIndex = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < i; j++) {
                if (nums[i] % nums[j] == 0 && dp[j] + 1 > dp[i]) {
                    dp[i] = dp[j] + 1;
                    parent[i] = j;
                }
            }
            if (dp[i] > dp[bestIndex]) {
                bestIndex = i;
            }
        }

        List<Integer> answer = new ArrayList<>();
        for (int cur = bestIndex; cur != -1; cur = parent[cur]) {
            answer.add(nums[cur]);
        }
        Collections.reverse(answer);
        return answer;
    }
}
// @lc code=end
