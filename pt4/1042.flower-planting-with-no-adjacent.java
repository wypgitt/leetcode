import java.util.ArrayList;
import java.util.List;

/*
 * 1042. Flower Planting With No Adjacent
 */
class Solution {
    public int[] gardenNoAdj(int n, int[][] paths) {
        @SuppressWarnings("unchecked")
        List<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int[] path : paths) {
            int a = path[0] - 1;
            int b = path[1] - 1;
            graph[a].add(b);
            graph[b].add(a);
        }

        int[] answer = new int[n];
        for (int garden = 0; garden < n; garden++) {
            boolean[] used = new boolean[5];
            for (int neighbor : graph[garden]) {
                used[answer[neighbor]] = true;
            }

            for (int flower = 1; flower <= 4; flower++) {
                if (!used[flower]) {
                    answer[garden] = flower;
                    break;
                }
            }
        }

        return answer;
    }
}

/*
Interview Explanation

Core idea:
Each garden has at most three neighbors, while four flower types are available.
When coloring any garden, at most three colors are forbidden, so a valid color
always exists.

Java data structures:
- ArrayList<Integer>[] adjacency list represents the sparse garden graph.
- int[] answer stores the chosen flower for each garden.
- boolean[5] used marks neighbor colors 1 through 4.

Algorithm:
1. Build the undirected graph, converting labels from 1-indexed to 0-indexed.
2. Visit gardens in order.
3. Mark colors already used by colored neighbors.
4. Assign the first unused color from 1 to 4.

Correctness:
When a garden is colored, it avoids every color already used by its neighbors.
Future neighbors will also avoid this garden's color. Since every garden has
degree at most 3 and there are 4 colors, the greedy choice always finds a
valid color. Therefore every path connects gardens with different flowers.

Complexity:
Building and coloring cost O(n + p), where p is paths.length. Space is
O(n + p).

Edge cases:
- No paths: every garden may receive color 1.
- Triangle graph: three colors are enough.
- Complete graph on four gardens: all four colors may be used.
*/
