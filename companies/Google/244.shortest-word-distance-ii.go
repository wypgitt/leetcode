package leetcode

// WordDistance244 pre-indexes each word to its sorted occurrence positions.
// Shortest then merges two sorted position lists with two pointers, always
// advancing the smaller index to seek a closer pair.
type WordDistance244 struct{ positions map[string][]int }

func Constructor244(wordsDict []string) WordDistance244 {
	pos := map[string][]int{}
	for i, w := range wordsDict {
		pos[w] = append(pos[w], i)
	}
	return WordDistance244{positions: pos}
}
func (w *WordDistance244) Shortest(word1 string, word2 string) int {
	a, b := w.positions[word1], w.positions[word2]
	i, j, best := 0, 0, 1<<31-1
	for i < len(a) && j < len(b) {
		best = minInt(best, absInt(a[i]-b[j]))
		if a[i] < b[j] {
			i++
		} else {
			j++
		}
	}
	return best
}
