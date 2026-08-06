/**
 * Algorithm:
 * Removing X from both strings must give the same L/R order. Then compare the
 * positions of each non-X character: L can only move left, and R can only move
 * right.
 *
 * Complexity:
 * Time O(n), space O(n) for the replace results.
 */
class Solution {
    public boolean canTransform(String start, String result) {
        if (!start.replace("X", "").equals(result.replace("X", ""))) {
            return false;
        }
        int i = 0;
        int j = 0;
        int n = start.length();
        while (i < n && j < n) {
            while (i < n && start.charAt(i) == 'X') {
                i++;
            }
            while (j < n && result.charAt(j) == 'X') {
                j++;
            }
            if (i == n || j == n) {
                break;
            }
            if (start.charAt(i) == 'L' && i < j) {
                return false;
            }
            if (start.charAt(i) == 'R' && i > j) {
                return false;
            }
            i++;
            j++;
        }
        return true;
    }
}

