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
    vector<string> invalidTransactions(vector<string>& transactions) {
        int n = transactions.size();
        vector<Record> records;
        records.reserve(n);
        for (int i = 0; i < n; ++i) records.push_back(parse(transactions[i], i));

        vector<bool> invalid(n, false);
        for (int i = 0; i < n; ++i) {
            if (records[i].amount > 1000) invalid[i] = true;
            for (int j = i + 1; j < n; ++j) {
                if (records[i].name == records[j].name &&
                    records[i].city != records[j].city &&
                    abs(records[i].time - records[j].time) <= 60) {
                    invalid[i] = invalid[j] = true;
                }
            }
        }

        vector<string> answer;
        for (int i = 0; i < n; ++i) {
            if (invalid[i]) answer.push_back(transactions[i]);
        }
        return answer;
    }

private:
    struct Record {
        string name;
        int time;
        int amount;
        string city;
        int index;
    };

    Record parse(const string& transaction, int index) {
        vector<string> parts;
        string token;
        stringstream ss(transaction);
        while (getline(ss, token, ',')) parts.push_back(token);
        return {parts[0], stoi(parts[1]), stoi(parts[2]), parts[3], index};
    }
};

/*
Interview Explanation

Core idea:
A transaction is invalid if amount > 1000 or if another transaction by the
same name occurs within 60 minutes in a different city.

C++ data structures:
- A Record struct stores parsed fields for easy comparison.
- vector<bool> marks invalid original indices.

Algorithm:
1. Parse each transaction string.
2. Mark amount violations.
3. Compare every pair for same name, different city, time difference <= 60.
4. Return original transaction strings whose invalid flag is true.

Correctness:
The two invalidity rules are checked directly. Pairwise comparison considers
every possible conflicting transaction pair, and marking both sides matches the
problem statement. Returning by original index preserves the original strings.

Complexity:
O(n^2) time and O(n) space. n is small enough for pairwise comparison.

Edge cases:
- Same city within 60 minutes is not invalid by the city rule.
- Amount exactly 1000 is valid unless city rule applies.
- Duplicate transaction strings are returned separately by index.
*/
