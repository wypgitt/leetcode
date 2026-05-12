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
    int maxDistance(vector<vector<int>>& grid) {
        int n = grid.size();
        queue<pair<int, int>> q;
        for (int r = 0; r < n; ++r) {
            for (int c = 0; c < n; ++c) {
                if (grid[r][c] == 1) q.push({r, c});
            }
        }

        if (q.empty() || (int)q.size() == n * n) return -1;

        vector<pair<int, int>> directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int distance = -1;
        while (!q.empty()) {
            int size = q.size();
            ++distance;
            while (size--) {
                auto [r, c] = q.front();
                q.pop();
                for (auto [dr, dc] : directions) {
                    int nr = r + dr, nc = c + dc;
                    if (nr < 0 || nr >= n || nc < 0 || nc >= n || grid[nr][nc] != 0) continue;
                    grid[nr][nc] = 1;
                    q.push({nr, nc});
                }
            }
        }

        return distance;
    }
};

/*
Interview Explanation

Core idea:
Start BFS simultaneously from every land cell. The level at which a water cell
is reached is its distance to nearest land. The last reached water cell has the
maximum such distance.

C++ data structures:
- queue<pair<int,int>> holds BFS frontier cells.
- The grid is reused as visited by changing water 0 to land/visited 1.

Algorithm:
1. Enqueue all land cells.
2. Reject all-water and all-land grids.
3. Run multi-source BFS by levels.
4. Return the final BFS level distance.

Correctness:
Multi-source BFS expands all cells in increasing distance from the nearest
source land. Therefore the first visit to each water cell is its nearest-land
distance, and the last level processed is the maximum distance.

Complexity:
O(n^2) time and O(n^2) queue space.

Edge cases:
- All land or all water returns -1.
- One land source works as normal BFS.
*/
