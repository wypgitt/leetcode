package leetcode

// CanIWin464 models the game state as a bitmask of used numbers plus the
// remaining total. The current player wins if any legal pick reaches the target
// immediately or leaves the opponent in a losing memoized state.
//
// Go data structure note: map[int]bool memoizes by used-mask. The remaining sum
// is determined by the path to that mask, so the mask alone is enough as key.
//
// Time: O(m*2^m). Space: O(2^m).
func CanIWin464(maxChoosableInteger int, desiredTotal int) bool {
	if desiredTotal <= 0 {
		return true
	}
	if maxChoosableInteger*(maxChoosableInteger+1)/2 < desiredTotal {
		return false
	}
	memo := map[int]bool{}
	var winning func(mask, remaining int) bool
	winning = func(mask, remaining int) bool {
		if v, ok := memo[mask]; ok {
			return v
		}
		for x := 1; x <= maxChoosableInteger; x++ {
			bit := 1 << (x - 1)
			if mask&bit != 0 {
				continue
			}
			if x >= remaining || !winning(mask|bit, remaining-x) {
				memo[mask] = true
				return true
			}
		}
		memo[mask] = false
		return false
	}
	return winning(0, desiredTotal)
}
