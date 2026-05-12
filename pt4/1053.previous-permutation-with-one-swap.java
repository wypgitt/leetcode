/*
 * 1053. Previous Permutation With One Swap
 */
class Solution {
    public int[] prevPermOpt1(int[] arr) {
        int pivot = arr.length - 2;
        while (pivot >= 0 && arr[pivot] <= arr[pivot + 1]) {
            pivot--;
        }

        if (pivot < 0) {
            return arr;
        }

        int swapIndex = arr.length - 1;
        while (arr[swapIndex] >= arr[pivot]) {
            swapIndex--;
        }

        while (swapIndex > pivot + 1 && arr[swapIndex] == arr[swapIndex - 1]) {
            swapIndex--;
        }

        int temp = arr[pivot];
        arr[pivot] = arr[swapIndex];
        arr[swapIndex] = temp;
        return arr;
    }
}

/*
Interview Explanation

Core idea:
To get the largest permutation smaller than arr using one swap, make the
decrease as far right as possible. Then, at that position, swap in the largest
smaller value available.

Java data structures:
- The int[] is modified in place.
- No extra structure is needed because the suffix after the pivot is
  nondecreasing.

Algorithm:
1. Scan from the right to find the first descent: arr[pivot] > arr[pivot + 1].
2. If no pivot exists, arr is already the smallest permutation.
3. Scan from the right for the largest value smaller than arr[pivot].
4. If duplicates of that value exist, move to the leftmost duplicate.
5. Swap pivot with that value.

Correctness:
Any smaller permutation must decrease some position. To remain
lexicographically largest, that position must be as far right as possible,
which is the pivot. Choosing the largest smaller suffix value minimizes the
decrease. With duplicates, swapping the leftmost equal candidate keeps the
suffix lexicographically largest after the swap.

Complexity:
The scans are O(n), and space is O(1).

Edge cases:
- Nondecreasing array returns unchanged.
- Strictly decreasing array swaps near the end.
- Duplicates require choosing the leftmost duplicate candidate.
*/
