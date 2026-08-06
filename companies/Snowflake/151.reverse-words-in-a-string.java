/**
 * Algorithm:
 * Trim and split on one or more spaces, then append words in reverse order with
 * single spaces between them.
 *
 * Java data structures:
 * StringBuilder avoids repeated immutable string concatenation.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public String reverseWords(String s) {
        String[] parts = s.trim().split("\\s+");
        StringBuilder ans = new StringBuilder();
        for (int i = parts.length - 1; i >= 0; i--) {
            if (ans.length() > 0) {
                ans.append(' ');
            }
            ans.append(parts[i]);
        }
        return ans.toString();
    }
}

