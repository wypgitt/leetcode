package leetcode

//
// @lc app=leetcode id=3918 lang=golang
//
// [3918] Sum of Primes Between Number and Its Reverse
//
// Notes
// Reverse n, sieve all primes up to max(n, reverse(n)), and build a prefix sum
// of prime values. The range answer is then prefix[right] - prefix[left-1].
// Time: O(R log log R). Space: O(R), where R is max(n, reverse(n)).
//
// @lc code=start

func SumOfPrimesInRange3918(n int) int {
	reversedN := reverseInt3918(n)
	left, right := n, reversedN
	if left > right {
		left, right = right, left
	}

	isPrime := sieve3918(right)
	prefix := make([]int, right+1)
	for value := 1; value <= right; value++ {
		prefix[value] = prefix[value-1]
		if isPrime[value] {
			prefix[value] += value
		}
	}
	if left > 0 {
		return prefix[right] - prefix[left-1]
	}
	return prefix[right]
}

func reverseInt3918(n int) int {
	reversed := 0
	for n > 0 {
		reversed = reversed*10 + n%10
		n /= 10
	}
	return reversed
}

func sieve3918(limit int) []bool {
	isPrime := make([]bool, limit+1)
	if limit < 2 {
		return isPrime
	}
	for i := 2; i <= limit; i++ {
		isPrime[i] = true
	}
	for p := 2; p*p <= limit; p++ {
		if isPrime[p] {
			for multiple := p * p; multiple <= limit; multiple += p {
				isPrime[multiple] = false
			}
		}
	}
	return isPrime
}

// @lc code=end
