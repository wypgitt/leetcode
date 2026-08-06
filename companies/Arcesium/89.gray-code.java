import java.util.*;

/**
 * Algorithm:
 * The binary-reflected Gray code for i is i ^ (i >> 1). Applying that transform
 * for every i from 0 to 2^n - 1 gives adjacent values differing by one bit.
 *
 * Complexity:
 * Time O(2^n), extra space O(1) excluding output.
 */
class Solution {
    public List<Integer> grayCode(int n) {
        int size = 1 << n;
        List<Integer> ans = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            ans.add(i ^ (i >> 1));
        }
        return ans;
    }
}

