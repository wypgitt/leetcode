package leetcode

//
// @lc app=leetcode id=3896 lang=golang
//
// [3896] Minimum Operations to Transform Array Into Alternating Prime
//
// Notes
// Sieve primes up to a safe bound and precompute nextPrime[x]. Even indices are
// increased to the next prime. Odd indices that are already prime are changed
// away from prime, costing 2 for value 2 and 1 otherwise, exactly as in the
// Python logic. Time: O(M log log M + n). Space: O(M).
//
// @lc code=start

func MinOperations3896(nums []int) int {
	maxValue := 0
	for _, value := range nums {
		if value > maxValue {
			maxValue = value
		}
	}
	limit := max3896(10, 2*maxValue+10)

	isPrime := make([]bool, limit+1)
	for i := range isPrime {
		isPrime[i] = true
	}
	isPrime[0] = false
	isPrime[1] = false
	for p := 2; p*p <= limit; p++ {
		if isPrime[p] {
			for multiple := p * p; multiple <= limit; multiple += p {
				isPrime[multiple] = false
			}
		}
	}

	nextPrime := make([]int, limit+1)
	closest := -1
	for value := limit; value >= 0; value-- {
		if isPrime[value] {
			closest = value
		}
		nextPrime[value] = closest
	}

	operations := 0
	for index, value := range nums {
		if index%2 == 0 {
			operations += nextPrime[value] - value
		} else if isPrime[value] {
			if value == 2 {
				operations += 2
			} else {
				operations++
			}
		}
	}
	return operations
}

func max3896(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// @lc code=end
