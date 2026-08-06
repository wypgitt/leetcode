package leetcode

import (
	"container/heap"
	"sort"
)

type endHeap253 []int

func (h endHeap253) Len() int           { return len(h) }
func (h endHeap253) Less(i, j int) bool { return h[i] < h[j] }
func (h endHeap253) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *endHeap253) Push(x any)        { *h = append(*h, x.(int)) }
func (h *endHeap253) Pop() any          { old := *h; x := old[len(old)-1]; *h = old[:len(old)-1]; return x }

// MinMeetingRooms253 sorts meetings by start and keeps a min-heap of active end
// times. Meetings whose end <= current start free a room; heap size is rooms in
// use, and the maximum size is the answer.
//
// Time: O(n log n). Space: O(n).
func MinMeetingRooms253(intervals [][]int) int {
	if len(intervals) == 0 {
		return 0
	}
	sort.Slice(intervals, func(i, j int) bool { return intervals[i][0] < intervals[j][0] })
	h := &endHeap253{}
	heap.Init(h)
	best := 0
	for _, in := range intervals {
		start, end := in[0], in[1]
		for h.Len() > 0 && (*h)[0] <= start {
			heap.Pop(h)
		}
		heap.Push(h, end)
		best = maxInt(best, h.Len())
	}
	return best
}
