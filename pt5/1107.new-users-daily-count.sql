SELECT
    first_login AS login_date,
    COUNT(*) AS user_count
FROM (
    SELECT
        user_id,
        MIN(activity_date) AS first_login
    FROM Traffic
    WHERE activity = 'login'
    GROUP BY user_id
) AS first_logins
WHERE first_login BETWEEN DATE_SUB('2019-06-30', INTERVAL 90 DAY) AND '2019-06-30'
GROUP BY first_login;

