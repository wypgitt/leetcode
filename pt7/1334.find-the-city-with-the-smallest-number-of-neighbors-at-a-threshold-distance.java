import java.util.Arrays;

/*
 * LeetCode 1334 - Find the City With the Smallest Number of Neighbors at a Threshold Distance
 */
class Solution {
    public int findTheCity(int n, int[][] edges, int distanceThreshold) {
        final int inf = 1_000_000_000;
        int[][] dist = new int[n][n];

        for (int i = 0; i < n; i++) {
            Arrays.fill(dist[i], inf);
            dist[i][i] = 0;
        }

        for (int[] edge : edges) {
            int a = edge[0];
            int b = edge[1];
            int weight = edge[2];
            dist[a][b] = Math.min(dist[a][b], weight);
            dist[b][a] = Math.min(dist[b][a], weight);
        }

        for (int mid = 0; mid < n; mid++) {
            for (int start = 0; start < n; start++) {
                for (int end = 0; end < n; end++) {
                    dist[start][end] = Math.min(
                            dist[start][end],
                            dist[start][mid] + dist[mid][end]);
                }
            }
        }

        int bestCity = -1;
        int bestCount = n + 1;

        for (int city = 0; city < n; city++) {
            int reachable = 0;
            for (int other = 0; other < n; other++) {
                if (other != city && dist[city][other] <= distanceThreshold) {
                    reachable++;
                }
            }

            if (reachable <= bestCount) {
                bestCount = reachable;
                bestCity = city;
            }
        }

        return bestCity;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * We need all-pairs shortest paths. With n <= 100, Floyd-Warshall is simple
 * and reliable: for every possible intermediate city, try to improve every
 * start-to-end distance.
 *
 * Java data structures:
 * `int[][] dist` stores shortest known distances. `Arrays.fill` initializes
 * each row to a large sentinel value.
 *
 * Tie-breaking:
 * The problem wants the greatest city id when counts tie. We scan from low to
 * high and update on `<=`, so later city ids replace earlier ids on ties.
 *
 * Edge cases:
 * - Disconnected pairs remain at infinity and are not counted.
 * - Multiple edges between two cities keep the smallest weight.
 * - Threshold 0 generally counts no other city.
 *
 * Complexity:
 * Time O(n^3).
 * Space O(n^2).
 */
