#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    int numIslands(vector<vector<char>>& grid) {
        /*
        Approach: scan the grid. When a '1' is found, count a new island and use
        iterative DFS to flood-fill all connected land to '0' so it is not counted
        again.

        C++ notes: vector<pair<int,int>> is used as an explicit stack.
        Complexity: O(m*n) time, O(m*n) worst-case stack space.
        */
        if (grid.empty() || grid[0].empty()) return 0;
        int rows = grid.size(), cols = grid[0].size(), islands = 0;
        int dirs[5] = {1, 0, -1, 0, 1};
        for (int r = 0; r < rows; ++r) {
            for (int c = 0; c < cols; ++c) {
                if (grid[r][c] != '1') continue;
                ++islands;
                grid[r][c] = '0';
                vector<pair<int,int>> st = {{r, c}};
                while (!st.empty()) {
                    auto [x, y] = st.back(); st.pop_back();
                    for (int d = 0; d < 4; ++d) {
                        int nx = x + dirs[d], ny = y + dirs[d + 1];
                        if (nx >= 0 && nx < rows && ny >= 0 && ny < cols && grid[nx][ny] == '1') {
                            grid[nx][ny] = '0';
                            st.push_back({nx, ny});
                        }
                    }
                }
            }
        }
        return islands;
    }
};
