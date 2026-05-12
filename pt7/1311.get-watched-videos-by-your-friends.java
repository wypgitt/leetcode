import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Queue;

/*
 * LeetCode 1311 - Get Watched Videos by Your Friends
 */
class Solution {
    public List<String> watchedVideosByFriends(
            List<List<String>> watchedVideos,
            int[][] friends,
            int id,
            int level) {

        boolean[] visited = new boolean[friends.length];
        Queue<Integer> queue = new ArrayDeque<>();
        queue.offer(id);
        visited[id] = true;

        for (int distance = 0; distance < level; distance++) {
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                int person = queue.poll();
                for (int friend : friends[person]) {
                    if (!visited[friend]) {
                        visited[friend] = true;
                        queue.offer(friend);
                    }
                }
            }
        }

        Map<String, Integer> frequency = new HashMap<>();
        while (!queue.isEmpty()) {
            int person = queue.poll();
            for (String video : watchedVideos.get(person)) {
                frequency.put(video, frequency.getOrDefault(video, 0) + 1);
            }
        }

        List<String> answer = new ArrayList<>(frequency.keySet());
        Collections.sort(answer, (a, b) -> {
            int countCompare = Integer.compare(frequency.get(a), frequency.get(b));
            if (countCompare != 0) {
                return countCompare;
            }
            return a.compareTo(b);
        });

        return answer;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Friend relationships form an unweighted graph. Friends at exactly `level`
 * are nodes whose shortest distance from `id` is exactly `level`, so BFS is the
 * natural traversal. After reaching that layer, count videos and sort by
 * frequency then lexicographic order.
 *
 * Java data structures:
 * - `Queue<Integer>` with `ArrayDeque` for level-order BFS.
 * - `boolean[] visited` to avoid cycles and duplicate people.
 * - `HashMap<String, Integer>` for video counts.
 * - `ArrayList<String>` for sorting the final video names.
 *
 * Edge cases:
 * - level 0 counts the starting user's own videos.
 * - Graph cycles are safe because each person is visited once.
 * - Equal video frequencies use alphabetical order.
 *
 * Complexity:
 * Time O(n + e + v log v), where v is distinct counted videos.
 * Space O(n + v).
 */
