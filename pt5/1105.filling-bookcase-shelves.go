package main

func minHeightShelves(books [][]int, shelfWidth int) int {
	n := len(books)
	dp := make([]int, n+1)
	for i := 1; i <= n; i++ {
		dp[i] = 1 << 30
	}

	for i := 1; i <= n; i++ {
		width, height := 0, 0
		for j := i - 1; j >= 0; j-- {
			width += books[j][0]
			if width > shelfWidth {
				break
			}
			if books[j][1] > height {
				height = books[j][1]
			}
			if dp[j]+height < dp[i] {
				dp[i] = dp[j] + height
			}
		}
	}
	return dp[n]
}

