import sqlite3, os
from datetime import datetime, timedelta
from typing import Dict, Any, List

class DatabaseManager:
    def __init__(self, db_path: str="data/learning_platform.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                learning_style TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                topic TEXT,
                question TEXT,
                user_answer TEXT,
                correct_answer TEXT,
                is_correct BOOLEAN,
                difficulty_level INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                topic TEXT,
                current_level INTEGER,
                total_questions INTEGER,
                correct_answers INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id,subject,topic)
            )""")
            # Add streak_count and last_login_date columns if they don't exist
            c.execute("ALTER TABLE users ADD COLUMN streak_count INTEGER DEFAULT 0")
            c.execute("ALTER TABLE users ADD COLUMN last_login_date DATE")
            conn.commit()
    # user helpers
    def create_user(self, name:str, style:str)->int:
        with sqlite3.connect(self.db_path) as conn:
            cur=conn.cursor()
            cur.execute("INSERT INTO users (name,learning_style) VALUES(?,?)",(name,style))
            return cur.lastrowid
    
    def get_user(self, uid:int)->Dict[str,Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory=sqlite3.Row
            cur=conn.cursor()
            cur.execute("SELECT * FROM users WHERE id=?",(uid,))
            row=cur.fetchone()
            return dict(row) if row else {}
    
    def get_all_users(self)->List[Dict[str,Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory=sqlite3.Row
            cur=conn.cursor()
            cur.execute("SELECT * FROM users ORDER BY created_at DESC")
            return [dict(r) for r in cur.fetchall()]
    
    def update_user_settings(self, uid:int, data:Dict[str,Any]):
        with sqlite3.connect(self.db_path) as conn:
            cur=conn.cursor()
            sets=", ".join(f"{k}=?" for k in data)
            cur.execute(f"UPDATE users SET {sets} WHERE id=?",(*data.values(),uid))
            conn.commit()
    # quiz record
    def record_quiz_answer(self, uid:int, subj:str, topic:str, question:str,
                           user_ans:str, correct:str, is_corr:bool, lvl:int):
        with sqlite3.connect(self.db_path) as conn:
            cur=conn.cursor()
            cur.execute("INSERT INTO quiz_attempts (user_id,subject,topic,question,user_answer,correct_answer,is_correct,difficulty_level) VALUES (?,?,?,?,?,?,?,?)",
                        (uid,subj,topic,question,user_ans,correct,is_corr,lvl))
            # progress table
            cur.execute("""INSERT INTO user_progress
                (user_id,subject,topic,current_level,total_questions,correct_answers)
                VALUES (?,?,?,?,1,?)
                ON CONFLICT(user_id,subject,topic) DO UPDATE SET
                    total_questions=total_questions+1,
                    correct_answers=correct_answers+?,
                    current_level=excluded.current_level,
                    last_updated=CURRENT_TIMESTAMP""",
                (uid,subj,topic,lvl,1 if is_corr else 0,1 if is_corr else 0))
            conn.commit()
    # stats
    def get_user_stats(self, uid:int)->Dict[str,Any]:
        with sqlite3.connect(self.db_path) as conn:
            cur=conn.cursor()
            cur.execute("SELECT COUNT(*), SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) FROM quiz_attempts WHERE user_id=?", (uid,))
            total,correct=cur.fetchone()
            cur.execute("SELECT MAX(difficulty_level) FROM quiz_attempts WHERE user_id=?", (uid,))
            level=cur.fetchone()[0] or 1
            return {"total_questions":total or 0,"correct_answers":correct or 0,"current_level":level}
    
    def get_user_topic_level(self,uid:int,subj:str,topic:str)->int:
        with sqlite3.connect(self.db_path) as conn:
            cur=conn.cursor()
            cur.execute("SELECT current_level FROM user_progress WHERE user_id=? AND subject=? AND topic=?", (uid,subj,topic))
            row=cur.fetchone()
            return row[0] if row else 1
    
    def get_subject_stats(self,uid:int)->List[Dict[str,Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory=sqlite3.Row
            cur=conn.cursor()
            cur.execute("SELECT subject, COUNT(*) total_questions, SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) correct_answers, ROUND(AVG(CASE WHEN is_correct THEN 100 ELSE 0 END),1) accuracy FROM quiz_attempts WHERE user_id=? GROUP BY subject",(uid,))
            return [dict(r) for r in cur.fetchall()]
    
    def get_topic_stats(self,uid:int,subj:str,topic:str)->Dict[str,Any]:
        with sqlite3.connect(self.db_path) as conn:
            cur=conn.cursor()
            cur.execute("SELECT COUNT(*), SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) FROM quiz_attempts WHERE user_id=? AND subject=? AND topic=?", (uid,subj,topic))
            total,correct = cur.fetchone()
            return {"total_questions": total or 0, "correct": correct or 0}
    
    def get_user_progress_data(self,uid:int)->List[Dict[str,Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory=sqlite3.Row
            cur=conn.cursor()
            cur.execute("SELECT DATE(timestamp) date, ROUND(AVG(CASE WHEN is_correct THEN 100 ELSE 0 END),1) accuracy FROM quiz_attempts WHERE user_id=? GROUP BY DATE(timestamp)",(uid,))
            return [dict(r) for r in cur.fetchall()]
        
    def get_user_streak_data(self, uid: int) -> Dict[str, Any]:
        """
        Retrieves the user's daily streak count and last login date.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Fetch the last login date and streak count
            cur.execute("""
                SELECT streak_count, last_login_date
                FROM users
                WHERE id = ?
            """, (uid,))
            row = cur.fetchone()
            
            # If no data exists, initialize streak count and last login date
            if not row:
                return {"streak_count": 0, "last_login_date": None}
            
            streak_count = row["streak_count"]
            last_login_date = row["last_login_date"]
            
            # Convert last_login_date to a Python date object
            if last_login_date:
                last_login_date = datetime.strptime(last_login_date, "%Y-%m-%d").date()
            
            return {"streak_count": streak_count, "last_login_date": last_login_date}

    def update_user_login(self, uid: int):
        """
        Updates the user's login streak and last login date.
        """
        today = datetime.now().date()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            # Fetch the current streak and last login date
            cur.execute("""
                SELECT streak_count, last_login_date
                FROM users
                WHERE id = ?
            """, (uid,))
            row = cur.fetchone()
            
            if row:
                streak_count = row[0]
                last_login_date = row[1]
                
                # Convert last_login_date to a Python date object
                if last_login_date:
                    last_login_date = datetime.strptime(last_login_date, "%Y-%m-%d").date()
                
                # Update streak count based on login date
                if last_login_date == today:
                    # Already logged in today, no update needed
                    return
                elif last_login_date == today - timedelta(days=1):
                    # Increment streak count
                    streak_count += 1
                else:
                    # Reset streak count
                    streak_count = 1
                
                # Update the database
                cur.execute("""
                    UPDATE users
                    SET streak_count = ?, last_login_date = ?
                    WHERE id = ?
                """, (streak_count, today.strftime("%Y-%m-%d"), uid))
            else:
                # Initialize streak count and last login date for new user
                cur.execute("""
                    UPDATE users
                    SET streak_count = 1, last_login_date = ?
                    WHERE id = ?
                """, (today.strftime("%Y-%m-%d"), uid))
            
            conn.commit()
