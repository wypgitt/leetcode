package main

func nthUglyNumber(n int, a int, b int, c int) int {
	gcd := func(x, y int64) int64 {
		for y != 0 {
			x, y = y, x%y
		}
		return x
	}
	lcm := func(x, y int64) int64 {
		return x / gcd(x, y) * y
	}

	aa, bb, cc := int64(a), int64(b), int64(c)
	ab := lcm(aa, bb)
	ac := lcm(aa, cc)
	bc := lcm(bb, cc)
	abc := lcm(ab, cc)

	countUgly := func(limit int64) int64 {
		return limit/aa + limit/bb + limit/cc - limit/ab - limit/ac - limit/bc + limit/abc
	}

	left, right := int64(1), int64(2_000_000_000)
	target := int64(n)
	for left < right {
		mid := left + (right-left)/2
		if countUgly(mid) >= target {
			right = mid
		} else {
			left = mid + 1
		}
	}
	return int(left)
}

