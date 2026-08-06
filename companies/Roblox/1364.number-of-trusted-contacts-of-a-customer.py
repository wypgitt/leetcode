#
# @lc app=leetcode id=1364 lang=python3
#
# [1364] Number of Trusted Contacts of a Customer
#
# https://leetcode.com/problems/number-of-trusted-contacts-of-a-customer/description/
#
# database
# Medium (74.68%)
# Likes:    96
# Dislikes: 403
# Total Accepted:    25.4K
# Total Submissions: 34.1K
# Testcase Example:  "{\"headers\":{\"Customers\":[\"customer_id\",\"customer_name\",\"email\"],\"Contacts\":[\"user_id\",\"contact_name\",\"contact_email\"],\"Invoices\":[\"invoice_id\",\"price\",\"user_id\"]},\"rows\":{\"Customers\":[[1,\"Alice\",\"alice@leetcode.com\"],[2,\"Bob\",\"bob@leetcode.com\"],[13,\"John\",\"john@leetcode.com\"],[6,\"Alex\",\"alex@leetcode.com\"]],\"Contacts\":[[1,\"Bob\",\"bob@leetcode.com\"],[1,\"John\",\"john@leetcode.com\"],[1,\"Jal\",\"jal@leetcode.com\"],[2,\"Omar\",\"omar@leetcode.com\"],[2,\"Meir\",\"meir@leetcode.com\"],[6,\"Alice\",\"alice@leetcode.com\"]],\"Invoices\":[[77,100,1],[88,200,1],[99,300,2],[66,400,2],[55,500,13],[44,60,6]]}}"
#
#
# Table: Customers
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | customer_id   | int     |
# | customer_name | varchar |
# | email         | varchar |
# +---------------+---------+
# customer_id is the column of unique values for this table.
# Each row of this table contains the name and the email of a customer of
# an online shop.
#
# Table: Contacts
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | user_id       | id      |
# | contact_name  | varchar |
# | contact_email | varchar |
# +---------------+---------+
# (user_id, contact_email) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table contains the name and email of one contact of
# customer with user_id.
# This table contains information about people each customer trust. The
# contact may or may not exist in the Customers table.
#
# Table: Invoices
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | invoice_id   | int     |
# | price        | int     |
# | user_id      | int     |
# +--------------+---------+
# invoice_id is the column of unique values for this table.
# Each row of this table indicates that user_id has an invoice with
# invoice_id and a price.
#
# Write a solution to find the following for each invoice_id:
#
# customer_name: The name of the customer the invoice is related to.
#
# price: The price of the invoice.
#
# contacts_cnt: The number of contacts related to the customer.
#
# trusted_contacts_cnt: The number of contacts related to the customer and
# at the same time they are customers to the shop. (i.e their email exists
# in the Customers table.)
#
# Return the result table ordered by invoice_id.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Customers table:
# +-------------+---------------+--------------------+
# | customer_id | customer_name | email              |
# +-------------+---------------+--------------------+
# | 1           | Alice         | alice@leetcode.com |
# | 2           | Bob           | bob@leetcode.com   |
# | 13          | John          | john@leetcode.com  |
# | 6           | Alex          | alex@leetcode.com  |
# +-------------+---------------+--------------------+
# Contacts table:
# +-------------+--------------+--------------------+
# | user_id     | contact_name | contact_email      |
# +-------------+--------------+--------------------+
# | 1           | Bob          | bob@leetcode.com   |
# | 1           | John         | john@leetcode.com  |
# | 1           | Jal          | jal@leetcode.com   |
# | 2           | Omar         | omar@leetcode.com  |
# | 2           | Meir         | meir@leetcode.com  |
# | 6           | Alice        | alice@leetcode.com |
# +-------------+--------------+--------------------+
# Invoices table:
# +------------+-------+---------+
# | invoice_id | price | user_id |
# +------------+-------+---------+
# | 77         | 100   | 1       |
# | 88         | 200   | 1       |
# | 99         | 300   | 2       |
# | 66         | 400   | 2       |
# | 55         | 500   | 13      |
# | 44         | 60    | 6       |
# +------------+-------+---------+
# Output:
# +------------+---------------+-------+--------------+----------------------+
# | invoice_id | customer_name | price | contacts_cnt |
# trusted_contacts_cnt |
# +------------+---------------+-------+--------------+----------------------+
# | 44         | Alex          | 60    | 1            | 1
# |
# | 55         | John          | 500   | 0            | 0
# |
# | 66         | Bob           | 400   | 2            | 0
# |
# | 77         | Alice         | 100   | 3            | 2
# |
# | 88         | Alice         | 200   | 3            | 2
# |
# | 99         | Bob           | 300   | 2            | 0
# |
# +------------+---------------+-------+--------------+----------------------+
# Explanation:
# Alice has three contacts, two of them are trusted contacts (Bob and
# John).
# Bob has two contacts, none of them is a trusted contact.
# Alex has one contact and it is a trusted contact (Alice).
# John doesn't have any contacts.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. For each invoice: report customer name, contact count, and how
        many of those contacts are also customers (trusted).

        Algorithm:
        - Join Invoices→Customers for name
        - LEFT JOIN Contacts for contacts_cnt
        - Trusted = contacts whose user_name appears in Customers.email
        - GROUP BY invoice_id

        Complexity: O(I + C + Cust) with hash joins.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        i.invoice_id,
        c.customer_name,
        i.price,
        COUNT(ct.user_id) AS contacts_cnt,
        COUNT(c2.email) AS trusted_contacts_cnt
    FROM Invoices i
    JOIN Customers c ON i.user_id = c.customer_id
    LEFT JOIN Contacts ct ON c.customer_id = ct.user_id
    LEFT JOIN Customers c2 ON ct.contact_email = c2.email
    GROUP BY i.invoice_id, c.customer_name, i.price
    ORDER BY i.invoice_id;
    """
# @lc code=end
