/*
 * @lc app=leetcode id=2663 lang=java
 *
 * [2663] Lexicographically Smallest Beautiful String
 */

// @lc code=start
class Solution {
    public String smallestBeautifulString(String s, int k) {
        char[] a = s.toCharArray();
        int n = a.length;
        for (int i = n - 1; i >= 0; i--) {
            for (int j = a[i] - 'a' + 1; j < k; j++) {
                char c = (char) ('a' + j);
                if (i > 0 && c == a[i - 1]) {
                    continue;
                }
                if (i > 1 && c == a[i - 2]) {
                    continue;
                }
                a[i] = c;
                boolean fillOk = true;
                for (int p = i + 1; p < n; p++) {
                    boolean placed = false;
                    for (int t = 0; t < k; t++) {
                        char d = (char) ('a' + t);
                        if (p > 0 && d == a[p - 1]) {
                            continue;
                        }
                        if (p > 1 && d == a[p - 2]) {
                            continue;
                        }
                        a[p] = d;
                        placed = true;
                        break;
                    }
                    if (!placed) {
                        fillOk = false;
                        break;
                    }
                }
                if (fillOk) {
                    return new String(a);
                }
            }
        }
        return "";
    }
}
// @lc code=end
