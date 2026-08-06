#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    void rotate(vector<vector<int>>& matrix) {
        /*
        Approach:
        A clockwise 90-degree rotation is transpose plus reversing each row.
        Transpose swaps across the main diagonal, then row reversal places the
        columns in the rotated order.

        Complexity: O(n^2) time and O(1) extra space.
        */
        int n = (int)matrix.size();
        for (int r = 0; r < n; ++r) {
            for (int c = r + 1; c < n; ++c) swap(matrix[r][c], matrix[c][r]);
        }
        for (auto& row : matrix) reverse(row.begin(), row.end());
    }
};
