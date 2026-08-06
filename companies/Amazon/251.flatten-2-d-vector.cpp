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


class Vector2D {
    vector<vector<int>> vec;
    int row = 0;
    int col = 0;

    void skipEmpty() {
        while (row < (int)vec.size() && col >= (int)vec[row].size()) {
            ++row;
            col = 0;
        }
    }

public:
    Vector2D(vector<vector<int>>& vec) : vec(vec) {
        /*
        Approach: keep row and column indices into the 2D vector. Before next()
        and hasNext(), skip over empty rows so row/col always point at the next
        available integer or past the end.

        C++ notes: vector<vector<int>> stores the copied 2D data; row/col are the
        iterator state.
        Complexity: each element and row is advanced past once, so O(1) amortized
        per operation; O(total input size) storage for the copied vector.
        */
    }

    int next() {
        skipEmpty();
        int val = vec[row][col++];
        return val;
    }

    bool hasNext() {
        skipEmpty();
        return row < (int)vec.size();
    }
};
