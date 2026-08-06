/**
 * Algorithm:
 * Compare dot-separated revision numbers pairwise. Missing revisions are
 * treated as zero.
 *
 * Complexity:
 * Time O(m + n), space O(m + n) for split arrays.
 */
class Solution {
    public int compareVersion(String version1, String version2) {
        String[] a = version1.split("\\.");
        String[] b = version2.split("\\.");
        int len = Math.max(a.length, b.length);
        for (int i = 0; i < len; i++) {
            int x = i < a.length ? Integer.parseInt(a[i]) : 0;
            int y = i < b.length ? Integer.parseInt(b[i]) : 0;
            if (x < y) {
                return -1;
            }
            if (x > y) {
                return 1;
            }
        }
        return 0;
    }
}

