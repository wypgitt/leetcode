import java.util.*;

class Solution {
    public int[] corpFlightBookings(int[][] bookings, int n) {
        int[] diff = new int[n + 1];

        for (int[] booking : bookings) {
            int first = booking[0];
            int last = booking[1];
            int seats = booking[2];
            diff[first - 1] += seats;
            diff[last] -= seats;
        }

        int[] answer = new int[n];
        int running = 0;
        for (int i = 0; i < n; i++) {
            running += diff[i];
            answer[i] = running;
        }
        return answer;
    }
}

