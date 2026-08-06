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
    int myAtoi(string s) {
        /*
        Approach:
        Parse the fixed grammar: leading spaces, optional sign, then digits.
        Stop at the first non-digit after the numeric prefix. Clamp while
        building the value so fixed-width integer overflow never occurs.

        C++ notes:
        isdigit should receive an unsigned char cast to avoid undefined behavior
        for negative char values.

        Complexity: O(n) time over the parsed prefix and O(1) space.
        */
        int i = 0, n = (int)s.size();
        while (i < n && s[i] == ' ') ++i;
        int sign = 1;
        if (i < n && (s[i] == '+' || s[i] == '-')) {
            sign = (s[i] == '-') ? -1 : 1;
            ++i;
        }
        long long value = 0;
        while (i < n && isdigit(static_cast<unsigned char>(s[i]))) {
            value = value * 10 + (s[i] - '0');
            if (sign == 1 && value >= INT_MAX) return INT_MAX;
            if (sign == -1 && -value <= INT_MIN) return INT_MIN;
            ++i;
        }
        return (int)(sign * value);
    }
};
