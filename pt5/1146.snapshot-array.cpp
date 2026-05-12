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

class SnapshotArray {
private:
    int currentSnap = 0;
    vector<vector<pair<int, int>>> history;

public:
    SnapshotArray(int length) : history(length, vector<pair<int, int>>{{0, 0}}) {}

    void set(int index, int val) {
        if (history[index].back().first == currentSnap) {
            history[index].back().second = val;
        } else {
            history[index].push_back({currentSnap, val});
        }
    }

    int snap() {
        return currentSnap++;
    }

    int get(int index, int snap_id) {
        auto& records = history[index];
        auto it = upper_bound(records.begin(), records.end(), make_pair(snap_id, INT_MAX));
        --it;
        return it->second;
    }
};

/*
Interview Explanation

Core idea:
Most indices are not updated on every snapshot. Store only changes per index,
tagged with the snap id when they happened.

C++ data structures:
- vector<vector<pair<int,int>>> history stores sorted (snap_id, value) records
  for each index.
- upper_bound finds the latest record with snap_id <= requested id.

Algorithm:
set: overwrite the last record if it belongs to the current snapshot; otherwise
append a new record.
snap: return current id and increment it.
get: binary search the index history for the rightmost record not after snap_id.

Correctness:
Each index history contains exactly the value changes in chronological order.
The value at a snapshot is the latest change at or before that snapshot, which
upper_bound returns.

Complexity:
set and snap are O(1). get is O(log k), where k is updates to that index.
Space is O(total set calls + length).

Edge cases:
- Unset values return 0 because each index starts with (0,0).
- Multiple sets before a snap are collapsed into one record.
*/
