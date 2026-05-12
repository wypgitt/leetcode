#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    vector<int> shortestAlternatingPaths(int n, vector<vector<int>>& redEdges, vector<vector<int>>& blueEdges) {
        vector<vector<pair<int, int>>> graph(n);
        for (auto& edge : redEdges) graph[edge[0]].push_back({edge[1], 0});
        for (auto& edge : blueEdges) graph[edge[0]].push_back({edge[1], 1});

        vector<vector<int>> dist(n, vector<int>(2, -1));
        queue<pair<int, int>> q;
        dist[0][0] = dist[0][1] = 0;
        q.push({0, 0});
        q.push({0, 1});

        while (!q.empty()) {
            auto [node, lastColor] = q.front();
            q.pop();

            for (auto [next, color] : graph[node]) {
                if (color == lastColor || dist[next][color] != -1) continue;
                dist[next][color] = dist[node][lastColor] + 1;
                q.push({next, color});
            }
        }

        vector<int> answer(n);
        for (int i = 0; i < n; ++i) {
            if (dist[i][0] == -1) answer[i] = dist[i][1];
            else if (dist[i][1] == -1) answer[i] = dist[i][0];
            else answer[i] = min(dist[i][0], dist[i][1]);
        }
        return answer;
    }
};

/*
Interview Explanation

Core idea:
The shortest path state must include the color of the last edge used. BFS over
(node, lastColor) states enforces alternation.

C++ data structures:
- vector<vector<pair<int,int>>> adjacency list stores neighbor and edge color.
- dist[node][color] is the shortest distance to node ending with color.
- queue<pair<int,int>> performs BFS.

Algorithm:
1. Add red edges with color 0 and blue edges with color 1.
2. Start at node 0 with both possible previous colors at distance 0.
3. In BFS, traverse only edges whose color differs from lastColor.
4. First time a state is reached is shortest.

Correctness:
BFS processes states in increasing path length. Because the state records the
last color, every transition preserves alternating colors. Thus the first
distance found for each state is optimal, and the answer for a node is the
minimum over its two ending colors.

Complexity:
O(n + r + b) time and space.

Edge cases:
- Node 0 has distance 0.
- Parallel edges and self-loops are safe because states prevent revisits.
- Unreachable nodes remain -1.
*/
