# %%
import pymysql
import os
from datetime import datetime
from utils import DTEncoder
import requests
import random


class CBSresource:

    def __int__(self):
        self.current_time = datetime.now()

    @staticmethod
    def _get_connection():

        usr = os.environ.get("DBUSER")
        pw = os.environ.get("DBPW")
        h = os.environ.get("DBHOST")

        conn = pymysql.connect(
            user=usr,
            password=pw,
            host=h,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn

    # Methods from MS1
    @staticmethod
    def _get_partner_id(userid):

        # set by environment variables
        baseURL = os.environ.get("MS1_URL")
        partnerid = None
        res = requests.get(baseURL + f'api/user/{userid}/partner').json()
        print(res)
        if res['success']:
            print(res)
            data = res['data'][0]
            partnerid = list(data.values())[0]
        return partnerid

    @staticmethod
    def process_google_login(user_info):

        conn = CBSresource._get_connection()
        cur = conn.cursor()
        # if user not exist, insert into user table
        sql = "SELECT * FROM ms2_db.users where email=%s"
        print(user_info)
        print(user_info['email'])
        cur.execute(sql, args=user_info['email'])
        res = cur.fetchone()
        if res:
            result = {'success': True, 'message': f'Hi {res["username"]}, you have logged in', 'data': res}
        if not res:
            print('insert new user')
            sql_i = "INSERT INTO ms2_db.users (email, username, profile_pic) VALUES (%s, %s, %s);"
            cur.execute(sql_i, args=(user_info['email'], user_info['name'], user_info['picture']))
            sql = "SELECT * FROM ms2_db.users where email=%s"
            cur.execute(sql, args=user_info['email'])
            res = cur.fetchone()
            result = {'success': True, 'message': f'Hi {res["username"]}, you have registered and logged in', 'data': res}
        # insert into login_log table
        sql_i = "INSERT INTO ms2_db.login_log (userid) VALUES (%s)"
        cur.execute(sql_i, args=(res['userid']))
        return result
        
    @staticmethod
    def get_most_recent_login():

        conn = CBSresource._get_connection()
        cur = conn.cursor()
        # if user not exist, insert into user table
        # not show all res
        sql = """
            SELECT t2.userid, t2.email, t2.username, t2.sex, t2.preference, t2.credits, t2.profile_pic, t2.role FROM
            (
            SELECT * FROM ms2_db.users
            WHERE updatetime = (SELECT max(updatetime) FROM ms2_db.users)) t1
            LEFT JOIN ms2_db.users t2
            ON t1.userid = t2.userid;
        """
        cur.execute(sql)
        res = cur.fetchone()
        return res

    @staticmethod
    def get_user_by_email(email):

        conn = CBSresource._get_connection()
        cur = conn.cursor()
        # if user not exist, insert into user table
        # not show all res
        sql = """
            SELECT t2.userid, t2.email, t2.username, t2.sex, t2.preference, t2.credits, t2.profile_pic, t2.role FROM
            (
            SELECT * FROM ms2_db.users
            WHERE email = %s);
        """
        cur.execute(sql, email)
        res = cur.fetchone()
        if res:
            result = {'success': True, 'message': 'Found user', 'data': res}
        else: 
            result = {'success': False, 'message': 'User not found'}
        return result
        
    @staticmethod
    def verify_login(email, password):

        sql = "SELECT userid FROM ms2_db.users where email=%s and password=%s"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=(email, password))
        result = cur.fetchone()
        userId = result['userid'] if result else None

        return userId

    @staticmethod
    def register_user(email, username, password):

        sql = "INSERT INTO ms2_db.users (email, username, password) VALUES (%s, %s, %s);"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            res = cur.execute(sql, args=(email, username, password))
            # if register success
            result = {'success': True, 'message': 'Register successfully, continue to log in'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': 'This email is already registered, try another one'}
        return result

    @staticmethod
    def if_admin(userid):

        sql = "SELECT * FROM ms2_db.users WHERE userid = %s and role = 'Admin'"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            res = cur.execute(sql, args=(userid))
            # if register success
            result = True if res else False
            
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': 'This email is already registered, try another one'}
        return result

    @staticmethod
    def get_available_session(userid):

        sql = """SELECT t1.*, (CASE WHEN t2.sessionid IS NULL THEN 0 ELSE 1 END) is_registered
                 FROM
                 (
                 SELECT s.sessionid, begintime, endtime, s.notes, s.capacity, count(1) enrolled
                 FROM ms2_db.sessions s
                 LEFT JOIN ms2_db.waitlist w
                 ON s.sessionid = w.sessionid
                 WHERE s.endtime > %s
                 GROUP BY s.sessionid, begintime, endtime, s.notes, s.capacity) t1
                 LEFT JOIN
                 (
                 SELECT distinct s.sessionid
                 FROM ms2_db.sessions s
                 LEFT JOIN ms2_db.waitlist w
                 ON s.sessionid = w.sessionid
                 WHERE w.userid = %s OR w.partnerid = %s) t2
                 ON t1.sessionid = t2.sessionid"""
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=(datetime.now(), userid, userid))
            # if register success
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    @staticmethod
    def get_session_by_key(sessionid):

        sql = "SELECT * FROM ms2_db.sessions WHERE sessionid = %s"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=(sessionid))
            # if register success
            res = cur.fetchone()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    @staticmethod
    def enroll_session(sessionid, userid, with_partner):
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        # if already approved
        sql = """SELECT * FROM ms2_db.sessions_enrolled
                 WHERE sessionid = %s AND userid = %s;
              """
        cur.execute(sql, args=(sessionid, userid))
        res = cur.fetchone()
        if res:
            result = {'success': False, 'message': 'Failed. You have already been approved to this session'}
            return result
        
        # not with partner
        if with_partner == 0:
            # check if already exist as user or partner
            sql = """
                SELECT * FROM ms2_db.waitlist
                WHERE (userid = %s or partnerid = %s)
                AND sessionid = %s;
            """
            cur.execute(sql, args=(userid, userid, sessionid))
            res = cur.fetchone()

            # if already exist
            if res:
                result = {'success': False, 'message': 'Failed. You have already joined this waitlist'}
            # otherwise insert into waitlist
            else:
                sql = "INSERT INTO ms2_db.waitlist (sessionid, userid) VALUES (%s, %s)"
                try:
                    cur.execute(sql, args=(sessionid, userid))
                    # if register success
                    result = {'success': True, 'message': 'You have joined the waitlist'}
                except pymysql.Error as e:
                    print(e)
                    res = 'ERROR'
                    result = {'success': False, 'message': str(e)}

        # with partner
        else:
            # if not with partner
            partnerid = CBSresource._get_partner_id(userid)
            if not partnerid:
                result = {'success': False, 'message': 'You do not have a partner'}
                return result
            # check if you or partner is already in
            sql = """
                SELECT * FROM ms2_db.waitlist
                WHERE (userid in (%s, %s) or partnerid in (%s, %s))
                AND sessionid = %s;
            """
            cur.execute(sql, args=(userid, partnerid, userid, partnerid, sessionid))
            res = cur.fetchone()
            if res:
                result = {'success': False, 'message': 'Failed. Your partner or you have already joined this waitlist'}
                return result
                # otherwise begin the joinning process
            sql = "INSERT INTO ms2_db.waitlist (sessionid, userid, partnerid) VALUES (%s, %s, %s)"
            try:
                cur.execute(sql, args=(sessionid, userid, partnerid))
                # if register success
                result = {'success': True, 'message': 'You have both joined the waitlist. Please inform your partner'}
            except pymysql.Error as e:
                print(e)
                res = 'ERROR'
                result = {'success': False, 'message': str(e)}

        return result

    @staticmethod
    def get_session_by_user(userid):
        sql = """
        SELECT s.sessionid, begintime, endtime, s.notes, s.capacity, count(1) enrolled
        FROM (SELECT * FROM ms2_db.sessions
              WHERE endtime > %s
              AND sessionid in (SELECT sessionid FROM ms2_db.waitlist WHERE userid = %s or partnerid = %s) )s
        LEFT JOIN ms2_db.waitlist w
        ON s.sessionid = w.sessionid
        GROUP BY s.sessionid, begintime, endtime, s.notes, s.capacity;
        """
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=(datetime.now(), userid, userid))
            res = cur.fetchall()
            # if fetched successful
            if res:
                result = {'success': True, 'message': 'Here is your sessions in the waitlist', 'data': res}
            else:
                result = {'success': True, 'message': 'You have no sessions in the waitlist', 'data': res}

        except pymysql.Error as e:
            print(e)
            res = 'ERROR'
            result = {'success': False, 'message': str(e)}
        return result

    @staticmethod
    def get_approved_session_by_user(userid):
        sql = """
        SELECT t1.sessionid, t1.begintime, t1.endtime, t1.capacity, t3.approved_cnt, t1.notes 
        FROM ms2_db.sessions t1
        INNER JOIN ms2_db.sessions_enrolled t2
        ON t1.sessionid = t2.sessionid
        INNER JOIN (
            SELECT sessionid, count(*) approved_cnt
            FROM ms2_db.sessions_enrolled
            GROUP BY sessionid
        ) t3
        ON t1.sessionid = t3.sessionid
        WHERE t2.userid = %s
        AND t1.endtime > %s;
        """
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=(userid, datetime.now()))
            res = cur.fetchall()
            # if fetched successful
            if res:
                result = {'success': True, 'message': 'Here is your approved sessions', 'data': res}
            else:
                result = {'success': True, 'message': 'You have no approved sessions', 'data': res}

        except pymysql.Error as e:
            print(e)
            res = 'ERROR'
            result = {'success': False, 'message': str(e)}
        return result

    @staticmethod
    def quit_waitlist(sessionid, userid):
        sql_p = "SELECT * FROM ms2_db.waitlist WHERE userid = %s AND sessionid = %s;"
        sql_q = "SELECT * FROM ms2_db.waitlist WHERE partnerid = %s AND sessionid = %s;"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        cur.execute(sql_p, args=(userid, sessionid))
        res_p = cur.fetchone()
        cur.execute(sql_q, args=(userid, sessionid))
        res_q = cur.fetchone()
        try:
            if res_p:
                sql = "DELETE FROM ms2_db.waitlist WHERE userid = %s AND sessionid = %s;"
                cur.execute(sql, args=(userid, sessionid))
                # if register success
                result = {'success': True, 'message': 'You have quitted the waitlist'}
                return result
            if res_q:
                sql = """
                    UPDATE ms2_db.waitlist
                    SET partnerid = NULL
                    WHERE sessionid = %s AND partnerid = %s;
                """
                cur.execute(sql, args=(sessionid, userid))
                # if register success
                result = {'success': True, 'message': 'You have quitted the waitlist as a partner'}
                return result

            result = {'success': False, 'message': 'You are not in the waitlist'}

        except pymysql.Error as e:
            print(e)
            res = 'ERROR'
            result = {'success': False, 'message': str(e)}
        return result
    
    @staticmethod
    def waitlist_approve(sessionid):
        sql = """
            SELECT userid FROM ms2_db.waitlist
            WHERE sessionid = %s
            AND userid not in (SELECT userid FROM ms2_db.sessions_enrolled WHERE sessionid = %s);
        """
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        cur.execute(sql, args=(sessionid, sessionid))
        res = cur.fetchall()
        result = {'success': False, 'message': f"No record for session {sessionid}"}
        print(res)
        if res:
            candidate_users = [a['userid'] for a in res]
            if len(candidate_users) <= 6:
                approved_users = candidate_users
            else:
                approved_users = random.sample(candidate_users, k = 6)
            try:
                for userid in approved_users:
                    sql = "INSERT INTO ms2_db.sessions_enrolled (sessionid, userid) VALUES (%s, %s)"
                    cur.execute(sql, args=(sessionid, userid))
                    sql = """
                    DELETE FROM ms2_db.waitlist
                    WHERE userid = %s
                    AND sessionid = %s;
                    """
                    cur.execute(sql, args=(userid, sessionid))
                result = {'success': True, 'message': f'Following users joined the session: {approved_users}'}
            except pymysql.Error as e:
                print(e)
                res = 'ERROR'
                result = {'success': False, 'message': str(e)}
            

        return result

    @staticmethod
    def reset_password(email, old_password, new_password):
        sql_p = "SELECT userid FROM ms2_db.users WHERE email = %s and password= %s;"
        sql = "UPDATE ms2_db.users \
               SET password=%s \
               WHERE email=%s and password= %s;"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_p, args=(email, old_password))
            res = cur.fetchone()
            if res:
                cur.execute(sql, args=(new_password, email, old_password))
                result = {'success': True, 'message': 'Resetting successfully, continue to log in'}
            else:
                result = {'success': False, 'message': 'Forget your password?'}

        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': 'Anything wrong with password...'}
        return result

    @staticmethod
    def show_profile(userid):
        sql = "Select userid, email, username, sex, preference, credits, birthday \
                FROM ms2_db.users WHERE userid = %s ;"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=userid)
            # if register success
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'User_id Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def show_profile2(userid):
        sql = "Select userid, profile_pic, role, email, username, sex, preference, credits, \
               year(birthday) as year, month(birthday) as month, day(birthday) as day \
               FROM ms2_db.users WHERE userid = %s ;"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=userid)
            # if register success
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'User_id Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def show_profile3(userid):
        sql = "Select userid, profile_pic, role, email, username, sex, preference, credits, birthday FROM ms2_db.users WHERE userid = %s ;"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=userid)
            # if register success
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'User_id Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    @staticmethod
    def edit_profile(username, sex, birthday, preference, userid):
        ## , email=%s
        sql_p = "SELECT preference FROM ms2_db.users WHERE userid = %s;"
        sql = "UPDATE ms2_db.users \
               SET username=%s, sex= %s, birthday=%s, preference=%s \
               WHERE userid=%s;"
        ##### need to be editted again...
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_p, args=(userid))
            res = cur.fetchone()
            if res:
                cur.execute(sql, args=(username, sex, birthday, preference, userid))
                # if register success
                result = {'success': True, 'message': 'You have successfully edited the profile'}
            else:
                result = {'success': False, 'message': 'You fail to edit the profile'}

        except pymysql.Error as e:
            print(e)
            res = 'ERROR'
            result = {'success': False, 'message': str(e)}
        return result

    def check_partner(userid):

        sql = "SELECT * FROM ms2_db.users WHERE userid=%s ;"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=(userid))
            # if register success
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'User_id Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def show_profile_by_email(email, number):
        sql = "Select userid, email, username, sex, preference, credits, birthday \
            FROM ms2_db.users WHERE email like  %s limit %s; "
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=('%%%s%%' %email, number))
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'Emails Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def show_profile_by_email_2(email):
        sql = "Select userid, email, username, sex, preference, credits, birthday \
            FROM ms2_db.users WHERE email  =%s; "
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=(email))
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'Emails Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

# %%
