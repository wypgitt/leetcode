/*
 * LeetCode 1362 - Closest Divisors
 */
class Solution {
    public int[] closestDivisors(int num) {
        int[] first = closestPair(num + 1);
        int[] second = closestPair(num + 2);

        if (Math.abs(first[0] - first[1]) <= Math.abs(second[0] - second[1])) {
            return first;
        }
        return second;
    }

    private int[] closestPair(int value) {
        for (int divisor = (int) Math.sqrt(value); divisor >= 1; divisor--) {
            if (value % divisor == 0) {
                return new int[] {divisor, value / divisor};
            }
        }
        return new int[] {1, value};
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * For a fixed number, the closest factor pair is nearest its square root. Scan
 * downward from sqrt(value), and the first divisor found gives the smallest
 * difference pair for that value. Compare `num + 1` and `num + 2`.
 *
 * Java data structures:
 * Only small `int[]` pairs are needed. No collection structure is necessary.
 *
 * Edge cases:
 * - Perfect square returns equal factors.
 * - Prime candidate falls back to 1 and itself.
 * - If both candidates tie, returning the first is valid.
 *
 * Complexity:
 * Time O(sqrt(num)).
 * Space O(1).
 */
