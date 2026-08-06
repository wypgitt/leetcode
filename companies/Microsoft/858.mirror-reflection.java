/*
 * @lc app=leetcode id=858 lang=java
 *
 * [858] Mirror Reflection
 *
 * Reduce p and q by gcd. If reduced p is even, the ray hits receptor 2. If
 * reduced p is odd and q is even, it hits receptor 0. Otherwise both are odd and
 * it hits receptor 1.
 *
 * Time: O(log min(p,q)). Space: O(1).
 */

// @lc code=start
class Solution {
    public int mirrorReflection(int p, int q) {
        int g = gcd(p, q);
        p /= g;
        q /= g;
        if ((p & 1) == 0) {
            return 2;
        }
        if ((q & 1) == 0) {
            return 0;
        }
        return 1;
    }

    private int gcd(int a, int b) {
        while (b != 0) {
            int t = a % b;
            a = b;
            b = t;
        }
        return Math.abs(a);
    }
}
// @lc code=end
