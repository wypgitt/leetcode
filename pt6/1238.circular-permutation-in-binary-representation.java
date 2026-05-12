import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<Integer> circularPermutation(int n, int start) {
        int size = 1 << n;
        List<Integer> ans = new ArrayList<>(size);

        for (int i = 0; i < size; i++) {
            int gray = i ^ (i >> 1);
            ans.add(start ^ gray);
        }

        return ans;
    }
}

/*
Explanation

i ^ (i >> 1) generates the standard n-bit Gray code sequence. Adjacent values
differ by one bit, and the last value also differs from the first by one bit.
XOR every value with start; XOR is a bijection and preserves bit differences,
so the sequence still forms a valid cycle and now begins at start.

This direct construction is simpler than backtracking over all permutations.

Edge cases: n == 1 returns two values; start can be any n-bit value.

Time complexity: O(2^n).
Space complexity: O(2^n).
*/
