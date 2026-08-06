package leetcode

import (
	"container/list"
	"sort"
)

//
// @lc app=leetcode id=950 lang=golang
//
// [950] Reveal Cards In Increasing Order
//

// --- Interview notes (process simulation, deque, inverse assignment, complexity) ---
//
// Problem
// **`deck`** has **`n`** distinct integers (cards). **Reorder** the deck so that if we run this procedure until empty:
// 1. **Reveal** the **top** card (record its value).
// 2. **Move** the **next** top card to the **bottom** of the deck.
// 3. Repeat.
// …the **revealed sequence** is **strictly increasing** (when **`deck`** is sorted ascending, that sequence should be **`deck[0],
// deck[1], …`** in sorted order — i.e. smallest revealed first, then next smallest, etc.).
//
// Equivalently
// Fix the **positions** in the initial deck that will be revealed **1st, 2nd, …, n-th**. Those positions must receive values in
// **sorted order**. So we need a **bijection**: **k-th smallest card** → **position revealed at step k**.
//
// Simulation — assign sorted cards to revelation order
// 1. **`sorted(deck)`** — cards revealed in this order left-to-right in the sorted list.
// 2. Maintain a **`deque`** of **indices** (indices into the **answer array**, i.e. **slots** in the final deck). The deque models the
//    **relative order of still-unfilled slots** as the physical process would visit them: **front** = next slot that will be
//    **revealed** if it held the next card in the procedure—matching **“reveal top, move next to bottom”** on **positions**.
// 3. For each **`x`** in **`sorted(deck)`** (smallest first):
//    • **`pos = dq.popleft()`** — next revelation slot; set **`ans[pos] = x`**.
//    • If any slots remain, **`dq.append(dq.popleft())`** — the **next** slot in line goes to the **back**, matching “move top card to
//      bottom” on the **remaining** abstract deck of **unfilled positions**.
//
// Why this models the game
// Label unfilled positions by how the strip-deck operation cycles through them; the deque’s **pop-left / append-left-popped** pattern
// is exactly one reveal plus one **rotate-next-to-back** on the remaining slots—without needing to physically simulate card values,
// only **slot order**.
//
// Data structures
// **`collections.deque`** — **`O(1)`** pops from front and push to back (**`O(n)`** total operations).
//
// Time complexity **`O(n log n)`** — sorting dominates; deque pass is **`O(n)`**.
//
// Space complexity **`O(n)`** for answer + deque + sorted copy (or sort in place if we copied — here **`sorted(deck)`** uses **`O(n)`**
// extra).
//
// Edge cases
// • **`n == 1`** — **`deque`** empty after one assignment; **no** second **`append`** (guard **`if dq:`** before rotating).
//
// Tests (LeetCode)
// • **`[17,13,11,2,3,5,7]`** → **`[2,13,3,11,5,17,7]`** (reveal order **`[2,3,5,7,11,13,17]`**).
//
// Improvements
// • **Inverse indexing** is possible (derive positions by formula / recursion on **`n`**) but **deque simulation** is clear and fast to
//   implement in interviews.
//
// --- end notes ---

// @lc code=start

func DeckRevealedIncreasing950(deck []int) []int {
	cards := append([]int(nil), deck...)
	sort.Ints(cards)
	n := len(cards)
	dq := list.New()
	for i := 0; i < n; i++ {
		dq.PushBack(i)
	}
	ans := make([]int, n)
	for _, x := range cards {
		e := dq.Front()
		pos := e.Value.(int)
		dq.Remove(e)
		ans[pos] = x
		if dq.Len() > 0 {
			e2 := dq.Front()
			v := e2.Value.(int)
			dq.Remove(e2)
			dq.PushBack(v)
		}
	}
	return ans
}

// @lc code=end
