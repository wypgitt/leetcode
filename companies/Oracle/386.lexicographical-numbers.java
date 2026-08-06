import java.util.*;

/**
 * Algorithm:
 * Lexicographical order is a preorder walk of an implicit 10-ary prefix tree.
 * From x, visit x * 10 if it is within range; otherwise climb until x has a
 * valid next sibling x + 1.
 *
 * Java data structures:
 * ArrayList stores the required output. No explicit trie is built because
 * integer arithmetic navigates the prefix tree.
 *
 * Complexity:
 * Time O(n) amortized, extra working space O(1), output space O(n).
 */
class Solution {
    public List<Integer> lexicalOrder(int n) {
        List<Integer> ans = new ArrayList<>(n);
        int cur = 1;
        for (int i = 0; i < n; i++) {
            ans.add(cur);
            if (cur * 10 <= n) {
                cur *= 10;
            } else {
                while (cur % 10 == 9 || cur + 1 > n) {
                    cur /= 10;
                }
                cur++;
            }
        }
        return ans;
    }
}

