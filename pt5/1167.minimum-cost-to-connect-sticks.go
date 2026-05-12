package main

import "container/heap"

type intHeap []int

func (h intHeap) Len() int           { return len(h) }
func (h intHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h intHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *intHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}

func (h *intHeap) Pop() interface{} {
	old := *h
	value := old[len(old)-1]
	*h = old[:len(old)-1]
	return value
}

func connectSticks(sticks []int) int {
	h := intHeap(sticks)
	heap.Init(&h)
	total := 0

	for h.Len() > 1 {
		first := heap.Pop(&h).(int)
		second := heap.Pop(&h).(int)
		merged := first + second
		total += merged
		heap.Push(&h, merged)
	}

	return total
}
