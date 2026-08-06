package leetcode

// MaxProfit122 adds every positive day-to-day gain. With unlimited transactions,
// every upward edge can be captured independently and sums to the same profit as
// buying at each valley and selling at each peak.
//
// Time: O(n). Space: O(1).
func MaxProfit122(prices []int) int {
	profit := 0
	for i := 1; i < len(prices); i++ {
		if prices[i] > prices[i-1] {
			profit += prices[i] - prices[i-1]
		}
	}
	return profit
}
