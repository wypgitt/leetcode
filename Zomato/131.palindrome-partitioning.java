import java.util.*;

/**
 * Algorithm:
 * Precompute pal[i][j], whether s[i..j] is a palindrome, then backtrack all
 * partitions by taking only palindromic next substrings.
 *
 * Java data structures:
 * boolean[][] stores palindrome DP; ArrayList<String> stores the current path.
 *
 * Complexity:
 * Palindrome DP O(n^2), backtracking output-dependent; recursion space O(n).
 */
class Solution {
    private String s;
    private boolean[][] pal;
    private List<String> path;
    private List<List<String>> ans;

    public List<List<String>> partition(String s) {
        this.s = s;
        int n = s.length();
        pal = new boolean[n][n];
        for (int i = n - 1; i >= 0; i--) {
            for (int j = i; j < n; j++) {
                pal[i][j] = s.charAt(i) == s.charAt(j) && (j - i < 2 || pal[i + 1][j - 1]);
            }
        }
        path = new ArrayList<>();
        ans = new ArrayList<>();
        dfs(0);
        return ans;
    }

    private void dfs(int start) {
        if (start == s.length()) {
            ans.add(new ArrayList<>(path));
            return;
        }
        for (int end = start; end < s.length(); end++) {
            if (pal[start][end]) {
                path.add(s.substring(start, end + 1));
                dfs(end + 1);
                path.remove(path.size() - 1);
            }
        }
    }
}

