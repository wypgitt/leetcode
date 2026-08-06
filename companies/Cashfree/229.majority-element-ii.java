import java.util.*;

/**
 * Algorithm:
 * Boyer-Moore voting generalized for elements appearing more than n/3 times.
 * At most two such elements can exist, so keep two candidates and verify them
 * with a second pass.
 *
 * Complexity:
 * Time O(n), space O(1) excluding output.
 */
class Solution {
    public List<Integer> majorityElement(int[] nums) {
        Integer cand1 = null;
        Integer cand2 = null;
        int count1 = 0;
        int count2 = 0;
        for (int num : nums) {
            if (cand1 != null && num == cand1) {
                count1++;
            } else if (cand2 != null && num == cand2) {
                count2++;
            } else if (count1 == 0) {
                cand1 = num;
                count1 = 1;
            } else if (count2 == 0) {
                cand2 = num;
                count2 = 1;
            } else {
                count1--;
                count2--;
            }
        }
        int actual1 = 0;
        int actual2 = 0;
        for (int num : nums) {
            if (cand1 != null && num == cand1) {
                actual1++;
            } else if (cand2 != null && num == cand2) {
                actual2++;
            }
        }
        List<Integer> ans = new ArrayList<>();
        if (cand1 != null && actual1 > nums.length / 3) {
            ans.add(cand1);
        }
        if (cand2 != null && actual2 > nums.length / 3) {
            ans.add(cand2);
        }
        return ans;
    }
}

