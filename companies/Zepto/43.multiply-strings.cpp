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
    string multiply(string num1, string num2) {
        /*
        Approach:
        Simulate grade-school multiplication. Digit i of num1 times digit j of
        num2 contributes to positions i+j and i+j+1 in the result array after
        carry propagation.

        C++ notes:
        vector<int> stores decimal digits before converting back to a string.

        Complexity: O(m*n) time and O(m+n) space.
        */
        if (num1 == "0" || num2 == "0") return "0";
        int m = (int)num1.size(), n = (int)num2.size();
        vector<int> digits(m + n, 0);
        for (int i = m - 1; i >= 0; --i) {
            for (int j = n - 1; j >= 0; --j) {
                int product = (num1[i] - '0') * (num2[j] - '0') + digits[i + j + 1];
                digits[i + j + 1] = product % 10;
                digits[i + j] += product / 10;
            }
        }
        string ans;
        int i = 0;
        while (i < (int)digits.size() && digits[i] == 0) ++i;
        for (; i < (int)digits.size(); ++i) ans.push_back('0' + digits[i]);
        return ans.empty() ? "0" : ans;
    }
};
