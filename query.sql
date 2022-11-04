-- Get available sessions info for user 1
SELECT t1.*, (CASE WHEN t2.sessionid IS NULL THEN FALSE ELSE TRUE END) is_registered
FROM
(
SELECT s.sessionid, begintime, endtime, s.notes, s.capacity, count(1) enrolled
FROM ms2_db.sessions s
LEFT JOIN ms2_db.waitlist w
ON s.sessionid = w.sessionid
GROUP BY s.sessionid, begintime, endtime, s.notes, s.capacity) t1
LEFT JOIN
(
SELECT distinct s.sessionid
FROM ms2_db.sessions s
LEFT JOIN ms2_db.waitlist w
ON s.sessionid = w.sessionid
WHERE w.userid = 1) t2
ON t1.sessionid = t2.sessionid;


SELECT s.sessionid, begintime, endtime, s.notes, s.capacity, count(1) enrolled
FROM (SELECT * FROM ms2_db.sessions
      WHERE endtime > '2022-10-24 19:30:00'
      AND sessionid in (SELECT sessionid FROM ms2_db.waitlist WHERE userid = 1) )s
LEFT JOIN ms2_db.waitlist w
ON s.sessionid = w.sessionid
GROUP BY s.sessionid, begintime, endtime, s.notes, s.capacity;

SELECT * FROM ms2_db.users WHERE userid = 1;

-- if already in wait list as user or partner
SELECT * FROM ms2_db.waitlist
WHERE (userid in (1, 2) or partnerid = 2)
AND sessionid = 1;

-- update partnerid in waitlist
UPDATE ms2_db.waitlist
SET partnerid = NULL
WHERE sessionid = 1 AND partnerid = 2;
SELECT * FROM ms2_db.waitlist;
