package leetcode

import "container/heap"

type minHeap215 []int

func (h minHeap215) Len() int           { return len(h) }
func (h minHeap215) Less(i, j int) bool { return h[i] < h[j] }
func (h minHeap215) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *minHeap215) Push(x any)        { *h = append(*h, x.(int)) }
func (h *minHeap215) Pop() any          { old := *h; x := old[len(old)-1]; *h = old[:len(old)-1]; return x }

// FindKthLargest215 keeps a min-heap of size k. After all numbers are processed,
// the heap root is the kth largest overall.
//
// Time: O(n log k). Space: O(k).
func FindKthLargest215(nums []int, k int) int {
	h := &minHeap215{}
	heap.Init(h)
	for _, x := range nums {
		heap.Push(h, x)
		if h.Len() > k {
			heap.Pop(h)
		}
	}
	return (*h)[0]
}
