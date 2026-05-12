package main

func nthPersonGetsNthSeat(n int) float64 {
	if n == 1 {
		return 1.0
	}
	return 0.5
}

/*
Explanation

For n == 1, the only passenger gets their own seat. For n > 1, after passenger
1 chooses randomly, the process only depends on which special seat is chosen
first: seat 1 or seat n. If seat 1 is chosen first, passenger n gets seat n. If
seat n is chosen first, passenger n loses. Choosing a middle seat just passes
the same situation to another displaced passenger.

By symmetry, seat 1 and seat n are equally likely to be the first special seat
chosen, so the answer is 1/2.

Edge cases: n == 1 is the only exception; every n >= 2 returns 0.5.

Time complexity: O(1).
Space complexity: O(1).
*/
