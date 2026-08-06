package leetcode

// CircularArrayLoop457 uses Floyd's cycle detection from each unvisited index.
// A valid cycle must keep one direction and have length greater than one. After
// a failed search, the traversed same-direction path is marked 0 so each index
// is processed at most once.
//
// The input slice is intentionally mutated for O(1) extra space.
// Time: O(n). Space: O(1).
func CircularArrayLoop457(nums []int) bool {
	n := len(nums)
	next := func(i int) int {
		j := (i + nums[i]) % n
		if j < 0 {
			j += n
		}
		return j
	}
	for i := 0; i < n; i++ {
		if nums[i] == 0 {
			continue
		}
		direction := nums[i] > 0
		slow, fast := i, i
		for {
			ns := next(slow)
			if nums[ns] == 0 || (nums[ns] > 0) != direction {
				break
			}
			nf := next(fast)
			if nums[nf] == 0 || (nums[nf] > 0) != direction {
				break
			}
			nnf := next(nf)
			if nums[nnf] == 0 || (nums[nnf] > 0) != direction {
				break
			}
			slow, fast = ns, nnf
			if slow == fast {
				if slow == next(slow) {
					break
				}
				return true
			}
		}
		for j := i; nums[j] != 0 && (nums[j] > 0) == direction; {
			nj := next(j)
			nums[j] = 0
			j = nj
		}
	}
	return false
}
