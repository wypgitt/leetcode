package leetcode

import "math/rand"

// RandomFlipMatrix519 implements lazy Fisher-Yates over flattened matrix
// indices. A map stores only positions whose current real index differs from
// the identity mapping, avoiding O(m*n) initialization.
type RandomFlipMatrix519 struct {
	m, n      int
	total     int
	remaining int
	remap     map[int]int
}

func Constructor519(m int, n int) RandomFlipMatrix519 {
	total := m * n
	return RandomFlipMatrix519{m: m, n: n, total: total, remaining: total, remap: map[int]int{}}
}

// Flip returns a uniformly random unflipped cell.
// Expected time: O(1). Space after f flips: O(f).
func (rfm *RandomFlipMatrix519) Flip() []int {
	pick := rand.Intn(rfm.remaining)
	rfm.remaining--
	actual, ok := rfm.remap[pick]
	if !ok {
		actual = pick
	}
	replacement, ok := rfm.remap[rfm.remaining]
	if !ok {
		replacement = rfm.remaining
	}
	rfm.remap[pick] = replacement
	return []int{actual / rfm.n, actual % rfm.n}
}

func (rfm *RandomFlipMatrix519) Reset() {
	rfm.remaining = rfm.total
	rfm.remap = map[int]int{}
}
