/*
 * @lc app=leetcode id=949 lang=java
 *
 * [949] Largest Time For Given Digits
 */

/*
 * --- Interview notes (enumerating assignments, validity, total-minutes order, complexity) ---
 *
 * Problem
 * Four digits 0-9; form HH:MM (24h). Return lexicographically largest valid time (equals latest time). Else "".
 *
 * Only 4! = 24 permutations of positions — brute force.
 *
 * Time O(1), Space O(1).
 *
 * --- end notes ---
 */

// @lc code=start
class Solution {
    public String largestTimeFromDigits(int[] arr) {
        int best = -1;
        int[] p = {0, 1, 2, 3};
        do {
            int a = arr[p[0]];
            int b = arr[p[1]];
            int c = arr[p[2]];
            int d = arr[p[3]];
            int h = 10 * a + b;
            int m = 10 * c + d;
            if (h < 24 && m < 60) {
                int t = 60 * h + m;
                if (t > best) {
                    best = t;
                }
            }
        } while (nextPermutation(p));
        if (best < 0) {
            return "";
        }
        return String.format("%02d:%02d", best / 60, best % 60);
    }

    private static boolean nextPermutation(int[] a) {
        int i = a.length - 2;
        while (i >= 0 && a[i] >= a[i + 1]) {
            i--;
        }
        if (i < 0) {
            return false;
        }
        int j = a.length - 1;
        while (a[j] <= a[i]) {
            j--;
        }
        swap(a, i, j);
        for (int l = i + 1, r = a.length - 1; l < r; l++, r--) {
            swap(a, l, r);
        }
        return true;
    }

    private static void swap(int[] a, int i, int j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
    }
}
// @lc code=end
