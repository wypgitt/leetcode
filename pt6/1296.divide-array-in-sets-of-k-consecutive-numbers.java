import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

class Solution {
    public boolean isPossibleDivide(int[] nums, int k) {
        if (nums.length % k != 0) {
            return false;
        }

        Map<Integer, Integer> count = new HashMap<>();
        for (int num : nums) {
            count.put(num, count.getOrDefault(num, 0) + 1);
        }
        Arrays.sort(nums);

        for (int start : nums) {
            int amount = count.getOrDefault(start, 0);
            if (amount == 0) {
                continue;
            }

            for (int value = start; value < start + k; value++) {
                int available = count.getOrDefault(value, 0);
                if (available < amount) {
                    return false;
                }
                count.put(value, available - amount);
            }
        }

        return true;
    }
}

/*
Explanation

Process numbers in sorted order. If count[start] is positive, those copies must
begin groups at start because no smaller value remains to use them. Therefore
each value start through start + k - 1 must have at least that many copies.

HashMap stores multiplicities, and sorting gives the greedy order that makes
the forced-start argument valid.

Edge cases: length not divisible by k; missing middle value; duplicate-heavy
inputs.

Time complexity: O(n log n + g * k), where g is the number of distinct group
starts processed.
Space complexity: O(n).
*/
