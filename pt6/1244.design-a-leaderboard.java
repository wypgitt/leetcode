import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Leaderboard {
    private final Map<Integer, Integer> scores;

    public Leaderboard() {
        scores = new HashMap<>();
    }

    public void addScore(int playerId, int score) {
        scores.put(playerId, scores.getOrDefault(playerId, 0) + score);
    }

    public int top(int K) {
        List<Integer> values = new ArrayList<>(scores.values());
        values.sort(Collections.reverseOrder());

        int total = 0;
        for (int i = 0; i < K; i++) {
            total += values.get(i);
        }
        return total;
    }

    public void reset(int playerId) {
        scores.remove(playerId);
    }
}

/*
Explanation

Store playerId -> score in a HashMap. addScore updates that map, reset removes
the player, and top(K) sorts current scores descending and sums the first K.

The constraints allow at most 1000 calls, so this simple HashMap plus sorting
is cleaner than a balanced tree or heap with lazy deletion. For a production
leaderboard with many top queries, a TreeMap or Fenwick tree over bounded
scores would be worth discussing.

Edge cases: a new player starts from score 0; reset is guaranteed to target an
existing player; K is guaranteed valid.

Time complexity: addScore O(1), reset O(1), top O(n log n).
Space complexity: O(n).
*/
