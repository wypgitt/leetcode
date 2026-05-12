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
    int largest1BorderedSquare(vector<vector<int>>& grid) {
        int rows = grid.size(), cols = grid[0].size();
        vector<vector<int>> right(rows, vector<int>(cols, 0));
        vector<vector<int>> down(rows, vector<int>(cols, 0));

        for (int r = rows - 1; r >= 0; --r) {
            for (int c = cols - 1; c >= 0; --c) {
                if (grid[r][c] == 1) {
                    right[r][c] = 1 + (c + 1 < cols ? right[r][c + 1] : 0);
                    down[r][c] = 1 + (r + 1 < rows ? down[r + 1][c] : 0);
                }
            }
        }

        for (int side = min(rows, cols); side >= 1; --side) {
            for (int r = 0; r + side <= rows; ++r) {
                for (int c = 0; c + side <= cols; ++c) {
                    if (right[r][c] >= side &&
                        down[r][c] >= side &&
                        right[r + side - 1][c] >= side &&
                        down[r][c + side - 1] >= side) {
                        return side * side;
                    }
                }
            }
        }

        return 0;
    }
};

/*
Interview Explanation

Core idea:
For a candidate square, only the four borders matter. Precompute how many
consecutive 1s extend rightward and downward from every cell.

C++ data structures:
- right[r][c] = number of consecutive 1s to the right from (r,c).
- down[r][c] = number of consecutive 1s downward from (r,c).

Algorithm:
1. Fill right and down from bottom-right to top-left.
2. Try side lengths from largest to smallest.
3. A square is valid if its top, left, bottom, and right borders each have at
   least side consecutive 1s.
4. Return the first valid area.

Correctness:
The precomputed arrays exactly answer whether a horizontal or vertical border
has enough 1s. Checking all four borders verifies the square definition. Since
side lengths are tried descending, the first valid square has maximum area.

Complexity:
Precomputation is O(mn). Testing all positions and side lengths is
O(mn*min(m,n)). Space is O(mn).

Edge cases:
- No 1s returns 0.
- A single 1 returns area 1.
- Interior zeros do not matter if borders are all 1s.
*/
