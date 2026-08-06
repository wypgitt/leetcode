package leetcode

import "strconv"

// TreeNode is the standard LeetCode binary-tree node used by several problems.
type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

// NestedInteger is a local stand-in for LeetCode's provided NestedInteger API.
type NestedInteger struct {
	isInt bool
	value int
	list  []NestedInteger
}

func NewNestedInteger() NestedInteger { return NestedInteger{list: []NestedInteger{}} }

func NewNestedIntegerWithValue(value int) NestedInteger {
	return NestedInteger{isInt: true, value: value}
}

func (ni *NestedInteger) IsInteger() bool { return ni.isInt }
func (ni *NestedInteger) GetInteger() int { return ni.value }
func (ni *NestedInteger) SetInteger(value int) {
	ni.isInt = true
	ni.value = value
	ni.list = nil
}
func (ni *NestedInteger) Add(elem NestedInteger) {
	if ni.isInt {
		ni.isInt = false
		ni.list = nil
	}
	ni.list = append(ni.list, elem)
}
func (ni *NestedInteger) GetList() []NestedInteger { return ni.list }

// QuadNode is the standard LeetCode quad-tree node for problem 558.
type QuadNode struct {
	Val         bool
	IsLeaf      bool
	TopLeft     *QuadNode
	TopRight    *QuadNode
	BottomLeft  *QuadNode
	BottomRight *QuadNode
}

func absInt(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func reverseString(s string) string {
	b := []byte(s)
	for i, j := 0, len(b)-1; i < j; i, j = i+1, j-1 {
		b[i], b[j] = b[j], b[i]
	}
	return string(b)
}

func intToString(x int) string { return strconv.Itoa(x) }
