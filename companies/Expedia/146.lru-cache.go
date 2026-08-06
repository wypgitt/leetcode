package leetcode

// lruNode146 is a doubly-linked-list node for LRUCache146.
type lruNode146 struct {
	key, value int
	prev, next *lruNode146
}

// LRUCache146 combines a hash map for O(1) key lookup with a doubly linked list
// ordered from least recently used after head to most recently used before tail.
type LRUCache146 struct {
	capacity   int
	nodes      map[int]*lruNode146
	head, tail *lruNode146
}

func Constructor146(capacity int) LRUCache146 {
	h, t := &lruNode146{}, &lruNode146{}
	h.next = t
	t.prev = h
	return LRUCache146{capacity: capacity, nodes: map[int]*lruNode146{}, head: h, tail: t}
}
func (c *LRUCache146) remove(n *lruNode146) { n.prev.next = n.next; n.next.prev = n.prev }
func (c *LRUCache146) addBack(n *lruNode146) {
	last := c.tail.prev
	last.next = n
	n.prev = last
	n.next = c.tail
	c.tail.prev = n
}
func (c *LRUCache146) markUsed(n *lruNode146) { c.remove(n); c.addBack(n) }
func (c *LRUCache146) Get(key int) int {
	n := c.nodes[key]
	if n == nil {
		return -1
	}
	c.markUsed(n)
	return n.value
}
func (c *LRUCache146) Put(key int, value int) {
	if n := c.nodes[key]; n != nil {
		n.value = value
		c.markUsed(n)
		return
	}
	n := &lruNode146{key: key, value: value}
	c.nodes[key] = n
	c.addBack(n)
	if len(c.nodes) > c.capacity {
		lru := c.head.next
		c.remove(lru)
		delete(c.nodes, lru.key)
	}
}
