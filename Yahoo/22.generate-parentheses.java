import java.util.*;

/**
 * Algorithm:
 * Backtrack only valid prefixes. We may add '(' while opened < n, and may add
 * ')' while closed < opened. When the path length is 2n, it is a valid string.
 *
 * Java data structures:
 * StringBuilder stores the mutable prefix.
 *
 * Complexity:
 * Time O(C_n * n), recursion space O(n), plus output.
 */
class Solution {
    private List<String> ans;
    private StringBuilder path;
    private int n;

    public List<String> generateParenthesis(int n) {
        this.n = n;
        ans = new ArrayList<>();
        path = new StringBuilder();
        backtrack(0, 0);
        return ans;
    }

    private void backtrack(int opened, int closed) {
        if (path.length() == 2 * n) {
            ans.add(path.toString());
            return;
        }
        if (opened < n) {
            path.append('(');
            backtrack(opened + 1, closed);
            path.deleteCharAt(path.length() - 1);
        }
        if (closed < opened) {
            path.append(')');
            backtrack(opened, closed + 1);
            path.deleteCharAt(path.length() - 1);
        }
    }
}

