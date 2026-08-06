package leetcode

//
// @lc app=leetcode id=2617 lang=golang
//
// [2617] Minimum Number of Visited Cells in a Grid
//
// --- Notes (problem, modeling, backward DP, segment tree, merge rule, complexity, edges, interview) ---
//
// Problem restatement
// m x n grid `grid`. Start at (0, 0). From (i, j) you may move to:
//   - (i, k) for any integer k with j < k <= j + grid[i][j]   (same row, jump right),
//   - (k, j) for any integer k with i < k <= i + grid[i][j]   (same column, jump down).
// Each move lands on a new cell; count VISITED cells along the path (the starting cell counts).
// Return the minimum possible visited-cell count to reach (m-1, n-1), or -1 if unreachable.
//
// Modeling
// Directed graph on cells (each jump is an edge). Edge weights are uniform if we count “extra”
// cells per jump — minimizing visited cells from start to goal equals shortest path where each
// edge from (i,j) to a farther cell costs +1 visited cell for the new cell (prefix length grows by 1).
//
// Backward DP (reverse relaxation)
// Let f(i, j) be the minimum visited cells needed when starting from (i, j), counting (i, j) itself.
// Then:
//   f(i, j) = 1 + min( min_{k in reachable right range} f(i, k),
//                      min_{k in reachable down  range} f(k, j) )
// Process cells from bottom-right to top-left so the needed future states are already known.
//
// Range-min queries
// For each row and each column maintain a segment tree with point updates and range-min queries.
//
// Time complexity
// O(m n (log n + log m)).
//
// --- end notes ---
//
// @lc code=start

type _segTree2617 struct {
	inf  int
	size int
	t    []int
}

func _newSegTree2617(n int, inf int) *_segTree2617 {
	sz := 1
	for sz < n {
		sz <<= 1
	}
	t := make([]int, 2*sz)
	for i := range t {
		t[i] = inf
	}
	return &_segTree2617{inf: inf, size: sz, t: t}
}

func (st *_segTree2617) update(pos int, val int) {
	i := pos + st.size
	st.t[i] = val
	for i >>= 1; i > 0; i >>= 1 {
		l, r := st.t[i<<1], st.t[i<<1|1]
		if l < r {
			st.t[i] = l
		} else {
			st.t[i] = r
		}
	}
}

func (st *_segTree2617) query(l int, r int) int {
	if l > r {
		return st.inf
	}
	l += st.size
	r += st.size
	res := st.inf
	for l <= r {
		if (l & 1) == 1 {
			if st.t[l] < res {
				res = st.t[l]
			}
			l++
		}
		if (r & 1) == 0 {
			if st.t[r] < res {
				res = st.t[r]
			}
			r--
		}
		l >>= 1
		r >>= 1
	}
	return res
}

// MinimumVisitedCells2617 returns the minimum number of visited cells to reach bottom-right.
func MinimumVisitedCells2617(grid [][]int) int {
	m, n := len(grid), len(grid[0])
	const INF = 1_000_000_000

	minInt := func(a, b int) int {
		if a < b {
			return a
		}
		return b
	}

	rows := make([]*_segTree2617, m)
	for i := 0; i < m; i++ {
		rows[i] = _newSegTree2617(n, INF)
	}
	cols := make([]*_segTree2617, n)
	for j := 0; j < n; j++ {
		cols[j] = _newSegTree2617(m, INF)
	}

	rows[m-1].update(n-1, 1)
	cols[n-1].update(m-1, 1)

	for i := m - 1; i >= 0; i-- {
		for j := n - 1; j >= 0; j-- {
			if grid[i][j] == 0 {
				continue
			}
			rMax := minInt(n-1, j+grid[i][j])
			dMax := minInt(m-1, i+grid[i][j])

			mr := rows[i].query(j+1, rMax)
			md := cols[j].query(i+1, dMax)
			cur := rows[i].query(j, j)
			cv := cols[j].query(i, i)
			if cv < cur {
				cur = cv
			}

			newVal := cur
			if mr < INF || md < INF {
				best := mr
				if md < best {
					best = md
				}
				if best+1 < newVal {
					newVal = best + 1
				}
			}
			rows[i].update(j, newVal)
			cols[j].update(i, newVal)
		}
	}

	res := rows[0].query(0, 0)
	if res >= INF {
		return -1
	}
	return res
}

// @lc code=end

