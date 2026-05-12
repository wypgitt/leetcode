package main

func minimumSwap(s1 string, s2 string) int {
	xy, yx := 0, 0
	for i := 0; i < len(s1); i++ {
		if s1[i] == 'x' && s2[i] == 'y' {
			xy++
		} else if s1[i] == 'y' && s2[i] == 'x' {
			yx++
		}
	}

	if (xy+yx)%2 == 1 {
		return -1
	}
	return xy/2 + yx/2 + 2*(xy%2)
}

/*
Explanation

Only mismatched positions matter. They are either "xy" or "yx". Two mismatches
of the same type can be fixed in one swap. If one xy and one yx remain, they
take two swaps.

If the total mismatch count is odd, one mismatch cannot be paired, so the task
is impossible.

Counting mismatch categories is enough because characters are only x and y;
exact positions are not important after classification.

Edge cases: already equal strings return 0; "xy" with "yx" returns 2; odd
mismatch count returns -1.

Time complexity: O(n).
Space complexity: O(1).
*/
