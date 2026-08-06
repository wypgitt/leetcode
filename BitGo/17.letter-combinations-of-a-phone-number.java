import java.util.*;

/**
 * Algorithm:
 * Backtrack through the Cartesian product of letters for each digit. The path
 * has one chosen character per processed digit; when it reaches full length,
 * it becomes one answer.
 *
 * Java data structures:
 * A String[] maps digit characters to letter strings. StringBuilder is the
 * mutable path.
 *
 * Complexity:
 * Time O(4^n * n), recursion space O(n), plus output.
 */
class Solution {
    private static final String[] PHONE = {
        "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
    };
    private List<String> ans;
    private String digits;
    private StringBuilder path;

    public List<String> letterCombinations(String digits) {
        ans = new ArrayList<>();
        if (digits == null || digits.isEmpty()) {
            return ans;
        }
        this.digits = digits;
        path = new StringBuilder();
        backtrack(0);
        return ans;
    }

    private void backtrack(int index) {
        if (index == digits.length()) {
            ans.add(path.toString());
            return;
        }
        String letters = PHONE[digits.charAt(index) - '0'];
        for (int i = 0; i < letters.length(); i++) {
            path.append(letters.charAt(i));
            backtrack(index + 1);
            path.deleteCharAt(path.length() - 1);
        }
    }
}

