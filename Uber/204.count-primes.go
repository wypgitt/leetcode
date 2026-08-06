package leetcode

// CountPrimes204 is the Sieve of Eratosthenes. When p is prime, mark multiples
// from p*p because smaller multiples were marked by smaller primes.
//
// Time: O(n log log n). Space: O(n).
func CountPrimes204(n int) int {
	if n <= 2 {
		return 0
	}
	prime := make([]bool, n)
	for i := 2; i < n; i++ {
		prime[i] = true
	}
	for p := 2; p*p < n; p++ {
		if prime[p] {
			for m := p * p; m < n; m += p {
				prime[m] = false
			}
		}
	}
	count := 0
	for _, ok := range prime {
		if ok {
			count++
		}
	}
	return count
}
