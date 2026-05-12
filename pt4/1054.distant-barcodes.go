package main

import "container/heap"

/*
1054. Distant Barcodes
*/
func rearrangeBarcodes(barcodes []int) []int {
	counts := make(map[int]int)
	for _, barcode := range barcodes {
		counts[barcode]++
	}

	items := make(barcodeMaxHeap, 0, len(counts))
	for barcode, count := range counts {
		items = append(items, barcodeEntry{count: count, value: barcode})
	}
	heap.Init(&items)

	result := make([]int, 0, len(barcodes))
	var previous barcodeEntry
	hasPrevious := false

	for items.Len() > 0 {
		current := heap.Pop(&items).(barcodeEntry)
		result = append(result, current.value)
		current.count--

		if hasPrevious && previous.count > 0 {
			heap.Push(&items, previous)
		}

		previous = current
		hasPrevious = true
	}

	return result
}

type barcodeEntry struct {
	count int
	value int
}

type barcodeMaxHeap []barcodeEntry

func (h barcodeMaxHeap) Len() int { return len(h) }

func (h barcodeMaxHeap) Less(i, j int) bool {
	if h[i].count == h[j].count {
		return h[i].value < h[j].value
	}
	return h[i].count > h[j].count
}

func (h barcodeMaxHeap) Swap(i, j int) { h[i], h[j] = h[j], h[i] }

func (h *barcodeMaxHeap) Push(x interface{}) {
	*h = append(*h, x.(barcodeEntry))
}

func (h *barcodeMaxHeap) Pop() interface{} {
	old := *h
	item := old[len(old)-1]
	*h = old[:len(old)-1]
	return item
}

/*
Interview Explanation

Core idea:
Always place the most frequent barcode that is not equal to the one just
placed. Holding the previous barcode out of the heap for one step enforces the
adjacency rule.

Go data structures:
- map[int]int counts barcode frequencies.
- container/heap is used with a custom max-heap type. Go's heap package is a
  min-heap by default, so Less is reversed by count.
- previous stores the last used barcode until a different barcode is placed.

Algorithm:
1. Count frequencies.
2. Build a max heap of (count, barcode).
3. Pop the most frequent currently allowed barcode and append it.
4. Decrement its count.
5. Push the previous barcode back after placing a different one.

Correctness:
The last placed barcode is absent from the heap during the next selection, so
two adjacent positions are never equal. Since a valid answer is guaranteed,
choosing the most frequent available barcode keeps high-frequency values spread
out and completes a valid rearrangement.

Complexity:
Let n be len(barcodes) and k be the number of distinct barcodes. Time is
O(n log k), and extra space is O(k) besides the result.

Edge cases:
- Length one returns that single barcode.
- Equal frequencies alternate naturally.
- A dominant barcode is repeatedly delayed by one position.
*/
