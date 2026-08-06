package leetcode

// WordDictionary211 is a trie with DFS search. The '.' wildcard branches to all
// child nodes except terminal markers, represented here by IsWord on the node.
type wordNode211 struct {
	children map[byte]*wordNode211
	isWord   bool
}
type WordDictionary211 struct{ root *wordNode211 }

func Constructor211() WordDictionary211 {
	return WordDictionary211{root: &wordNode211{children: map[byte]*wordNode211{}}}
}
func (w *WordDictionary211) AddWord(word string) {
	node := w.root
	for i := 0; i < len(word); i++ {
		ch := word[i]
		if node.children[ch] == nil {
			node.children[ch] = &wordNode211{children: map[byte]*wordNode211{}}
		}
		node = node.children[ch]
	}
	node.isWord = true
}
func (w *WordDictionary211) Search(word string) bool {
	var dfs func(int, *wordNode211) bool
	dfs = func(i int, node *wordNode211) bool {
		if i == len(word) {
			return node.isWord
		}
		ch := word[i]
		if ch == '.' {
			for _, child := range node.children {
				if dfs(i+1, child) {
					return true
				}
			}
			return false
		}
		child := node.children[ch]
		return child != nil && dfs(i+1, child)
	}
	return dfs(0, w.root)
}
