import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/*
 * LeetCode 1387 - Sort Integers by The Power Value
 */
class Solution {
    private final Map<Integer, Integer> memo = new HashMap<>();

    public int getKth(int lo, int hi, int k) {
        memo.put(1, 0);

        Integer[] values = new Integer[hi - lo + 1];
        for (int i = 0; i < values.length; i++) {
            values[i] = lo + i;
        }

        Arrays.sort(values, (a, b) -> {
            int powerA = power(a);
            int powerB = power(b);
            if (powerA != powerB) {
                return Integer.compare(powerA, powerB);
            }
            return Integer.compare(a, b);
        });

        return values[k - 1];
    }

    private int power(int value) {
        if (memo.containsKey(value)) {
            return memo.get(value);
        }

        int next = value % 2 == 0 ? value / 2 : 3 * value + 1;
        int result = 1 + power(next);
        memo.put(value, result);
        return result;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Compute the Collatz power value for every number in [lo, hi], sort by
 * `(power, value)`, and return the kth number.
 *
 * Java data structures:
 * `HashMap<Integer, Integer>` memoizes power values. Collatz sequences often
 * merge into shared tails, so memoization saves repeated recursion. `Integer[]`
 * is used because Java comparators work with object arrays, not primitive
 * `int[]`.
 *
 * Edge cases:
 * - lo == hi returns that number.
 * - Equal power values break ties by smaller integer.
 * - Intermediate Collatz values can exceed hi; memo still stores them.
 *
 * Complexity:
 * Time O(m log m + C), where m = hi - lo + 1 and C is unique Collatz states.
 * Space O(C).
 */
