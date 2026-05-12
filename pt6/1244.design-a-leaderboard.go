package main

import "sort"

type Leaderboard struct {
	scores map[int]int
}

func Constructor() Leaderboard {
	return Leaderboard{scores: map[int]int{}}
}

func (l *Leaderboard) AddScore(playerId int, score int) {
	l.scores[playerId] += score
}

func (l *Leaderboard) Top(K int) int {
	values := make([]int, 0, len(l.scores))
	for _, score := range l.scores {
		values = append(values, score)
	}
	sort.Sort(sort.Reverse(sort.IntSlice(values)))

	total := 0
	for i := 0; i < K; i++ {
		total += values[i]
	}
	return total
}

func (l *Leaderboard) Reset(playerId int) {
	delete(l.scores, playerId)
}

/*
Explanation

The leaderboard keeps one hash map: player id -> current score. AddScore is a
map update, Reset deletes the player, and Top copies scores into a slice, sorts
descending, and sums the first K.

This is the right level of data structure for the constraints because there are
at most 1000 calls. A production leaderboard with frequent Top queries could
use a balanced tree, heap with lazy deletion, or Fenwick tree over bounded
scores, but that adds complexity without benefit here.

Go detail: sort.Reverse(sort.IntSlice(values)) gives descending numeric order.

Edge cases: adding a new player starts from zero; Reset is guaranteed to target
an existing player; K is guaranteed valid.

Time complexity: AddScore O(1), Reset O(1), Top O(n log n).
Space complexity: O(n).
*/
