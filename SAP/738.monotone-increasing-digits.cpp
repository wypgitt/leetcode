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
    int monotoneIncreasingDigits(int n) {
        string digits = to_string(n);
        int marker = digits.size();
        for (int i = digits.size() - 1; i > 0; --i) {
            if (digits[i - 1] > digits[i]) {
                --digits[i - 1];
                marker = i;
            }
        }
        for (int i = marker; i < (int)digits.size(); ++i) digits[i] = '9';
        return stoi(digits);
    }
};

/*
Interview explanation:
Scan right-to-left for descents. When digits[i-1] > digits[i], decrement digits[i-1] and set everything after it to 9 to maximize the valid number.

C++ data structures: string gives mutable digit access.

Edge cases: cascades like 332 are handled by continuing left; leading zero from 10 becomes 09 and stoi returns 9.

Complexity: O(d) time and O(d) space for d digits.
*/
