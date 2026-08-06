package leetcode

// MyCircularDeque641 is a fixed-size circular buffer. front points to the first
// element and size determines both fullness and the rear position.
type MyCircularDeque641 struct {
	data        []int
	k           int
	front, size int
}

func Constructor641(k int) MyCircularDeque641 {
	return MyCircularDeque641{data: make([]int, k), k: k}
}

func (d *MyCircularDeque641) InsertFront(value int) bool {
	if d.IsFull() {
		return false
	}
	d.front = (d.front - 1 + d.k) % d.k
	d.data[d.front] = value
	d.size++
	return true
}

func (d *MyCircularDeque641) InsertLast(value int) bool {
	if d.IsFull() {
		return false
	}
	rear := (d.front + d.size) % d.k
	d.data[rear] = value
	d.size++
	return true
}

func (d *MyCircularDeque641) DeleteFront() bool {
	if d.IsEmpty() {
		return false
	}
	d.front = (d.front + 1) % d.k
	d.size--
	return true
}

func (d *MyCircularDeque641) DeleteLast() bool {
	if d.IsEmpty() {
		return false
	}
	d.size--
	return true
}

func (d *MyCircularDeque641) GetFront() int {
	if d.IsEmpty() {
		return -1
	}
	return d.data[d.front]
}

func (d *MyCircularDeque641) GetRear() int {
	if d.IsEmpty() {
		return -1
	}
	return d.data[(d.front+d.size-1)%d.k]
}

func (d *MyCircularDeque641) IsEmpty() bool { return d.size == 0 }
func (d *MyCircularDeque641) IsFull() bool  { return d.size == d.k }
