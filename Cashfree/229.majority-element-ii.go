package leetcode

// MajorityElement229 is Boyer-Moore generalized for elements appearing more than
// n/3 times. There can be at most two candidates, so a second pass verifies the
// actual counts.
//
// Time: O(n). Space: O(1).
func MajorityElement229(nums []int) []int {
	cand1, cand2, count1, count2 := 0, 1, 0, 0
	for _, x := range nums {
		if count1 > 0 && x == cand1 {
			count1++
		} else if count2 > 0 && x == cand2 {
			count2++
		} else if count1 == 0 {
			cand1, count1 = x, 1
		} else if count2 == 0 {
			cand2, count2 = x, 1
		} else {
			count1--
			count2--
		}
	}
	c1, c2 := 0, 0
	for _, x := range nums {
		if count1 > 0 && x == cand1 {
			c1++
		}
		if count2 > 0 && x == cand2 {
			c2++
		}
	}
	ans := []int{}
	if count1 > 0 && c1 > len(nums)/3 {
		ans = append(ans, cand1)
	}
	if count2 > 0 && cand2 != cand1 && c2 > len(nums)/3 {
		ans = append(ans, cand2)
	}
	return ans
}
