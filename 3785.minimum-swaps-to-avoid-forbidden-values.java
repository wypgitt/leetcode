/*
 * @lc app=leetcode id=3785 lang=java
 *
 * [3785] Minimum Swaps to Avoid Forbidden Values
 *
 * First verify feasibility: a value appearing more than n times across nums
 * and forbidden cannot be placed away from all its forbidden positions. Among
 * bad positions where nums[i] == forbidden[i], each swap can fix at most two
 * bad positions unless one value dominates; answer is max(ceil(bad/2), maxBadByValue).
 *
 * Java note: HashMap<Integer,Integer> is used as Counter.
 *
 * Time: O(n). Space: O(n).
 */

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

// @lc code=start
class Solution {
    public int minSwaps(int[] nums, int[] forbidden) {
        int n = nums.length;
        Map<Integer, Integer> numsCount = new HashMap<>();
        Map<Integer, Integer> forbiddenCount = new HashMap<>();
        Set<Integer> values = new HashSet<>();

        for (int value : nums) {
            numsCount.merge(value, 1, Integer::sum);
            values.add(value);
        }
        for (int value : forbidden) {
            forbiddenCount.merge(value, 1, Integer::sum);
            values.add(value);
        }
        for (int value : values) {
            if (numsCount.getOrDefault(value, 0) + forbiddenCount.getOrDefault(value, 0) > n) {
                return -1;
            }
        }

        Map<Integer, Integer> badCount = new HashMap<>();
        int badTotal = 0;
        int maxBad = 0;
        for (int i = 0; i < n; i++) {
            if (nums[i] == forbidden[i]) {
                int count = badCount.merge(nums[i], 1, Integer::sum);
                maxBad = Math.max(maxBad, count);
                badTotal++;
            }
        }
        if (badTotal == 0) {
            return 0;
        }
        return Math.max((badTotal + 1) / 2, maxBad);
    }
}
// @lc code=end
