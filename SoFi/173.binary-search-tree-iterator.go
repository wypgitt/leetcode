package leetcode

// BSTIterator173 stores a stack of the path to the next inorder node. pushLeft
// descends left children; Next pops one node and then pushes its right subtree's
// left spine.
type BSTIterator173 struct{ stack []*TreeNode }

func Constructor173(root *TreeNode) BSTIterator173 {
	it := BSTIterator173{}
	it.pushLeft(root)
	return it
}
func (it *BSTIterator173) pushLeft(node *TreeNode) {
	for node != nil {
		it.stack = append(it.stack, node)
		node = node.Left
	}
}
func (it *BSTIterator173) Next() int {
	node := it.stack[len(it.stack)-1]
	it.stack = it.stack[:len(it.stack)-1]
	it.pushLeft(node.Right)
	return node.Val
}
func (it *BSTIterator173) HasNext() bool { return len(it.stack) > 0 }
