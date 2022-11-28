use ms2_db;

-- Drop table
DROP TABLE IF EXISTS waitlist;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS login_log;
DROP TABLE IF EXISTS users;

-- Create table
DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    userid int auto_increment PRIMARY KEY,
    email varchar(255) unique NOT NULL ,
    username varchar(255) default 'Badminton Player',
    sex	ENUM('Female', 'Male', 'Others'),
    birthday DATE,
    preference ENUM('Double', 'Single'),
    credits	int default 100,
    profile_pic varchar(255),
    role ENUM('User', 'Admin') default 'User',
    updatetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE login_log
(
    userid int,
    updatetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE
);

CREATE TABLE sessions
(
    sessionid int auto_increment primary key,
    begintime DATETIME not null,
    endtime DATETIME not null,
    capacity int default 8,
    notes varchar(255)
);

CREATE TABLE waitlist
(
    sessionid int,
    userid int,
    updatetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    partnerid int,
    notes varchar(255),
    PRIMARY KEY (sessionid, userid),
    FOREIGN KEY (sessionid) REFERENCES sessions(sessionid) ON DELETE CASCADE,
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE

);


-- Insertion
INSERT INTO users (email, username, sex, birthday, credits ) VALUES ('test5@test.com', 'panda', 'female', '2014-01-01', '90');
INSERT INTO users (email, username, sex, birthday, credits ) VALUES ('test4@test.com', 'zebra', 'female', '2014-01-01', '60');
INSERT INTO users (email, username, sex, birthday, credits ) VALUES ('test3@test.com', 'orange', 'female', '2015-01-01', '0');
INSERT INTO users (email, username, sex, birthday, credits ) VALUES ('test2@test.com', 'apple', 'male', '2017-01-01', '40');
INSERT INTO users (email, username, sex, birthday, credits ) VALUES ('test1@test.com', 'banana', 'male', '2022-01-01', '100');
INSERT INTO users (email, username, sex, birthday, credits ) VALUES ('test@test.com', 'mushroom', 'male', '2021-01-01', '100');
INSERT INTO users (email, username, sex, birthday) VALUES ('test6@test.com', 'panda', 'female', '2010-01-01');

INSERT INTO login_log(userid) VALUES (1);
INSERT INTO login_log(userid) VALUES (3);
INSERT INTO login_log(userid) VALUES (5);
INSERT INTO login_log(userid) VALUES (1);

INSERT INTO sessions (begintime, endtime) VALUES ('2022-11-27 18:30:00', '2022-11-27 19:30:00');
INSERT INTO sessions (begintime, endtime) VALUES ('2022-11-28 18:30:00', '2022-11-28 19:30:00');
INSERT INTO sessions (begintime, endtime) VALUES ('2022-11-29 18:30:00', '2022-11-29 19:30:00');
INSERT INTO sessions (begintime, endtime) VALUES ('2022-11-29 19:30:00', '2022-11-29 20:30:00');
INSERT INTO sessions (begintime, endtime) VALUES ('2022-10-17 19:30:00', '2022-10-17 20:30:00');
INSERT INTO sessions (begintime, endtime, notes) VALUES ('2022-10-30 18:30:00', '2022-10-30 19:30:00', 'Welcome');

INSERT INTO waitlist (sessionid, userid, notes) VALUES (1,1, 'Enjoy');
INSERT INTO waitlist (sessionid, userid, notes) VALUES (1,3, 'Welcome');
INSERT INTO waitlist (sessionid, userid, partnerid) VALUES (1,6,2);
INSERT INTO waitlist (sessionid, userid) VALUES (2,1);
INSERT INTO waitlist (sessionid, userid) VALUES (2,2);
INSERT INTO waitlist (sessionid, userid) VALUES (2,4);
INSERT INTO waitlist (sessionid, userid) VALUES (2,5);
INSERT INTO waitlist (sessionid, userid) VALUES (3,1);
INSERT INTO waitlist (sessionid, userid) VALUES (3,3);
INSERT INTO waitlist (sessionid, userid) VALUES (4,3);
INSERT INTO waitlist (sessionid, userid) VALUES (4,4);
INSERT INTO waitlist (sessionid, userid) VALUES (4,5);
INSERT INTO waitlist (sessionid, userid) VALUES (5,1);
DELETE FROM waitlist WHERE userid=1 AND sessionid=1;

SELECT * FROM users;
SELECT * FROM sessions;
SELECT * FROM waitlist;
SELECT * FROM login_log;

# create an admin zheyan.liu@columbia.edu
UPDATE ms2_db.users
SET role = 'Admin'
WHERE email = 'zheyan.liu@columbia.edu'
SELECT * FROM ms2_db.users;


