package leetcode

//
// @lc app=leetcode id=604 lang=golang
//
// [604] Design Compressed String Iterator
//
// Notes
// Keep the compressed string index, current character, and remaining repeat
// count. HasNext lazily loads the next letter+count group when the current group
// is exhausted; Next consumes one character or returns a space when no group
// remains. Time: amortized O(1) per operation. Space: O(1).
//
// @lc code=start

type StringIterator604 struct {
	compressed  string
	index       int
	currentChar byte
	remaining   int
}

func NewStringIterator604(compressedString string) *StringIterator604 {
	return &StringIterator604{compressed: compressedString}
}

func (s *StringIterator604) Next() byte {
	if !s.HasNext() {
		return ' '
	}
	s.remaining--
	return s.currentChar
}

func (s *StringIterator604) HasNext() bool {
	if s.remaining > 0 {
		return true
	}
	s.loadNextGroup()
	return s.remaining > 0
}

func (s *StringIterator604) loadNextGroup() {
	if s.index >= len(s.compressed) {
		return
	}

	s.currentChar = s.compressed[s.index]
	s.index++
	count := 0
	for s.index < len(s.compressed) && '0' <= s.compressed[s.index] && s.compressed[s.index] <= '9' {
		count = count*10 + int(s.compressed[s.index]-'0')
		s.index++
	}
	s.remaining = count
}

// @lc code=end
