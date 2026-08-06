import java.util.*;

/**
 * Algorithm:
 * Backtrack four IP parts. Each part must have length 1..3, no leading zero
 * unless it is exactly "0", and integer value <= 255. Prune by remaining
 * character count.
 *
 * Complexity:
 * O(1) in practice because at most 3^4 segment choices exist; output is bounded.
 */
class Solution {
    private String s;
    private List<String> path;
    private List<String> ans;

    public List<String> restoreIpAddresses(String s) {
        this.s = s;
        path = new ArrayList<>();
        ans = new ArrayList<>();
        dfs(0);
        return ans;
    }

    private void dfs(int index) {
        int partsLeft = 4 - path.size();
        int charsLeft = s.length() - index;
        if (charsLeft < partsLeft || charsLeft > partsLeft * 3) {
            return;
        }
        if (path.size() == 4) {
            if (index == s.length()) {
                ans.add(String.join(".", path));
            }
            return;
        }
        for (int end = index + 1; end <= Math.min(index + 3, s.length()); end++) {
            String part = s.substring(index, end);
            if (valid(part)) {
                path.add(part);
                dfs(end);
                path.remove(path.size() - 1);
            }
        }
    }

    private boolean valid(String part) {
        return (part.equals("0") || !part.startsWith("0")) && Integer.parseInt(part) <= 255;
    }
}

