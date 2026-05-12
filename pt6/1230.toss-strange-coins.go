package main

func probabilityOfHeads(prob []float64, target int) float64 {
	dp := make([]float64, target+1)
	dp[0] = 1.0

	for _, p := range prob {
		for heads := target; heads >= 1; heads-- {
			dp[heads] = dp[heads]*(1-p) + dp[heads-1]*p
		}
		dp[0] *= 1 - p
	}

	return dp[target]
}

/*
Explanation

dp[h] is the probability of exactly h heads after processing some prefix of
coins. For a new coin with head probability p, h heads can come from old h
heads plus tails, or old h-1 heads plus heads.

The one-dimensional DP updates h from high to low so dp[h-1] is still from the
previous coin layer. This is the standard Go slice version of compressed 0/1
dynamic programming.

Edge cases: target == 0 only multiplies tail probabilities; probabilities 0
and 1 work naturally; impossible head counts remain 0.

Time complexity: O(n * target).
Space complexity: O(target).
*/
