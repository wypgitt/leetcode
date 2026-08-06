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


class Solution {
public:
    string fractionToDecimal(int numerator, int denominator) {
        /*
        Approach: write the integer part, then simulate long division for the
        fractional part. When a remainder repeats, the digits from its first
        position repeat, so insert parentheses there.

        C++ notes: long long safely handles abs(INT_MIN). unordered_map maps each
        remainder to the string index where its digit sequence began.
        Complexity: O(number of produced digits) time and space.
        */
        if (numerator == 0) return "0";
        string sign = ((numerator < 0) ^ (denominator < 0)) ? "-" : "";
        long long num = llabs((long long)numerator);
        long long den = llabs((long long)denominator);
        string ans = sign + to_string(num / den);
        long long rem = num % den;
        if (rem == 0) return ans;
        ans.push_back('.');
        unordered_map<long long, int> seen;
        while (rem != 0) {
            if (seen.count(rem)) {
                ans.insert(seen[rem], "(");
                ans.push_back(')');
                break;
            }
            seen[rem] = ans.size();
            rem *= 10;
            ans += to_string(rem / den);
            rem %= den;
        }
        return ans;
    }
};
