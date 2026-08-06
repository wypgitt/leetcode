package leetcode

//
// @lc app=leetcode id=3841 lang=golang
//
// [3841] Palindromic Path Queries in a Tree
//
// Notes
// A path can be rearranged into a palindrome iff at most one character has odd
// frequency. Store each node as a 26-bit mask and answer path XOR queries with
// heavy-light decomposition plus a segment tree. Updates change one leaf in the
// segment tree. Slices implement the HLD arrays; the segment tree is iterative.
// Time: O((n+q) log^2 n). Space: O(n).
//
// @lc code=start

import (
	"strconv"
	"strings"
)

type segmentTreeXor3841 struct {
	size int
	tree []int
}

func newSegmentTreeXor3841(values []int) *segmentTreeXor3841 {
	size := 1
	for size < len(values) {
		size <<= 1
	}
	tree := make([]int, 2*size)
	for i, value := range values {
		tree[size+i] = value
	}
	for i := size - 1; i > 0; i-- {
		tree[i] = tree[2*i] ^ tree[2*i+1]
	}
	return &segmentTreeXor3841{size: size, tree: tree}
}

func (s *segmentTreeXor3841) update(index int, value int) {
	index += s.size
	s.tree[index] = value
	index /= 2
	for index > 0 {
		s.tree[index] = s.tree[2*index] ^ s.tree[2*index+1]
		index /= 2
	}
}

func (s *segmentTreeXor3841) query(left int, right int) int {
	left += s.size
	right += s.size
	answer := 0
	for left <= right {
		if left&1 == 1 {
			answer ^= s.tree[left]
			left++
		}
		if right&1 == 0 {
			answer ^= s.tree[right]
			right--
		}
		left /= 2
		right /= 2
	}
	return answer
}

func PalindromePath3841(n int, edges [][]int, s string, queries []string) []bool {
	graph := make([][]int, n)
	for _, edge := range edges {
		u, v := edge[0], edge[1]
		graph[u] = append(graph[u], v)
		graph[v] = append(graph[v], u)
	}

	parent := make([]int, n)
	depth := make([]int, n)
	for i := range parent {
		parent[i] = -1
	}
	order := []int{0}
	for idx := 0; idx < len(order); idx++ {
		node := order[idx]
		for _, nei := range graph[node] {
			if nei == parent[node] {
				continue
			}
			parent[nei] = node
			depth[nei] = depth[node] + 1
			order = append(order, nei)
		}
	}

	size := make([]int, n)
	heavy := make([]int, n)
	for i := range size {
		size[i] = 1
		heavy[i] = -1
	}
	for i := len(order) - 1; i >= 0; i-- {
		node := order[i]
		bestSize := 0
		for _, nei := range graph[node] {
			if parent[nei] == node {
				size[node] += size[nei]
				if size[nei] > bestSize {
					bestSize = size[nei]
					heavy[node] = nei
				}
			}
		}
	}

	head := make([]int, n)
	pos := make([]int, n)
	base := make([]int, n)
	currentPos := 0
	stack := [][2]int{{0, 0}}
	for len(stack) > 0 {
		item := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		start, chainHead := item[0], item[1]
		for node := start; node != -1; node = heavy[node] {
			head[node] = chainHead
			pos[node] = currentPos
			base[currentPos] = mask3841(s[node])
			currentPos++

			for _, nei := range graph[node] {
				if parent[nei] == node && nei != heavy[node] {
					stack = append(stack, [2]int{nei, nei})
				}
			}
		}
	}

	seg := newSegmentTreeXor3841(base)
	chars := []byte(s)
	answer := []bool{}

	for _, raw := range queries {
		parts := strings.Fields(raw)
		if parts[0] == "update" {
			node, _ := strconv.Atoi(parts[1])
			chars[node] = parts[2][0]
			seg.update(pos[node], mask3841(parts[2][0]))
		} else {
			u, _ := strconv.Atoi(parts[1])
			v, _ := strconv.Atoi(parts[2])
			mask := pathXor3841(u, v, head, parent, depth, pos, seg)
			answer = append(answer, mask&(mask-1) == 0)
		}
	}

	return answer
}

func pathXor3841(u, v int, head, parent, depth, pos []int, seg *segmentTreeXor3841) int {
	answer := 0
	for head[u] != head[v] {
		if depth[head[u]] < depth[head[v]] {
			u, v = v, u
		}
		answer ^= seg.query(pos[head[u]], pos[u])
		u = parent[head[u]]
	}
	if depth[u] > depth[v] {
		u, v = v, u
	}
	answer ^= seg.query(pos[u], pos[v])
	return answer
}

func mask3841(ch byte) int {
	return 1 << int(ch-'a')
}

// @lc code=end
