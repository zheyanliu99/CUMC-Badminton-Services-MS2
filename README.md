# CUMC-Badminton-Services-MS2
Microservice2 for CUMC Badminton Services, which contains auth and booking sessions

# Notifications

Use [ms2_db.sql](ms2_db.sql) to init database before running application.py.

## Update for Google login
Please do the following to make it work
* Reinstall requirements.txt
```
pip install -r requirements.txt
```
* Re-init the database using [ms2_db.sql](ms2_db.sql)
* Set up environment variables

```bash
export MS1_URL=http://localhost:5010/
export WEB_APP_URL=http://localhost:4200/
export GOOGLE_CLIENT_ID=432898219349-ufa3r6877k4b3uo7bm8ciiu70vfeh0lb.apps.googleusercontent.com
export GOOGLE_CLIENT_SECRET=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
```
