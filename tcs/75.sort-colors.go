package leetcode

// SortColors75 is Dutch national flag partitioning. [0,low) are 0s, [low,mid)
// are 1s, (high,end] are 2s, and mid scans unknown values.
//
// Time: O(n). Space: O(1).
func SortColors75(nums []int) {
	low, mid, high := 0, 0, len(nums)-1
	for mid <= high {
		if nums[mid] == 0 {
			nums[low], nums[mid] = nums[mid], nums[low]
			low++
			mid++
		} else if nums[mid] == 2 {
			nums[mid], nums[high] = nums[high], nums[mid]
			high--
		} else {
			mid++
		}
	}
}
