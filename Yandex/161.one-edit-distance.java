/**
 * Algorithm:
 * Ensure s is no longer than t. At the first mismatch, equal lengths require
 * replacing one character; unequal lengths require inserting one character into
 * s, so compare the remaining suffixes accordingly.
 *
 * Complexity:
 * Time O(n), space O(1) excluding substring comparison allocation.
 */
class Solution {
    public boolean isOneEditDistance(String s, String t) {
        if (Math.abs(s.length() - t.length()) > 1) {
            return false;
        }
        if (s.length() > t.length()) {
            return isOneEditDistance(t, s);
        }
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) != t.charAt(i)) {
                if (s.length() == t.length()) {
                    return s.substring(i + 1).equals(t.substring(i + 1));
                }
                return s.substring(i).equals(t.substring(i + 1));
            }
        }
        return t.length() - s.length() == 1;
    }
}

