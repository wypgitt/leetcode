import java.util.*;

/**
 * Algorithm:
 * Sieve of Eratosthenes. Mark multiples of each prime starting at p*p because
 * smaller multiples were already marked by smaller primes.
 *
 * Java data structures:
 * boolean[] stores primality flags.
 *
 * Complexity:
 * Time O(n log log n), space O(n).
 */
class Solution {
    public int countPrimes(int n) {
        if (n <= 2) {
            return 0;
        }
        boolean[] prime = new boolean[n];
        Arrays.fill(prime, true);
        prime[0] = false;
        prime[1] = false;
        for (int p = 2; p * p < n; p++) {
            if (prime[p]) {
                for (int multiple = p * p; multiple < n; multiple += p) {
                    prime[multiple] = false;
                }
            }
        }
        int count = 0;
        for (boolean isPrime : prime) {
            if (isPrime) {
                count++;
            }
        }
        return count;
    }
}
