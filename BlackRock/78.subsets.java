import java.util.*;

/**
 * Algorithm:
 * Iteratively build the power set. For each number, append that number to every
 * subset built so far and add those new subsets to the answer.
 *
 * Complexity:
 * Time O(2^n * n), output space O(2^n * n).
 */
class Solution {
    public List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> ans = new ArrayList<>();
        ans.add(new ArrayList<>());
        for (int num : nums) {
            int size = ans.size();
            for (int i = 0; i < size; i++) {
                List<Integer> next = new ArrayList<>(ans.get(i));
                next.add(num);
                ans.add(next);
            }
        }
        return ans;
    }
}

