/*
 * @lc app=leetcode id=2584 lang=java
 *
 * [2584] Split the Array to Make Coprime Products
 */

/*
 * gcd(product left, product right) == 1 iff no prime divides both sides of the split.
 * Sweep i: move index i from "right" to "left"; decrement per-prime right counts;
 * if a prime still exists on both sides, it enters {@code leftBridge}. First i with
 * empty {@code leftBridge} is the answer.
 *
 * Time: O(n · trial divisions per value). Space: O(number of distinct primes).
 * =============================================================================
 */

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// @lc code=start
class Solution {
    public int findValidSplit(int[] nums) {
        Map<Integer, Integer> right = new HashMap<>();
        for (int v : nums) {
            for (int p : primeFactors(v)) {
                right.merge(p, 1, Integer::sum);
            }
        }

        Map<Integer, Integer> leftBridge = new HashMap<>();

        for (int i = 0; i < nums.length - 1; i++) {
            for (int p : primeFactors(nums[i])) {
                right.merge(p, -1, Integer::sum);
                if (right.get(p) == 0) {
                    right.remove(p);
                    leftBridge.remove(p);
                } else {
                    leftBridge.merge(p, 1, Integer::sum);
                }
            }
            if (leftBridge.isEmpty()) {
                return i;
            }
        }
        return -1;
    }

    /** Distinct prime factors; nums[i] ≤ 10^6 → trial divide up to 1000 suffices. */
    private static List<Integer> primeFactors(int num) {
        List<Integer> factors = new ArrayList<>();
        if (num <= 1) {
            return factors;
        }
        int x = num;
        int lim = Math.min(1000, x);
        for (int d = 2; d <= lim; d++) {
            if (x % d == 0) {
                factors.add(d);
                while (x % d == 0) {
                    x /= d;
                }
            }
        }
        if (x > 1) {
            factors.add(x);
        }
        return factors;
    }
}
// @lc code=end
