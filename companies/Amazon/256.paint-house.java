/**
 * Algorithm:
 * Rolling DP for three colors. The cost to paint the current house a color is
 * its color cost plus the minimum previous cost of the other two colors.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int minCost(int[][] costs) {
        if (costs == null || costs.length == 0) {
            return 0;
        }
        int red = 0;
        int blue = 0;
        int green = 0;
        for (int[] cost : costs) {
            int nextRed = cost[0] + Math.min(blue, green);
            int nextBlue = cost[1] + Math.min(red, green);
            int nextGreen = cost[2] + Math.min(red, blue);
            red = nextRed;
            blue = nextBlue;
            green = nextGreen;
        }
        return Math.min(red, Math.min(blue, green));
    }
}

