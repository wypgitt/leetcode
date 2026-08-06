package leetcode

import "container/heap"

type fraction786 struct{ i, j int }
type fractionHeap786 struct {
	arr []int
	h   []fraction786
}

func (fh fractionHeap786) Len() int { return len(fh.h) }
func (fh fractionHeap786) Less(a, b int) bool {
	x, y := fh.h[a], fh.h[b]
	return fh.arr[x.i]*fh.arr[y.j] < fh.arr[y.i]*fh.arr[x.j]
}
func (fh fractionHeap786) Swap(i, j int) { fh.h[i], fh.h[j] = fh.h[j], fh.h[i] }
func (fh *fractionHeap786) Push(x any)   { fh.h = append(fh.h, x.(fraction786)) }
func (fh *fractionHeap786) Pop() any {
	old := fh.h
	x := old[len(old)-1]
	fh.h = old[:len(old)-1]
	return x
}

// KthSmallestPrimeFraction786 merges sorted fraction lists by denominator. For a
// fixed denominator arr[j], fractions arr[0]/arr[j], arr[1]/arr[j], ... are
// increasing, so a min-heap over the current head of each list yields kth order.
//
// Go data structure note: container/heap needs Len/Less/Swap/Push/Pop methods;
// Less cross-multiplies integers to avoid floating-point precision issues.
//
// Time: O((n+k) log n). Space: O(n).
func KthSmallestPrimeFraction786(arr []int, k int) []int {
	n := len(arr)
	fh := &fractionHeap786{arr: arr, h: make([]fraction786, 0, n-1)}
	for j := 1; j < n; j++ {
		fh.h = append(fh.h, fraction786{0, j})
	}
	heap.Init(fh)
	for ; k > 1; k-- {
		cur := heap.Pop(fh).(fraction786)
		if cur.i+1 < cur.j {
			heap.Push(fh, fraction786{cur.i + 1, cur.j})
		}
	}
	cur := heap.Pop(fh).(fraction786)
	return []int{arr[cur.i], arr[cur.j]}
}
