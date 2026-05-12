import java.util.*;

class Solution {
    public int minKnightMoves(int x, int y) {
        x = Math.abs(x);
        y = Math.abs(y);
        if (x == 0 && y == 0) {
            return 0;
        }

        int[][] moves = {
            {1, 2}, {2, 1}, {2, -1}, {1, -2},
            {-1, -2}, {-2, -1}, {-2, 1}, {-1, 2}
        };
        Queue<int[]> queue = new ArrayDeque<>();
        Set<Long> visited = new HashSet<>();
        queue.offer(new int[] {0, 0, 0});
        visited.add(key(0, 0));

        while (!queue.isEmpty()) {
            int[] state = queue.poll();
            for (int[] move : moves) {
                int nr = state[0] + move[0];
                int nc = state[1] + move[1];
                if (nr == x && nc == y) {
                    return state[2] + 1;
                }
                long key = key(nr, nc);
                if (nr >= -2 && nr <= x + 2 && nc >= -2 && nc <= y + 2 && visited.add(key)) {
                    queue.offer(new int[] {nr, nc, state[2] + 1});
                }
            }
        }

        return -1;
    }

    private long key(int row, int col) {
        return (((long) row) << 32) ^ (col & 0xffffffffL);
    }
}

