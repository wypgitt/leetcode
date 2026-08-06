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
    string convert(string s, int numRows) {
        /*
        Approach:
        Simulate writing characters row by row. The row index moves downward
        until the last row, then upward until the first row, repeating this
        direction change for the whole string.

        C++ notes:
        vector<string> stores the mutable rows, and appending chars is amortized
        O(1).

        Complexity: O(n) time and O(n) space.
        */
        if (numRows == 1 || numRows >= (int)s.size()) return s;
        vector<string> rows(numRows);
        int row = 0, dir = 1;
        for (char ch : s) {
            rows[row].push_back(ch);
            if (row == 0) dir = 1;
            else if (row == numRows - 1) dir = -1;
            row += dir;
        }
        string ans;
        for (const string& part : rows) ans += part;
        return ans;
    }
};
