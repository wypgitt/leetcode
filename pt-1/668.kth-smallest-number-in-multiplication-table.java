/*
 * @lc app=leetcode id=668 lang=java
 *
 * [668] Kth Smallest Number in Multiplication Table
 *
 * Binary search the answer value. For a candidate x, row i contributes
 * min(n, x / i) entries <= x. The smallest x with count >= k is the kth value.
 *
 * Time: O(min(m,n) * log(mn)). Space: O(1).
 */

// @lc code=start
class Solution {
    public int findKthNumber(int m, int n, int k) {
        if (m > n) {
            int tmp = m;
            m = n;
            n = tmp;
        }

        int left = 1;
        int right = m * n;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (countLessOrEqual(m, n, mid) >= k) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }

    private int countLessOrEqual(int m, int n, int value) {
        int count = 0;
        for (int row = 1; row <= m; row++) {
            count += Math.min(n, value / row);
        }
        return count;
    }
}
// @lc code=end
