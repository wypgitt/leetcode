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
    int smallestCommonElement(vector<vector<int>>& mat) {
        unordered_map<int, int> count;
        for (const auto& row : mat) {
            for (int value : row) {
                ++count[value];
            }
        }

        for (int value : mat[0]) {
            if (count[value] == (int)mat.size()) return value;
        }
        return -1;
    }
};

/*
Interview Explanation

Core idea:
Rows are strictly increasing, so each value appears at most once per row. Count
how many rows contain each value, then scan the first row for the smallest
common value.

C++ data structures:
- unordered_map<int,int> counts row appearances for each value.

Algorithm:
1. Count every value across all rows.
2. Since row 0 is sorted, scan it from left to right.
3. The first value whose count equals the number of rows is the answer.

Correctness:
A value is common to all rows exactly when it is counted once in every row,
which gives count == number of rows. The first such value in the sorted first
row is the smallest common element.

Complexity:
O(mn) time and O(number of distinct values) space.

Edge cases:
- No common value returns -1.
- A one-row matrix returns its first element.
*/
