/*
 * @lc app=leetcode id=3907 lang=java
 *
 * [3907] Count Smaller Elements With Opposite Parity
 *
 * Coordinate-compress values and scan from right to left. Two Fenwick trees
 * store frequencies of seen even and odd values; query the opposite-parity tree
 * for ranks smaller than the current value.
 *
 * Time: O(n log n). Space: O(n).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public int[] countSmallerOppositeParity(int[] nums) {
        int[] sorted = nums.clone();
        Arrays.sort(sorted);
        int unique = 0;
        for (int value : sorted) {
            if (unique == 0 || sorted[unique - 1] != value) {
                sorted[unique++] = value;
            }
        }
        int[] values = Arrays.copyOf(sorted, unique);

        Fenwick evenTree = new Fenwick(unique);
        Fenwick oddTree = new Fenwick(unique);
        int[] answer = new int[nums.length];

        for (int i = nums.length - 1; i >= 0; i--) {
            int pos = lowerBound(values, nums[i]) + 1;
            if ((nums[i] & 1) == 0) {
                answer[i] = oddTree.query(pos - 1);
                evenTree.add(pos, 1);
            } else {
                answer[i] = evenTree.query(pos - 1);
                oddTree.add(pos, 1);
            }
        }
        return answer;
    }

    private int lowerBound(int[] arr, int target) {
        int lo = 0;
        int hi = arr.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (arr[mid] < target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }

    private static class Fenwick {
        private final int[] tree;

        Fenwick(int size) {
            tree = new int[size + 1];
        }

        void add(int index, int delta) {
            while (index < tree.length) {
                tree[index] += delta;
                index += index & -index;
            }
        }

        int query(int index) {
            int total = 0;
            while (index > 0) {
                total += tree[index];
                index -= index & -index;
            }
            return total;
        }
    }
}
// @lc code=end
