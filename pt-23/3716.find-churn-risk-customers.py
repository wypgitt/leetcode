#
# @lc app=leetcode id=3716 lang=python3
#
# [3716] Find Churn Risk Customers
#
# https://leetcode.com/problems/find-churn-risk-customers/description/
#
# database
# Medium (46.95%)
# Likes:    37
# Dislikes: 3
# Total Accepted:    8.9K
# Total Submissions: 19K
# Testcase Example:  "{\"headers\":{\"subscription_events\":[\"event_id\",\"user_id\",\"event_date\",\"event_type\",\"plan_name\",\"monthly_amount\"]},\"rows\":{\"subscription_events\":[[1,501,\"2024-01-01\",\"start\",\"premium\",29.99],[2,501,\"2024-02-15\",\"downgrade\",\"standard\",19.99],[3,501,\"2024-03-20\",\"downgrade\",\"basic\",9.99],[4,502,\"2024-01-05\",\"start\",\"standard\",19.99],[5,502,\"2024-02-10\",\"upgrade\",\"premium\",29.99],[6,502,\"2024-03-15\",\"downgrade\",\"basic\",9.99],[7,503,\"2024-01-10\",\"start\",\"basic\",9.99],[8,503,\"2024-02-20\",\"upgrade\",\"standard\",19.99],[9,503,\"2024-03-25\",\"upgrade\",\"premium\",29.99],[10,504,\"2024-01-15\",\"start\",\"premium\",29.99],[11,504,\"2024-03-01\",\"downgrade\",\"standard\",19.99],[12,504,\"2024-03-30\",\"cancel\",null,0.00],[13,505,\"2024-02-01\",\"start\",\"basic\",9.99],[14,505,\"2024-02-28\",\"upgrade\",\"standard\",19.99],[15,506,\"2024-01-20\",\"start\",\"premium\",29.99],[16,506,\"2024-03-10\",\"downgrade\",\"basic\",9.99]]}}"
#
#
# Table: subscription_events
#
# +------------------+---------+
# | Column Name      | Type    |
# +------------------+---------+
# | event_id         | int     |
# | user_id          | int     |
# | event_date       | date    |
# | event_type       | varchar |
# | plan_name        | varchar |
# | monthly_amount   | decimal |
# +------------------+---------+
# event_id is the unique identifier for this table.
# event_type can be start, upgrade, downgrade, or cancel.
# plan_name can be basic, standard, premium, or NULL (when event_type is
# cancel).
# monthly_amount represents the monthly subscription cost after this
# event.
# For cancel events, monthly_amount is 0.
#
# Write a solution to Find Churn Risk Customers - users who show warning
# signs before churning. A user is considered churn risk customer if they
# meet ALL the following criteria:
#
# Currently have an active subscription (their last event is not cancel).
#
# Have performed at least one downgrade in their subscription history.
#
# Their current plan revenue is less than 50% of their historical maximum
# plan revenue.
#
# Have been a subscriber for at least 60 days.
#
# Return the result table ordered by days_as_subscriber in descending
# order, then by user_id in ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# subscription_events table:
#
# +----------+---------+------------+------------+-----------+----------------+
# | event_id | user_id | event_date | event_type | plan_name |
# monthly_amount |
# +----------+---------+------------+------------+-----------+----------------+
# | 1        | 501     | 2024-01-01 | start      | premium   | 29.99
# |
# | 2        | 501     | 2024-02-15 | downgrade  | standard  | 19.99
# |
# | 3        | 501     | 2024-03-20 | downgrade  | basic     | 9.99
# |
# | 4        | 502     | 2024-01-05 | start      | standard  | 19.99
# |
# | 5        | 502     | 2024-02-10 | upgrade    | premium   | 29.99
# |
# | 6        | 502     | 2024-03-15 | downgrade  | basic     | 9.99
# |
# | 7        | 503     | 2024-01-10 | start      | basic     | 9.99
# |
# | 8        | 503     | 2024-02-20 | upgrade    | standard  | 19.99
# |
# | 9        | 503     | 2024-03-25 | upgrade    | premium   | 29.99
# |
# | 10       | 504     | 2024-01-15 | start      | premium   | 29.99
# |
# | 11       | 504     | 2024-03-01 | downgrade  | standard  | 19.99
# |
# | 12       | 504     | 2024-03-30 | cancel     | NULL      | 0.00
# |
# | 13       | 505     | 2024-02-01 | start      | basic     | 9.99
# |
# | 14       | 505     | 2024-02-28 | upgrade    | standard  | 19.99
# |
# | 15       | 506     | 2024-01-20 | start      | premium   | 29.99
# |
# | 16       | 506     | 2024-03-10 | downgrade  | basic     | 9.99
# |
# +----------+---------+------------+------------+-----------+----------------+
#
# Output:
#
# +----------+--------------+------------------------+-----------------------+--------------------+
# | user_id  | current_plan | current_monthly_amount |
# max_historical_amount | days_as_subscriber |
# +----------+--------------+------------------------+-----------------------+--------------------+
# | 501      | basic        | 9.99                   | 29.99
# | 79                 |
# | 502      | basic        | 9.99                   | 29.99
# | 70                 |
# +----------+--------------+------------------------+-----------------------+--------------------+
#
# Explanation:
#
# User 501:
#
# Currently active: Last event is downgrade to basic (not cancelled)
#
# Has downgrades: Yes, 2 downgrades in history
#
# Current revenue (9.99) vs max (29.99): 9.99/29.99 = 33.3% (less than
# 50%)
#
# Days as subscriber: Jan 1 to Mar 20 = 79 days (at least 60)
#
# Result: Churn Risk Customer
#
# User 502:
#
# Currently active: Last event is downgrade to basic (not cancelled)
#
# Has downgrades: Yes, 1 downgrade in history
#
# Current revenue (9.99) vs max (29.99): 9.99/29.99 = 33.3% (less than
# 50%)
#
# Days as subscriber: Jan 5 to Mar 15 = 70 days (at least 60)
#
# Result: Churn Risk Customer
#
# User 503:
#
# Currently active: Last event is upgrade to premium (not cancelled)
#
# Has downgrades: No downgrades in history
#
# Result: Not at-risk (no downgrade history)
#
# User 504:
#
# Currently active: Last event is cancel
#
# Result: Not at-risk (subscription cancelled)
#
# User 505:
#
# Currently active: Last event is 'upgrade' to standard (not cancelled)
#
# Has downgrades: No downgrades in history
#
# Result: Not at-risk (no downgrade history)
#
# User 506:
#
# Currently active: Last event is downgrade to basic (not cancelled)
#
# Has downgrades: Yes, 1 downgrade in history
#
# Current revenue (9.99) vs max (29.99): 9.99/29.99 = 33.3% (less than
# 50%)
#
# Days as subscriber: Jan 20 to Mar 10 = 50 days (less than 60)
#
# Result: Not at-risk (insufficient subscription duration)
#
# Result table is ordered by days_as_subscriber DESC, then user_id ASC.
#
# Note: days_as_subscriber is calculated from the first event date to the
# last event date for each user.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Churn-risk users are still active, have downgraded, earn <50% of their
        historical max plan amount, and have subscribed >= 60 days.

        Algorithm:
        - Per user: last event (plan/amount/type), max monthly_amount, downgrade
          count, DATEDIFF(last, first) as days_as_subscriber.
        - Filter last_event != cancel, downgrades >= 1, current < 0.5 * max, days >= 60.
        - ORDER BY days_as_subscriber DESC, user_id ASC.

        Complexity: O(N log N) with window/sort over events.
        """
        self.sql = """
