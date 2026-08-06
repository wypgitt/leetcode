package leetcode

import "sort"

//
// @lc app=leetcode id=948 lang=golang
//
// [948] Bag Of Tokens
//

// --- Interview notes (greedy two pointers, exchange argument, complexity) ---
//
// Problem
// **`tokens`** are integer costs. Start with **`power`** points and **score** **`0`**. Each unused token can be played:
// • **Face up** — pay **`tokens[i]`** power; **score += 1`** (only if you can afford it).
// • **Face down** — requires **score ≥ 1** before playing; **gain `tokens[j]`** power and **score -= 1`**.
// Maximize **final** achievable score (actually maximum score **at any time** — problem asks maximum score you can obtain; playing face-down
// lowers score temporarily but may enable more face-ups later — we track **peak** score).
//
// Greedy strategy (sorted array + two pointers)
// Sort **`tokens`** ascending. Maintain **`lo`** (cheapest remaining) and **`hi`** (most expensive remaining).
// • **If `power ≥ tokens[lo]`** — buy the **cheapest** face-up: cheapest gives **maximum tokens per unit power** among remaining buys, so
//   greedy **locally optimal** for increasing score.
// • **Else**, if **`score > 0`** — sell the **most expensive** face-down: losing one score point while reclaiming **as much power as
//   possible** is the best trade if we must “borrow” power to continue.
// • **Else** — stuck (no power to buy, cannot sell), **stop**.
// Track **`answer = max(answer, score)`** after each successful face-up (only face-ups increase score).
//
// Why selling the largest token is optimal when forced
// Any face-down loses **exactly 1** score; choosing **`tokens[hi]`** maximizes power gained, enlarging the chance to afford more cheap
// face-ups afterward — standard exchange argument vs selling a cheaper remaining token.
//
// Why buying the smallest token first when affordable
// Spending power on the **minimum** cost buys **one** score while preserving **maximum residual power** for future moves compared to
// spending on a larger token first.
//
// Data structures
// **`list`** sorted in place (**`O(n log n)`**); **`lo`**, **`hi`** indices — **`O(1)`** extra.
//
// Time complexity **`O(n log n)`** from sorting; scan **`O(n)`**.
//
// Space complexity **`O(1)`** auxiliary if sorting in place (**`O(log n)`** sort stack depending on implementation).
//
// Edge cases
// • **Empty **`tokens`** → **`0`**.
// • **Never affordable** — **`power < min(tokens)`** and score stays **`0`** → **`0`**.
// • **Power buys everything** — monotone face-ups only.
//
// Tests (LeetCode)
// • **`tokens = [100], power = 50`** → **`0`** (cannot play face-up).
// • **`tokens = [100,200], power = 150`** → **`1`** (buy **`100`**, optional trade later).
// • **`tokens = [100,200,300,400], power = 200`** → **`2`**.
//
// Improvements
// • **Counting sort** if costs bounded small — linear time possible; default **`int`** costs use comparison sort.
//
// --- end notes ---

// @lc code=start

func BagOfTokensScore948(tokens []int, power int) int {
	sort.Ints(tokens)
	lo, hi := 0, len(tokens)-1
	score := 0
	best := 0
	for lo <= hi {
		if power >= tokens[lo] {
			power -= tokens[lo]
			lo++
			score++
			if score > best {
				best = score
			}
		} else if score > 0 {
			power += tokens[hi]
			hi--
			score--
		} else {
			break
		}
	}
	return best
}

// @lc code=end
