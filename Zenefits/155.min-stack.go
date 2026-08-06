package leetcode

// MinStack155 stores each pushed value with the minimum value at or below that
// stack depth. This makes GetMin O(1) without a second stack.
type MinStack155 struct{ stack [][2]int }

func Constructor155() MinStack155 { return MinStack155{} }
func (s *MinStack155) Push(val int) {
	cur := val
	if len(s.stack) > 0 {
		cur = minInt(cur, s.stack[len(s.stack)-1][1])
	}
	s.stack = append(s.stack, [2]int{val, cur})
}
func (s *MinStack155) Pop()        { s.stack = s.stack[:len(s.stack)-1] }
func (s *MinStack155) Top() int    { return s.stack[len(s.stack)-1][0] }
func (s *MinStack155) GetMin() int { return s.stack[len(s.stack)-1][1] }
