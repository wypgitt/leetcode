package main

func balancedString(s string) int {
	n, limit := len(s), len(s)/4
	count := map[byte]int{'Q': 0, 'W': 0, 'E': 0, 'R': 0}
	for i := 0; i < n; i++ {
		count[s[i]]++
	}
	if balancedOutside(count, limit) {
		return 0
	}

	ans, left := n, 0
	for right := 0; right < n; right++ {
		count[s[right]]--
		for left <= right && balancedOutside(count, limit) {
			if right-left+1 < ans {
				ans = right - left + 1
			}
			count[s[left]]++
			left++
		}
	}

	return ans
}

func balancedOutside(count map[byte]int, limit int) bool {
	return count['Q'] <= limit && count['W'] <= limit && count['E'] <= limit && count['R'] <= limit
}

/*
Explanation

The replacement window can contain anything, so the only requirement is that
the characters outside the window are already not over the limit n/4. Count the
whole string, then slide a window and subtract characters that enter it. When
all outside counts are <= n/4, the current window is sufficient; shrink it to
find the minimum.

The map stores outside-window counts. Since there are only four characters,
balancedOutside is constant time.

Edge cases: already balanced returns 0; a single overrepresented character is
handled by the same window; shrinking repeatedly ensures minimal length.

Time complexity: O(n).
Space complexity: O(1).
*/
