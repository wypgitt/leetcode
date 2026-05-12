import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public List<List<Integer>> queensAttacktheKing(int[][] queens, int[] king) {
        Set<Integer> occupied = new HashSet<>();
        for (int[] q : queens) {
            occupied.add(q[0] * 8 + q[1]);
        }

        int[][] dirs = {
            {1, 0}, {-1, 0}, {0, 1}, {0, -1},
            {1, 1}, {1, -1}, {-1, 1}, {-1, -1}
        };
        List<List<Integer>> ans = new ArrayList<>();

        for (int[] d : dirs) {
            int r = king[0] + d[0];
            int c = king[1] + d[1];
            while (r >= 0 && r < 8 && c >= 0 && c < 8) {
                if (occupied.contains(r * 8 + c)) {
                    List<Integer> queen = new ArrayList<>();
                    queen.add(r);
                    queen.add(c);
                    ans.add(queen);
                    break;
                }
                r += d[0];
                c += d[1];
            }
        }

        return ans;
    }
}

/*
Explanation

A queen attacks the king if it is the first queen found in one of the eight
straight directions from the king. Store queen locations in a HashSet and scan
outward from the king in each direction.

The HashSet gives constant-time board lookup. Encoding row and column as
row * 8 + col avoids needing a custom coordinate object.

Edge cases: multiple queens in the same direction only the nearest counts; no
queen in a direction contributes nothing; the board is fixed size.

Time complexity: O(1), at most 8 directions times 7 squares.
Space complexity: O(q).
*/
