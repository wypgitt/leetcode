/*
 * @lc app=leetcode id=3867 lang=java
 *
 * [3867] Sum of GCD of Formed Pairs
 *
 * Build the same transformed prefix values as the Python reference:
 * prefixGcd[i] = gcd(nums[i], max(nums[0..i])). Sort them, pair smallest with
 * largest, and sum gcds of each pair.
 *
 * Time: O(n log n). Space: O(n).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public int gcdSum(int[] nums) {
        int[] prefixGcd = new int[nums.length];
        int runningMax = 0;
        for (int i = 0; i < nums.length; i++) {
            runningMax = Math.max(runningMax, nums[i]);
            prefixGcd[i] = gcd(nums[i], runningMax);
        }

        Arrays.sort(prefixGcd);
        int answer = 0;
        int left = 0;
        int right = prefixGcd.length - 1;
        while (left < right) {
            answer += gcd(prefixGcd[left++], prefixGcd[right--]);
        }
        return answer;
    }

    private int gcd(int a, int b) {
        while (b != 0) {
            int t = a % b;
            a = b;
            b = t;
        }
        return Math.abs(a);
    }
}
// @lc code=end
