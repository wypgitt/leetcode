/**
 * Algorithm:
 * Iteratively run-length encode the previous term: count adjacent equal digits
 * and append "count then digit" to form the next term.
 *
 * Java data structures:
 * StringBuilder builds each next term in linear time.
 *
 * Complexity:
 * Time O(total generated length), space O(current term length).
 */
class Solution {
    public String countAndSay(int n) {
        String term = "1";
        for (int iter = 1; iter < n; iter++) {
            StringBuilder next = new StringBuilder();
            int i = 0;
            while (i < term.length()) {
                int j = i;
                while (j < term.length() && term.charAt(j) == term.charAt(i)) {
                    j++;
                }
                next.append(j - i).append(term.charAt(i));
                i = j;
            }
            term = next.toString();
        }
        return term;
    }
}

