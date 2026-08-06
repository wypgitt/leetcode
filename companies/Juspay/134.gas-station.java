/**
 * Algorithm:
 * If total gas is less than total cost, no solution exists. Otherwise, scan
 * once. When the current tank drops below zero, no station in the current
 * segment can be a valid start, so start at the next station.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int canCompleteCircuit(int[] gas, int[] cost) {
        int total = 0;
        int tank = 0;
        int start = 0;
        for (int i = 0; i < gas.length; i++) {
            int diff = gas[i] - cost[i];
            total += diff;
            tank += diff;
            if (tank < 0) {
                start = i + 1;
                tank = 0;
            }
        }
        return total < 0 ? -1 : start;
    }
}

