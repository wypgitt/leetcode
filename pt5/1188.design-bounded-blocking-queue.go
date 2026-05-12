package main

import (
	"container/list"
	"sync"
)

type BoundedBlockingQueue struct {
	slots chan struct{}
	items chan struct{}
	mu    sync.Mutex
	data  *list.List
}

func Constructor(capacity int) BoundedBlockingQueue {
	slots := make(chan struct{}, capacity)
	for i := 0; i < capacity; i++ {
		slots <- struct{}{}
	}
	return BoundedBlockingQueue{
		slots: slots,
		items: make(chan struct{}, capacity),
		data:  list.New(),
	}
}

func (q *BoundedBlockingQueue) Enqueue(element int) {
	<-q.slots
	q.mu.Lock()
	q.data.PushFront(element)
	q.mu.Unlock()
	q.items <- struct{}{}
}

func (q *BoundedBlockingQueue) Dequeue() int {
	<-q.items
	q.mu.Lock()
	back := q.data.Back()
	value := back.Value.(int)
	q.data.Remove(back)
	q.mu.Unlock()
	q.slots <- struct{}{}
	return value
}

func (q *BoundedBlockingQueue) Size() int {
	q.mu.Lock()
	defer q.mu.Unlock()
	return q.data.Len()
}

