/**
 * Algorithm:
 * Each index belongs to one cycle in the permutation-like array. Walk each
 * unvisited cycle, mark visited entries in-place as -1, and track the largest
 * cycle length.
 *
 * Complexity:
 * Time O(n), space O(1) because the input array is reused for visited marks.
 */
class Solution {
    public int arrayNesting(int[] nums) {
        int best = 0;
        for (int i = 0; i < nums.length; i++) {
            if (nums[i] == -1) {
                continue;
            }
            int count = 0;
            int j = i;
            while (nums[j] != -1) {
                int next = nums[j];
                nums[j] = -1;
                j = next;
                count++;
            }
            best = Math.max(best, count);
        }
        return best;
    }
}

