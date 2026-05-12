class Solution {
    public double nthPersonGetsNthSeat(int n) {
        return n == 1 ? 1.0 : 0.5;
    }
}

/*
Explanation

For n == 1, the only passenger gets their own seat. For n > 1, after the first
passenger chooses randomly, the process only depends on which special seat is
chosen first: seat 1 or seat n. Choosing a middle seat simply transfers the
same problem to another displaced passenger.

By symmetry, seat 1 and seat n are equally likely to be the first special seat
chosen, so the answer is 1/2.

Edge cases: n == 1 is the only exception; every n >= 2 returns 0.5.

Time complexity: O(1).
Space complexity: O(1).
*/
