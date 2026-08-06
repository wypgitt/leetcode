import java.util.*;

/**
 * Algorithm:
 * Sort numbers as strings with comparator (b+a) vs (a+b). If a+b is larger
 * than b+a, a should come before b.
 *
 * Java data structures:
 * String[] stores numeric strings; Arrays.sort uses the custom comparator.
 *
 * Complexity:
 * Time O(n log n * k), where k is max digit length. Space O(nk).
 */
class Solution {
    public String largestNumber(int[] nums) {
        String[] parts = new String[nums.length];
        for (int i = 0; i < nums.length; i++) {
            parts[i] = String.valueOf(nums[i]);
        }
        Arrays.sort(parts, (a, b) -> (b + a).compareTo(a + b));
        StringBuilder ans = new StringBuilder();
        for (String part : parts) {
            ans.append(part);
        }
        return ans.charAt(0) == '0' ? "0" : ans.toString();
    }
}

