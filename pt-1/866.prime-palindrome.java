/*
 * @lc app=leetcode id=866 lang=java
 *
 * [866] Prime Palindrome
 *
 * Handle small primes directly. For n > 11, only odd-length palindromes can be
 * prime because every even-length palindrome is divisible by 11. Generate
 * odd-length palindromes by mirroring a half and test primality.
 *
 * Time: practical O(number of candidates * sqrt(candidate)). Space: O(1).
 */

// @lc code=start
class Solution {
    public int primePalindrome(int n) {
        if (n <= 2) {
            return 2;
        }
        if (n <= 3) {
            return 3;
        }
        if (n <= 5) {
            return 5;
        }
        if (n <= 7) {
            return 7;
        }
        if (n <= 11) {
            return 11;
        }

        int length = Integer.toString(n).length();
        if ((length & 1) == 0) {
            length++;
        }

        while (true) {
            int halfLo = pow10((length - 1) / 2);
            int halfHi = pow10((length + 1) / 2);
            for (int half = halfLo; half < halfHi; half++) {
                int candidate = buildOddPalindrome(half);
                if (candidate >= n && isPrime(candidate)) {
                    return candidate;
                }
            }
            length += 2;
        }
    }

    private int buildOddPalindrome(int half) {
        int result = half;
        int tail = half / 10;
        while (tail > 0) {
            result = result * 10 + tail % 10;
            tail /= 10;
        }
        return result;
    }

    private boolean isPrime(int x) {
        if (x < 2) {
            return false;
        }
        if ((x & 1) == 0) {
            return x == 2;
        }
        for (int d = 3; (long) d * d <= x; d += 2) {
            if (x % d == 0) {
                return false;
            }
        }
        return true;
    }

    private int pow10(int exp) {
        int value = 1;
        while (exp-- > 0) {
            value *= 10;
        }
        return value;
    }
}
// @lc code=end
