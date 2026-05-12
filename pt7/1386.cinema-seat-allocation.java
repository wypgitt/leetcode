import java.util.HashMap;
import java.util.Map;

/*
 * LeetCode 1386 - Cinema Seat Allocation
 */
class Solution {
    public int maxNumberOfFamilies(int n, int[][] reservedSeats) {
        Map<Integer, Integer> reservedByRow = new HashMap<>();

        for (int[] seatInfo : reservedSeats) {
            int row = seatInfo[0];
            int seat = seatInfo[1];
            if (seat >= 2 && seat <= 9) {
                int bit = seat - 2;
                reservedByRow.put(row, reservedByRow.getOrDefault(row, 0) | (1 << bit));
            }
        }

        int leftBlock = 0b00001111;   // seats 2, 3, 4, 5
        int middleBlock = 0b00111100; // seats 4, 5, 6, 7
        int rightBlock = 0b11110000;  // seats 6, 7, 8, 9

        int families = (n - reservedByRow.size()) * 2;

        for (int mask : reservedByRow.values()) {
            boolean canLeft = (mask & leftBlock) == 0;
            boolean canRight = (mask & rightBlock) == 0;

            if (canLeft && canRight) {
                families += 2;
            } else if (canLeft || canRight || (mask & middleBlock) == 0) {
                families += 1;
            }
        }

        return families;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Only seats 2 through 9 matter. Each row can fit two families in blocks 2-5
 * and 6-9, or one family in block 4-7 if side blocks are blocked. Represent
 * reserved seats in those positions as an 8-bit mask.
 *
 * Java data structures:
 * `HashMap<Integer, Integer>` stores one bitmask per row that has relevant
 * reservations. Rows with no relevant reservations are counted in bulk as two
 * families each.
 *
 * Edge cases:
 * - Reservations in seats 1 or 10 are ignored.
 * - Rows absent from the map contribute 2.
 * - Middle block only matters when both side families cannot be placed.
 *
 * Complexity:
 * Time O(r), where r is reservedSeats length.
 * Space O(min(n, r)).
 */
