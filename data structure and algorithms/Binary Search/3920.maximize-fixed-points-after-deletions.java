/*
 * @lc app=leetcode id=3920 lang=java
 *
 * [3920] Maximize Fixed Points After Deletions
 *
 * For nums[i] to become fixed after deletions, deletedBefore = i - nums[i]
 * must be nonnegative. Process groups by value; a Fenwick tree stores maximum
 * chain length for each deletedBefore. Updates for the same value are batched so
 * equal values do not extend each other prematurely.
 *
 * Java note: FenwickMax performs prefix maximum queries and point max updates.
 *
 * Time: O(n log n). Space: O(n).
 */

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

// @lc code=start
class Solution {
    public int maxFixedPoints(int[] nums) {
        int n = nums.length;
        TreeMap<Integer, List<Integer>> groups = new TreeMap<>();
        for (int i = 0; i < n; i++) {
            if (nums[i] <= i) {
                groups.computeIfAbsent(nums[i], unused -> new ArrayList<>()).add(i - nums[i]);
            }
        }

        FenwickMax bit = new FenwickMax(n);
        int answer = 0;
        for (Map.Entry<Integer, List<Integer>> entry : groups.entrySet()) {
            List<int[]> pending = new ArrayList<>();
            for (int deletedBefore : entry.getValue()) {
                int best = bit.query(deletedBefore) + 1;
                pending.add(new int[] {deletedBefore, best});
                answer = Math.max(answer, best);
            }
            for (int[] update : pending) {
                bit.update(update[0], update[1]);
            }
        }
        return answer;
    }

    private static class FenwickMax {
        private final int[] tree;

        FenwickMax(int size) {
            tree = new int[size + 1];
        }

        void update(int index, int value) {
            index++;
            while (index < tree.length) {
                tree[index] = Math.max(tree[index], value);
                index += index & -index;
            }
        }

        int query(int index) {
            index++;
            int best = 0;
            while (index > 0) {
                best = Math.max(best, tree[index]);
                index -= index & -index;
            }
            return best;
        }
    }
}
// @lc code=end
