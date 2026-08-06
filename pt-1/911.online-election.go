package leetcode

//
// @lc app=leetcode id=911 lang=golang
//
// [911] Online Election
//

// =============================================================================
// INTERVIEW: ELEVATOR PITCH (~30 seconds)
// =============================================================================
//
// "Votes arrive at strictly increasing timestamps. After each ballot we know who is
// ahead: whoever has the most votes; on a tie, whoever got a vote **most recently**.
// That's a single forward simulation updating counts and the current leader with one
// comparison per vote. Queries ask 'who leads at time t?' — that's **prefix-only**
// information, so we **snapshot the leader after each vote** and answer queries by
// binary-searching the last vote at or before `t`. Preprocessing O(n), each query
// O(log n)."
//
// =============================================================================
// PROBLEM (PRECISE)
// =============================================================================
//
// • `persons[i]` receives one vote at time `times[i]`.
// • `times` is strictly increasing (typical LeetCode constraint).
// • Query `q(t)`: among all votes cast at times **≤ t**, which candidate has the
//   most votes? **Tie-break:** if multiple have the same maximum count, return the
//   candidate who received a vote **most recently** among those tied at the top.
//
// =============================================================================
// WHY PREFIX SNAPSHOTS + BINARY SEARCH?
// =============================================================================
//
// The leader depends only on votes with timestamp ≤ t — a **prefix** of the
// chronological vote stream. Between consecutive vote times the leader does not
// change. Therefore:
//
//   leader_at(t) = leader_immediately_after_processing_the_last_vote_with_time_≤t
//
// Precompute `leaders[k]` = winner after applying votes `0 .. k` inclusive.
// For query `t`, find largest index `k` with `times[k] ≤ t` (binary search on sorted
// `times`), then return `leaders[k]`.
//
// =============================================================================
// TIE-BREAKING — SINGLE PASS UPDATE RULE
// =============================================================================
//
// Process votes in order. Maintain `cnt[p]` = votes for person `p`, and `leader`.
//
// After recording vote for person `p` at this step:
//
//       if cnt[p] >= cnt[leader]:
//           leader = p
//
// **Why this encodes “most recent wins ties”:**
// When we increment `p`, only `p`’s count can increase. If after incrementing,
// `cnt[p]` **strictly exceeds** `cnt[leader]`, `p` is ahead. If `cnt[p] == cnt[leader]`,
// then `p` is tied with the previous leader’s count — but `p` **just received** a vote,
// so among everyone tied at that count, `p` is the most recently active → becomes
// leader. If `cnt[p] < cnt[leader]`, the incumbent stays ahead.
//
// No need to track “last vote time” per person separately; processing order makes
// the last increment resolve ties correctly.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// • **`counts`** — map from person id → vote count. Only persons who
//   appear need entries → **O(unique candidates)** entries, ≤ **O(n)**.
// • **`times`** — stored for queries (sorted input enables binary search).
// • **`leaders`** — slice parallel to `times`, length **n**. **O(n)** space.
//
// Alternatives: **array** for counts if person ids bounded small (not assumed here).
//
// =============================================================================
// TIME & SPACE COMPLEXITY
// =============================================================================
//
// **`__init__`:** One scan over **n** votes — **O(n)** time, **O(n)** space for
// `leaders` plus map.
//
// **`q(t)`:** Binary search on `times` — **O(log n)** time, **O(1)** extra space.
//
// Total across **q** queries: **O(q log n)** online time after **O(n)** preprocess.
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// • **Single vote** — `leaders` length 1; any `t ≥ times[0]` returns that winner.
// • **All votes same person** — leader never changes after first ballot (still update
//   rule holds).
// • **Query `t` before first vote** — problem constraints usually guarantee
//   `times[0] ≤ t`; if not, define behavior (bisect index −1 — avoid by constraint).
// • **Query `t` after last vote** — bisect returns last index; leader is final winner.
//
// =============================================================================
// TESTING (UNIT / PROPERTY)
// =============================================================================
//
// • Match brute force for random small instances: for each `t`, recount votes with
//   `time ≤ t`, resolve ties by scanning votes in order for max frequency then last
//   occurrence among tied maxima — compare to `q(t)`.
// • Known samples from statement (if provided): replay timeline.
//
// =============================================================================
// IMPROVEMENTS / VARIANTS
// =============================================================================
//
// • If **many queries** and **discrete small time universe**, **bucket** answers by
//   time — rarely needed; binary search is standard.
// • **Persistence:** snapshots are already an implicit persistent prefix structure.
//
// =============================================================================

// @lc code=start

import "sort"

// TopVotedCandidate911 precomputes the election winner after each recorded vote, then answers
// time-queries via binary search on vote timestamps.
type TopVotedCandidate911 struct {
	times   []int
	leaders []int
}

// NewTopVotedCandidate911 constructs from parallel persons and times slices.
//
// persons[i] receives one vote at times[i]; times strictly increases.
func NewTopVotedCandidate911(persons, times []int) *TopVotedCandidate911 {
	n := len(times)
	cnt := make(map[int]int)
	leader := persons[0]
	cnt[leader] = 1
	leaders := make([]int, n)
	leaders[0] = leader

	for i := 1; i < n; i++ {
		p := persons[i]
		cnt[p]++
		if cnt[p] >= cnt[leader] {
			leader = p
		}
		leaders[i] = leader
	}

	return &TopVotedCandidate911{times: times, leaders: leaders}
}

// Q returns the winning candidate among all votes cast at time <= t.
func (t *TopVotedCandidate911) Q(query int) int {
	// Largest index i with times[i] <= t  ==  bisect_right - 1
	i := sort.Search(len(t.times), func(j int) bool {
		return t.times[j] > query
	}) - 1
	return t.leaders[i]
}

// Your TopVotedCandidate object will be instantiated and called as such:
// obj := NewTopVotedCandidate911(persons, times)
// param_1 := obj.Q(t)
// @lc code=end
