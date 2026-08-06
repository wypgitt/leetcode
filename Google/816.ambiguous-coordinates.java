import java.util.*;

/**
 * Algorithm:
 * Remove the outer parentheses, split the digits into left and right parts,
 * generate every valid decimal representation for each side, and combine them.
 * Leading zeros and trailing decimal zeros are rejected by the rules.
 *
 * Complexity:
 * There are O(n) split positions and O(n) forms per side, so O(n^3) including
 * output string construction in the worst case. Output space dominates.
 */
class Solution {
    public List<String> ambiguousCoordinates(String s) {
        String digits = s.substring(1, s.length() - 1);
        List<String> ans = new ArrayList<>();
        for (int i = 1; i < digits.length(); i++) {
            List<String> leftForms = forms(digits.substring(0, i));
            List<String> rightForms = forms(digits.substring(i));
            for (String left : leftForms) {
                for (String right : rightForms) {
                    ans.add("(" + left + ", " + right + ")");
                }
            }
        }
        return ans;
    }

    private List<String> forms(String part) {
        List<String> ans = new ArrayList<>();
        if (part.length() == 1) {
            ans.add(part);
            return ans;
        }
        if (part.charAt(0) != '0') {
            ans.add(part);
        }
        for (int i = 1; i < part.length(); i++) {
            String left = part.substring(0, i);
            String right = part.substring(i);
            if ((left.equals("0") || !left.startsWith("0")) && !right.endsWith("0")) {
                ans.add(left + "." + right);
            }
        }
        return ans;
    }
}