WITH ranked AS (
    SELECT
        user_id,
        event_date,
        event_type,
        plan_name,
        monthly_amount,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY event_date DESC, event_id DESC
        ) AS rn_desc
    FROM subscription_events
),
agg AS (
    SELECT
        r.user_id,
        MAX(CASE WHEN r.rn_desc = 1 THEN r.plan_name END) AS current_plan,
        MAX(CASE WHEN r.rn_desc = 1 THEN r.monthly_amount END) AS current_monthly_amount,
        MAX(CASE WHEN r.rn_desc = 1 THEN r.event_type END) AS last_event_type,
        MAX(r.monthly_amount) AS max_historical_amount,
        SUM(CASE WHEN r.event_type = 'downgrade' THEN 1 ELSE 0 END) AS downgrade_cnt,
        DATEDIFF(MAX(r.event_date), MIN(r.event_date)) AS days_as_subscriber
    FROM ranked r
    GROUP BY r.user_id
)
SELECT
    user_id,
    current_plan,
    current_monthly_amount,
    max_historical_amount,
    days_as_subscriber
FROM agg
WHERE last_event_type <> 'cancel'
  AND downgrade_cnt >= 1
  AND current_monthly_amount < 0.5 * max_historical_amount
  AND days_as_subscriber >= 60
ORDER BY days_as_subscriber DESC, user_id ASC;
"""
        return self.sql
# @lc code=end
