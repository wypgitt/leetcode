import java.util.*;

class Solution {
    public int nthUglyNumber(int n, int a, int b, int c) {
        long ab = lcm(a, b);
        long ac = lcm(a, c);
        long bc = lcm(b, c);
        long abc = lcm(ab, c);

        long left = 1;
        long right = 2_000_000_000L;
        while (left < right) {
            long mid = left + (right - left) / 2;
            if (countUgly(mid, a, b, c, ab, ac, bc, abc) >= n) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }

        return (int) left;
    }

    private long countUgly(long limit, long a, long b, long c, long ab, long ac, long bc, long abc) {
        return limit / a + limit / b + limit / c - limit / ab - limit / ac - limit / bc + limit / abc;
    }

    private long gcd(long a, long b) {
        while (b != 0) {
            long temp = a % b;
            a = b;
            b = temp;
        }
        return a;
    }

    private long lcm(long a, long b) {
        return a / gcd(a, b) * b;
    }
}

