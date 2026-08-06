package leetcode

//
// @lc app=leetcode id=3845 lang=golang
//
// [3845] Maximum Subarray XOR With Bounded Range
//
// Notes
// Maintain a sliding window whose max-min is at most k using monotonic deques.
// Insert valid starting prefix XORs into a binary trie; for each right endpoint,
// querying the trie with the current prefix gives the best subarray XOR ending
// there. Trie nodes store counts so prefixes can be removed as the left boundary
// moves. Time: O(n * B). Space: O(n * B), B=15 here.
//
// @lc code=start

type binaryTrie3845 struct {
	child [][2]int
	count []int
}

func newBinaryTrie3845() *binaryTrie3845 {
	return &binaryTrie3845{
		child: [][2]int{{-1, -1}},
		count: []int{0},
	}
}

func (b *binaryTrie3845) insert(value int) {
	node := 0
	b.count[node]++
	for bitIndex := maxBit3845; bitIndex >= 0; bitIndex-- {
		bit := (value >> bitIndex) & 1
		next := b.child[node][bit]
		if next == -1 {
			next = len(b.child)
			b.child[node][bit] = next
			b.child = append(b.child, [2]int{-1, -1})
			b.count = append(b.count, 0)
		}
		node = next
		b.count[node]++
	}
}

func (b *binaryTrie3845) remove(value int) {
	node := 0
	b.count[node]--
	for bitIndex := maxBit3845; bitIndex >= 0; bitIndex-- {
		bit := (value >> bitIndex) & 1
		node = b.child[node][bit]
		b.count[node]--
	}
}

func (b *binaryTrie3845) maxXor(value int) int {
	node := 0
	best := 0
	for bitIndex := maxBit3845; bitIndex >= 0; bitIndex-- {
		bit := (value >> bitIndex) & 1
		preferred := bit ^ 1
		preferredNode := b.child[node][preferred]
		if preferredNode != -1 && b.count[preferredNode] > 0 {
			best |= 1 << bitIndex
			node = preferredNode
		} else {
			node = b.child[node][bit]
		}
	}
	return best
}

const maxBit3845 = 14

func MaxXor3845(nums []int, k int) int {
	trie := newBinaryTrie3845()
	maxQ := []int{}
	minQ := []int{}
	prefixes := []int{0}

	left := 0
	currentPrefix := 0
	answer := 0

	for right, value := range nums {
		trie.insert(prefixes[right])

		for len(maxQ) > 0 && nums[maxQ[len(maxQ)-1]] <= value {
			maxQ = maxQ[:len(maxQ)-1]
		}
		maxQ = append(maxQ, right)

		for len(minQ) > 0 && nums[minQ[len(minQ)-1]] >= value {
			minQ = minQ[:len(minQ)-1]
		}
		minQ = append(minQ, right)

		for nums[maxQ[0]]-nums[minQ[0]] > k {
			trie.remove(prefixes[left])
			if maxQ[0] == left {
				maxQ = maxQ[1:]
			}
			if minQ[0] == left {
				minQ = minQ[1:]
			}
			left++
		}

		currentPrefix ^= value
		if best := trie.maxXor(currentPrefix); best > answer {
			answer = best
		}
		prefixes = append(prefixes, currentPrefix)
	}

	return answer
}

// @lc code=end
