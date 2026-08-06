package leetcode

//
// @lc app=leetcode id=3885 lang=golang
//
// [3885] Design Event Manager
//
// Notes
// Keep the active priority for each event in a map and push every update into a
// heap. pollHighest lazily discards stale heap entries whose priority no longer
// matches the map. container/heap is Go's standard priority-queue interface.
// Update: O(log n). Poll amortized O(log n). Space: O(n+updates).
//
// @lc code=start

import "container/heap"

type eventItem3885 struct {
	priority int
	eventID  int
}

type eventHeap3885 []eventItem3885

func (h eventHeap3885) Len() int { return len(h) }
func (h eventHeap3885) Less(i, j int) bool {
	if h[i].priority != h[j].priority {
		return h[i].priority > h[j].priority
	}
	return h[i].eventID < h[j].eventID
}
func (h eventHeap3885) Swap(i, j int) { h[i], h[j] = h[j], h[i] }
func (h *eventHeap3885) Push(x any)   { *h = append(*h, x.(eventItem3885)) }
func (h *eventHeap3885) Pop() any {
	old := *h
	item := old[len(old)-1]
	*h = old[:len(old)-1]
	return item
}

type EventManager3885 struct {
	activePriority map[int]int
	events         eventHeap3885
}

func NewEventManager3885(events [][]int) *EventManager3885 {
	manager := &EventManager3885{
		activePriority: map[int]int{},
		events:         eventHeap3885{},
	}
	for _, event := range events {
		eventID, priority := event[0], event[1]
		manager.activePriority[eventID] = priority
		manager.events = append(manager.events, eventItem3885{priority: priority, eventID: eventID})
	}
	heap.Init(&manager.events)
	return manager
}

func (e *EventManager3885) UpdatePriority(eventID int, newPriority int) {
	e.activePriority[eventID] = newPriority
	heap.Push(&e.events, eventItem3885{priority: newPriority, eventID: eventID})
}

func (e *EventManager3885) PollHighest() int {
	for len(e.events) > 0 {
		item := heap.Pop(&e.events).(eventItem3885)
		if priority, ok := e.activePriority[item.eventID]; ok && priority == item.priority {
			delete(e.activePriority, item.eventID)
			return item.eventID
		}
	}
	return -1
}

// @lc code=end
