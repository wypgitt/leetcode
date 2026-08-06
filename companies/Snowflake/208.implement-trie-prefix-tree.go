package leetcode

// Trie208 stores children in a map from byte to child node. This mirrors the
// Python dict implementation and supports arbitrary lowercase paths without a
// fixed array, while IsWord marks complete words.
type trieNode208 struct {
	children map[byte]*trieNode208
	isWord   bool
}
type Trie208 struct{ root *trieNode208 }

func Constructor208() Trie208 { return Trie208{root: &trieNode208{children: map[byte]*trieNode208{}}} }
func (t *Trie208) Insert(word string) {
	node := t.root
	for i := 0; i < len(word); i++ {
		ch := word[i]
		if node.children[ch] == nil {
			node.children[ch] = &trieNode208{children: map[byte]*trieNode208{}}
		}
		node = node.children[ch]
	}
	node.isWord = true
}
func (t *Trie208) Search(word string) bool {
	node := t.root
	for i := 0; i < len(word); i++ {
		node = node.children[word[i]]
		if node == nil {
			return false
		}
	}
	return node.isWord
}
func (t *Trie208) StartsWith(prefix string) bool {
	node := t.root
	for i := 0; i < len(prefix); i++ {
		node = node.children[prefix[i]]
		if node == nil {
			return false
		}
	}
	return true
}
