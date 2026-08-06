package leetcode

// MinMutation433 runs BFS on the implicit graph of valid gene strings. Each edge
// changes one character, so the first time endGene is dequeued is the shortest
// mutation count.
//
// Go data structure note: map[string]bool provides O(1) membership for the bank
// and visited set; a slice with a moving head index is an efficient queue.
//
// Time: O(B*L*4), with L=8 in the constraints. Space: O(B).
func MinMutation433(startGene string, endGene string, bank []string) int {
	bankSet := map[string]bool{}
	for _, gene := range bank {
		bankSet[gene] = true
	}
	if !bankSet[endGene] {
		return -1
	}
	type item struct {
		gene  string
		steps int
	}
	choices := []byte{'A', 'C', 'G', 'T'}
	queue := []item{{startGene, 0}}
	seen := map[string]bool{startGene: true}
	for head := 0; head < len(queue); head++ {
		cur := queue[head]
		if cur.gene == endGene {
			return cur.steps
		}
		chars := []byte(cur.gene)
		for i, old := range chars {
			for _, ch := range choices {
				if ch == old {
					continue
				}
				chars[i] = ch
				next := string(chars)
				if bankSet[next] && !seen[next] {
					seen[next] = true
					queue = append(queue, item{next, cur.steps + 1})
				}
			}
			chars[i] = old
		}
	}
	return -1
}
