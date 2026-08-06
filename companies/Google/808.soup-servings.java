/**
 * Algorithm:
 * Scale servings by 25 ml units. Memoized recursion computes the probability
 * that soup A empties first, with 0.5 when both empty together. For large n the
 * probability is close enough to 1.0 under the problem tolerance.
 *
 * Java data structures:
 * Double[][] memo stores nullable cached probabilities.
 *
 * Complexity:
 * For n <= 4800, states are O((n/25)^2), each with four transitions.
 */
class Solution {
    private static final int[][] SERVINGS = {{4, 0}, {3, 1}, {2, 2}, {1, 3}};
    private Double[][] memo;

    public double soupServings(int n) {
        if (n > 4800) {
            return 1.0;
        }
        int units = (n + 24) / 25;
        memo = new Double[units + 1][units + 1];
        return dp(units, units);
    }

    private double dp(int a, int b) {
        if (a <= 0 && b <= 0) {
            return 0.5;
        }
        if (a <= 0) {
            return 1.0;
        }
        if (b <= 0) {
            return 0.0;
        }
        if (memo[a][b] != null) {
            return memo[a][b];
        }
        double ans = 0.0;
        for (int[] serving : SERVINGS) {
            ans += dp(a - serving[0], b - serving[1]);
        }
        memo[a][b] = 0.25 * ans;
        return memo[a][b];
    }
}

