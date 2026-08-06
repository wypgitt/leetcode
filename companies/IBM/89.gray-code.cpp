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
    vector<int> grayCode(int n) {
        /*
        Approach:
        The binary-reflected Gray code for i is i ^ (i >> 1). Iterating i from 0
        to 2^n - 1 produces a sequence where adjacent values differ by one bit.

        C++ notes:
        ^ is bitwise XOR and >> is right shift.

        Complexity: O(2^n) time for the output and O(1) extra space.
        */
        vector<int> ans;
        for (int i = 0; i < (1 << n); ++i) ans.push_back(i ^ (i >> 1));
        return ans;
    }
};
