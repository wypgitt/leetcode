#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    bool canTransform(string start, string result) {
        string a, b;
        for (char c : start) if (c != 'X') a += c;
        for (char c : result) if (c != 'X') b += c;
        if (a != b) return false;
        int i = 0, j = 0, n = start.size();
        while (i < n && j < n) {
            while (i < n && start[i] == 'X') ++i;
            while (j < n && result[j] == 'X') ++j;
            if (i == n || j == n) break;
            if (start[i] == 'L' && i < j) return false;
            if (start[i] == 'R' && i > j) return false;
            ++i; ++j;
        }
        return true;
    }
};

/*
Interview explanation:
Removing X, the L/R order cannot change. L can only move left and R can only move right, so compare original and final indices of each non-X character.

C++ data structures: strings a and b check non-X order; two pointers compare positions.

Edge cases: equality of arrival time is irrelevant here; only direction constraints matter.

Complexity: O(n) time and O(n) space for the filtered strings.
*/
