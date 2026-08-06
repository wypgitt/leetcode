package leetcode

// Intersect558 computes the logical OR of two quad trees. True leaves
// short-circuit to true; false leaves return the other subtree. Internal nodes
// recurse on corresponding quadrants and are compressed if all children become
// equal leaves.
//
// Go data structure note: *QuadNode pointers allow large unchanged subtrees to
// be returned directly when OR with false does not alter them.
//
// Time: O(m) inspected node pairs, often less due to short-circuiting.
// Space: O(h) recursion plus output nodes.
func Intersect558(quadTree1 *QuadNode, quadTree2 *QuadNode) *QuadNode {
	if quadTree1.IsLeaf {
		if quadTree1.Val {
			return &QuadNode{Val: true, IsLeaf: true}
		}
		return quadTree2
	}
	if quadTree2.IsLeaf {
		if quadTree2.Val {
			return &QuadNode{Val: true, IsLeaf: true}
		}
		return quadTree1
	}
	children := []*QuadNode{
		Intersect558(quadTree1.TopLeft, quadTree2.TopLeft),
		Intersect558(quadTree1.TopRight, quadTree2.TopRight),
		Intersect558(quadTree1.BottomLeft, quadTree2.BottomLeft),
		Intersect558(quadTree1.BottomRight, quadTree2.BottomRight),
	}
	allLeafSame := true
	for i := 1; i < 4; i++ {
		if !children[i].IsLeaf || !children[0].IsLeaf || children[i].Val != children[0].Val {
			allLeafSame = false
			break
		}
	}
	if allLeafSame {
		return &QuadNode{Val: children[0].Val, IsLeaf: true}
	}
	return &QuadNode{TopLeft: children[0], TopRight: children[1], BottomLeft: children[2], BottomRight: children[3]}
}
