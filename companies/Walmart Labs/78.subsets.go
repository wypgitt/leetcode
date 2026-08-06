package leetcode

// Subsets78 iteratively doubles the answer: for each number, append that number
// to every subset built so far. Input values are distinct, so no duplicate
// handling is needed.
//
// Time/space: O(2^n*n) including output copies.
func Subsets78(nums []int) [][]int {
	ans := [][]int{{}}
	for _, num := range nums {
		size := len(ans)
		for i := 0; i < size; i++ {
			next := append(append([]int(nil), ans[i]...), num)
			ans = append(ans, next)
		}
	}
	return ans
}
