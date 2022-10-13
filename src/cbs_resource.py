# %%
import pymysql

import os


class CBSresource:

    def __int__(self):
        pass

    @staticmethod
    def _get_connection():

        # set by environment variables
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

    @staticmethod
    def get_user_by_key(key):

        sql = "SELECT * FROM ms2_db.users where userid=%s"
        conn = CBSresource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=key)
        result = cur.fetchone()

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
            result = {'success':True, 'message':'Register successfully, continue to log in'}
        except pymysql.Error as e:
            print(e)
            result = {'success':False, 'message':'This email is already registered, try another one'}
        return result

        
        



# %%
