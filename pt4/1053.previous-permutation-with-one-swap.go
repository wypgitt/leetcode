package main

/*
1053. Previous Permutation With One Swap
*/
func prevPermOpt1(arr []int) []int {
	pivot := len(arr) - 2
	for pivot >= 0 && arr[pivot] <= arr[pivot+1] {
		pivot--
	}

	if pivot < 0 {
		return arr
	}

	swapIndex := len(arr) - 1
	for arr[swapIndex] >= arr[pivot] {
		swapIndex--
	}

	for swapIndex > pivot+1 && arr[swapIndex] == arr[swapIndex-1] {
		swapIndex--
	}

	arr[pivot], arr[swapIndex] = arr[swapIndex], arr[pivot]
	return arr
}

/*
Interview Explanation

Core idea:
To get the lexicographically largest permutation smaller than arr with one
swap, make the first decrease as far right as possible. Then make that
decrease as small as possible.

Go data structures:
- The []int is modified in place.
- No extra structure is needed because the suffix after the pivot is
  nondecreasing.

Algorithm:
1. Scan from right to left for the first pivot with arr[pivot] > arr[pivot+1].
2. If no pivot exists, the array is already the smallest permutation.
3. Scan from the right for the largest value smaller than arr[pivot].
4. If that value has duplicates, use the leftmost duplicate.
5. Swap and return.

Correctness:
Any smaller permutation must decrease some index. To stay lexicographically
largest, that index must be as far right as possible, which is the pivot.
Choosing the largest smaller suffix value minimizes the decrease. For
duplicates, swapping the leftmost equal candidate leaves the suffix as large as
possible after the swap.

Complexity:
Time is O(n), and space is O(1).

Edge cases:
- Nondecreasing array returns unchanged.
- Strictly decreasing array swaps near the end.
- Duplicates require leftmost candidate handling.
*/
