package leetcode

import "sort"

type beautifulPairsPoint2613 struct {
	x   int
	y   int
	idx int
}

func BeautifulPair2613(nums1 []int, nums2 []int) []int {
	n := len(nums1)

	type key struct{ x, y int }
	groups := make(map[key][]int, n)
	for i := 0; i < n; i++ {
		k := key{nums1[i], nums2[i]}
		groups[k] = append(groups[k], i)
	}

	bestDupA, bestDupB := -1, -1
	for _, idxs := range groups {
		if len(idxs) >= 2 {
			a, b := idxs[0], idxs[1]
			if bestDupA == -1 || a < bestDupA || (a == bestDupA && b < bestDupB) {
				bestDupA, bestDupB = a, b
			}
		}
	}
	if bestDupA != -1 {
		return []int{bestDupA, bestDupB}
	}

	const inf int64 = 1<<62 - 1

	pts := make([]beautifulPairsPoint2613, n)
	for i := 0; i < n; i++ {
		pts[i] = beautifulPairsPoint2613{x: nums1[i], y: nums2[i], idx: i}
	}
	sort.Slice(pts, func(i, j int) bool {
		if pts[i].x != pts[j].x {
			return pts[i].x < pts[j].x
		}
		if pts[i].y != pts[j].y {
			return pts[i].y < pts[j].y
		}
		return pts[i].idx < pts[j].idx
	})

	manhattan := func(a, b beautifulPairsPoint2613) int64 {
		dx := int64(a.x - b.x)
		if dx < 0 {
			dx = -dx
		}
		dy := int64(a.y - b.y)
		if dy < 0 {
			dy = -dy
		}
		return dx + dy
	}

	better := func(d1 int64, i1, j1 int, d2 int64, i2, j2 int) bool {
		if d2 < d1 {
			return true
		}
		if d2 > d1 {
			return false
		}
		if i2 != i1 {
			return i2 < i1
		}
		return j2 < j1
	}

	var dfs func(l, r int) (int64, int, int)
	dfs = func(l, r int) (int64, int, int) {
		if l >= r {
			return inf, -1, -1
		}
		m := (l + r) >> 1
		xMid := pts[m].x

		d1, a1, b1 := dfs(l, m)
		d2, a2, b2 := dfs(m+1, r)
		if better(d1, a1, b1, d2, a2, b2) {
			d1, a1, b1 = d2, a2, b2
		}

		strip := make([]beautifulPairsPoint2613, 0, r-l+1)
		for i := l; i <= r; i++ {
			dx := pts[i].x - xMid
			if dx < 0 {
				dx = -dx
			}
			if int64(dx) <= d1 {
				strip = append(strip, pts[i])
			}
		}
		sort.Slice(strip, func(i, j int) bool { return strip[i].y < strip[j].y })

		for i := 0; i < len(strip); i++ {
			for j := i + 1; j < len(strip); j++ {
				if int64(strip[j].y-strip[i].y) > d1 {
					break
				}
				ii, jj := strip[i].idx, strip[j].idx
				if ii > jj {
					ii, jj = jj, ii
				}
				d := manhattan(strip[i], strip[j])
				if better(d1, a1, b1, d, ii, jj) {
					d1, a1, b1 = d, ii, jj
				}
			}
		}
		return d1, a1, b1
	}

	_, pi, pj := dfs(0, n-1)
	return []int{pi, pj}
}

// @lc code=end

