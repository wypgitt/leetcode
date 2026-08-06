package leetcode

// SingleNumber260 xors all values to get a^b. The lowest set bit separates the
// two unique numbers into different groups; xor within one group recovers one,
// and xor_all^a recovers the other.
//
// Time: O(n). Space: O(1).
func SingleNumber260(nums []int) []int {
	xorAll := 0
	for _, x := range nums {
		xorAll ^= x
	}
	mask := xorAll & -xorAll
	a := 0
	for _, x := range nums {
		if x&mask != 0 {
			a ^= x
		}
	}
	return []int{a, xorAll ^ a}
}
