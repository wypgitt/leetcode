package leetcode

import "math/bits"

// FlipLights672 enumerates the 16 parity masks for the four buttons. A mask is
// reachable if it uses no more presses than allowed and has the same parity as
// presses after adding canceling double-presses. Only the first six bulbs matter
// because the button patterns repeat every lcm(2,3)=6 positions.
//
// Time: O(1). Space: O(1).
func FlipLights672(n int, presses int) int {
	if n > 6 {
		n = 6
	}
	seen := map[string]bool{}
	for mask := 0; mask < 16; mask++ {
		cnt := bits.OnesCount(uint(mask))
		if cnt > presses || (presses-cnt)%2 != 0 {
			continue
		}
		state := make([]byte, n)
		for i := 1; i <= n; i++ {
			on := byte('1')
			if mask&1 != 0 {
				on ^= 1
			}
			if mask&2 != 0 && i%2 == 0 {
				on ^= 1
			}
			if mask&4 != 0 && i%2 == 1 {
				on ^= 1
			}
			if mask&8 != 0 && i%3 == 1 {
				on ^= 1
			}
			state[i-1] = on
		}
		seen[string(state)] = true
	}
	return len(seen)
}
