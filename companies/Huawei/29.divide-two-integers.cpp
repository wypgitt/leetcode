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
    int divide(int dividend, int divisor) {
        /*
        Approach:
        Work with positive long long magnitudes and subtract the largest shifted
        divisor chunk possible at each step. This is binary long division using
        bit shifts instead of multiplication, division, or modulo.

        C++ notes:
        long long safely holds abs(INT_MIN). The only overflowing 32-bit result
        is INT_MIN / -1, which must clamp to INT_MAX.

        Complexity: O(log |dividend|) time and O(1) space.
        */
        if (dividend == INT_MIN && divisor == -1) return INT_MAX;
        long long a = llabs((long long)dividend);
        long long b = llabs((long long)divisor);
        long long quotient = 0;
        while (a >= b) {
            long long chunk = b, multiple = 1;
            while ((chunk << 1) <= a) {
                chunk <<= 1;
                multiple <<= 1;
            }
            a -= chunk;
            quotient += multiple;
        }
        bool negative = (dividend < 0) ^ (divisor < 0);
        return (int)(negative ? -quotient : quotient);
    }
};
