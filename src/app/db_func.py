from pymysql import *
import sys
import re
from datetime import datetime
from werkzeug.utils import secure_filename

UPLOAD_PATH = "/static/files/"
IMG_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

#ok# 공백 확인
def isBlank(text):
    encText = text

    blankCount = re.findall(' ', encText)

    return blankCount
#ok# 한글 확인 (한글 있으면 들어있는 리스트, 없으면 빈 리스트)
def isHangul(text):
    encText = text
    
    hanCount = re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', encText)

    return hanCount

#ok# 기타 특수문자 확인 (특수문자 있으면 들어있는 리스트, 없으면 빈 리스트)
def isSpecial(text):
    encText = text

    SpeCount = re.findall(u'[^\w\s]', encText)

    return SpeCount

#ok# (이메일만) 기타 특수문자 확인 (이메일 중 앞에 아이디 부분만 추출하기 위하여)
def is_emailSpecial(text):
    encText = text
    pattern = '(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
    text = re.sub(pattern=pattern, repl='', string=text)
    SpeCount = re.findall(u'[^\w\s]', text)

    return SpeCount
#ok# 한글 자음, 모음 확인 (온전한 한글이 아닌 것 확인)
def isHangulzmo(text):
    encText = text
    zmoCount = re.findall(u'[\u3131-\u3163]+', encText)
    
    return zmoCount

#ok# 이메일 형식인지 확인
def is_emailFormat(text):
    p = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    encText = text
    EF = p.match(encText)

    return EF

#ok# 생일 오류 확인 (1900년 이전이거나 오늘날짜보다 미래날짜를 입력했을 경우 및 생일 포맷인지를 확인)
def birth_check(BIRTH):
    system_date_format = '%Y%m%d'

    try:
        birthday = datetime.strptime(BIRTH, system_date_format)
    except ValueError:
        return "Wrong"
    
    if datetime.now() < birthday:
        return "Wrong"
    birthTuple = birthday.timetuple()
    if birthTuple.tm_year < 1900:
        return "Wrong"

####################################
### DB 연동/처리 코드 #################
####################################
#ok# 아이디 중복확인 (대소문자 구별 X)
def user_id_check(db, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT user_id 
        FROM v_Looklendar_user 
        WHERE user_id = %s;
        '''
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
    if result:
        return "exist"

#ok# 닉네임 중복확인 (대소문자 구별 X)
def user_nick_check(db, user_nickname):
    with db.cursor() as cursor:
        query = '''
        SELECT user_nickname 
        FROM v_Looklendar_user 
        WHERE user_nickname = %s;
        '''
        cursor.execute(query, (user_nickname,))
        result = cursor.fetchone()
    if result:
        return "exist"

#ok# 이메일 중복확인 (대소문자 구별 X)
def user_email_check(db, user_email):
    with db.cursor() as cursor:
        query = '''
        SELECT user_email 
        FROM v_Looklendar_user 
        WHERE user_email = %s;
        '''
        cursor.execute(query, (user_email,))
        result = cursor.fetchone()
    if result:
        return "exist"

# 닉네임 수정 시 중복확인 (대소문자 구별 X, 본인의 기존 닉네임 제외)
def user_nick_check2(db, user_nickname, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT user_nickname 
        FROM v_Looklendar_user 
        WHERE user_nickname = %s AND user_id <> %s;
        '''
        cursor.execute(query, (user_nickname, user_id,))
        result = cursor.fetchone()
    if result:
        return "exist"

#ok# 이메일 수정 시 중복확인 (대소문자 구별 X, 본인의 기존 이메일 제외)
def user_email_check2(db, user_email, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT user_email 
        FROM v_Looklendar_user 
        WHERE user_email = %s AND user_id <> %s;
        '''
        cursor.execute(query, (user_email, user_id,))
        result = cursor.fetchone()
    if result:
        return "exist"        
        
#ok# 유저 정보 저장
def user_insert(db, user_data):
    with db.cursor() as cursor:
        query = '''
        INSERT INTO Looklendar_user
            (user_id, user_pw, user_email, user_name, user_nickname, user_birth, user_gender, user_photo, user_date) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, NOW());
        '''
        cursor.execute(query, user_data)
    db.commit()

    return "success"

#ok# 유저 정보 반환
def user_select(db, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT * 
        FROM v_Looklendar_user 
        WHERE user_id = %s;
        '''
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result is None:
            return "NOT FOUND"
    return result

#ok# 비밀번호 필요 시 유저 정보 반환
def user_selectp(db, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT * 
        FROM Looklendar_user 
        WHERE user_id = %s;
        '''
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result is None:
            return "NOT FOUND"
    return result

#ok# 아이디 찾기
def user_find_id(db, user_name, user_email):
    with db.cursor() as cursor:
        query = '''
        SELECT user_id 
        FROM v_Looklendar_user 
        WHERE user_name = %s AND user_email = %s;
        '''
        cursor.execute(query, (user_name, user_email,))
        result = cursor.fetchone()

    return result

# 비밀번호만 변경 
def user_pw_modify(db, new_pw, user_id):
    with db.cursor() as cursor:
        query = '''
        UPDATE Looklendar_user 
        SET user_pw = %s 
        WHERE user_id = %s;
        '''
        cursor.execute(query, (new_pw, user_id,))
    db.commit()

    return "SUCCESS"

#ok# 유저 정보 변경
def user_modify(db, user_new_data):
    with db.cursor() as cursor:
        query = '''
        UPDATE v_Looklendar_user 
        SET user_email = %s, user_nickname = %s, user_birth = %s, user_gender = %s, user_photo = %s 
        WHERE user_id = %s;
        '''
        cursor.execute(query, user_new_data)
    db.commit()

    return "SUCCESS"

#ok# 사진 변경 안 했을 시 유저 정보 변경 (사진은 그대로 유지)
def user_modify2(db, user_new_data):
    with db.cursor() as cursor:
        query = '''
        UPDATE v_Looklendar_user 
        SET user_email = %s, user_nickname = %s, user_birth = %s, user_gender = %s 
        WHERE user_id = %s;
        '''
        cursor.execute(query, user_new_data)
    db.commit()

    return "SUCCESS"

# 유저 정보 삭제 (회원탈퇴)
def user_out(db, user_id):
    with db.cursor() as cursor:
        query = '''
        DELETE 
        FROM Looklendar_user 
        WHERE user_id = %s;
        '''
        cursor.execute(query, (user_id,))
    db.commit()

    return "SUCCESS"

#ok# 룩 일정 달력에 저장 
def look_insert(db, look_data, look_data2):
    with db.cursor() as cursor:
        query = '''
        INSERT INTO Looklendar_calendar
            (event_title, event_color, user_id, event_date, event_place) 
        VALUES(%s, %s, %s, %s, %s);
        '''
        cursor.execute(query, look_data)
        db.commit()
        query = '''
        INSERT INTO Looklendar_look
            (look_num, look_photo, look_s_photo, look_outer, look_top, look_bot, look_shoes, look_acc) 
        VALUES(
            (SELECT event_num 
            FROM Looklendar_calendar 
            WHERE user_id = %s AND event_date = %s 
            ORDER BY event_num DESC LIMIT 1), 
            %s, %s, %s, %s, %s, %s, %s);
        '''
        cursor.execute(query, look_data2)
    db.commit()

    return "success"

#ok# 룩 일정 달력 찾기
def look_select(db, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT * 
        FROM v_Looklendar_look 
        WHERE user_id = %s;
        '''
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
    return result

#ok# 룩 일정 달력 변경
def look_modify(db, look_new_data, look_new_data2):
    with db.cursor() as cursor:
        query = '''
        UPDATE Looklendar_calendar 
        SET event_title = %s, event_color = %s, event_date = %s, event_place = %s 
        WHERE event_num = %s;
        '''
        cursor.execute(query, look_new_data)
        query = '''
        UPDATE Looklendar_look 
        SET look_photo = %s, look_s_photo = %s, look_outer = %s, look_top = %s, look_bot = %s, look_shoes = %s, look_acc = %s 
        WHERE look_num = %s;
        '''
        cursor.execute(query, look_new_data2)
    db.commit()

    return "SUCCESS"

#ok# 사진 변경 안 했을 시 룩 일정 달력 변경 (사진은 그대로 유지) 
def look_modify2(db, look_new_data, look_new_data2):
    with db.cursor() as cursor:
        query = '''
        UPDATE Looklendar_calendar 
        SET event_title = %s, event_color = %s, event_date = %s, event_place = %s 
        WHERE event_num = %s;
        '''
        cursor.execute(query, look_new_data)
        query = '''
        UPDATE Looklendar_look 
        SET look_outer = %s, look_top = %s, look_bot = %s, look_shoes = %s, look_acc = %s 
        WHERE look_num = %s;
        '''
        cursor.execute(query, look_new_data2)
    db.commit()

    return "SUCCESS"

#ok# 룩 일정 달력 삭제 
def look_delete(db, event_num):
    with db.cursor() as cursor:
        query = '''
        DELETE 
        FROM Looklendar_calendar 
        WHERE event_num = %s;
        '''
        cursor.execute(query, (event_num,))
    db.commit()

    return "success"

#ok# 일정 달력 찾기
def event_select(db, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT 
            cal.event_num, cal.event_title, cal.event_color, cal.user_id, 
            CONCAT(
                year(cal.event_date), '-', 
                IF(LENGTH(month(cal.event_date))<>2, 
                    CONCAT('0', month(cal.event_date)), month(cal.event_date)), '-', 
                IF(LENGTH(day(cal.event_date))<>2, 
                    CONCAT('0', day(cal.event_date)), day(cal.event_date))
            ) AS event_date, 
            cal.event_place, lo.look_num 
        FROM Looklendar_calendar AS cal 
        LEFT JOIN Looklendar_look AS lo 
        ON cal.event_num = lo.look_num 
        WHERE cal.user_id = %s;
        '''
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

    return result

#ok# 일정 달력에 저장 
def event_insert(db, event_data):
    with db.cursor() as cursor:
        query = '''
        INSERT INTO 
        Looklendar_calendar(event_title, event_color, event_date, event_place, user_id) 
        VALUES(%s, %s, %s, %s, %s);
        '''
        cursor.execute(query, event_data)
    db.commit()

    return "success"

#ok# 일정 달력 변경 
def event_modify(db, event_new_data):
    with db.cursor() as cursor:
        query = '''
        UPDATE Looklendar_calendar 
        SET event_title = %s, event_date = %s, event_color = %s, event_place = %s 
        WHERE event_num = %s;
        '''
        cursor.execute(query, event_new_data)
    db.commit()

    return "SUCCESS"

#ok# 일정 달력 삭제 
def event_delete(db, event_num):
    with db.cursor() as cursor:
        query = '''
        DELETE 
        FROM Looklendar_calendar 
        WHERE event_num = %s;
        '''
        cursor.execute(query, (event_num,))
    db.commit()

    return "success"

# 커뮤니티 전체 글 반환
def boards_select(db, page):
    with db.cursor() as cursor:
        query = '''
        SELECT 
            DL_Li.*, DL_U.dailylook_title, DL_U.user_nickname, DL_U.dailylook_date, DL_U.dailylook_view, DL_U.dailylook_photo 
        FROM 
            (SELECT DL.dailylook_num, DL.dailylook_title, U.user_nickname, DL.dailylook_date, DL.dailylook_view, DL.dailylook_photo 
            FROM Looklendar_dailylook AS DL 
            JOIN Looklendar_user AS U 
            ON DL.user_id = U.user_id 
            ORDER BY DL.dailylook_date) AS DL_U 
        JOIN 
            (SELECT DL.dailylook_num, COUNT(Li.dailylook_num) AS LIKEE 
            FROM Looklendar_dailylook AS DL 
            LEFT JOIN Looklendar_like AS Li 
            ON DL.dailylook_num = Li.dailylook_num 
            GROUP BY DL.dailylook_num) AS DL_Li 
        ON DL_U.dailylook_num = DL_Li.dailylook_num 
        ORDER BY DL_U.dailylook_date DESC, DL_U.dailylook_num DESC 
        LIMIT %s, 12;
        '''
        cursor.execute(query, page*12-12,)
        result = cursor.fetchall()
    return result

# 커뮤니티 검색 글 반환 (option == 1 이면 제목 검색, 2 이면 닉네임 검색)
def boards_select_search(db, text, page, option):
    with db.cursor() as cursor:
        # option이 1이면 제목 검색
        if option == "1":
            query = '''
            SELECT 
                DL_Li.*, DL_U.dailylook_title, DL_U.user_nickname, DL_U.dailylook_date, DL_U.dailylook_view, DL_U.dailylook_photo 
            FROM 
                (SELECT DL.dailylook_num, DL.dailylook_title, U.user_nickname, DL.dailylook_date, DL.dailylook_view, DL.dailylook_photo 
                FROM Looklendar_dailylook AS DL 
                JOIN Looklendar_user AS U 
                ON DL.user_id = U.user_id 
                ORDER BY DL.dailylook_date) AS DL_U 
            JOIN 
                (SELECT DL.dailylook_num, COUNT(Li.dailylook_num) AS LIKEE 
                FROM Looklendar_dailylook AS DL 
                LEFT JOIN Looklendar_like AS Li 
                ON DL.dailylook_num = Li.dailylook_num 
                GROUP BY DL.dailylook_num) AS DL_Li 
            ON DL_U.dailylook_num = DL_Li.dailylook_num 
            WHERE DL_U.dailylook_title REGEXP %s
            ORDER BY DL_U.dailylook_date DESC, DL_U.dailylook_num DESC  
            LIMIT %s, 12;
            '''
            cursor.execute(query, (text, page,))
        # option이 2이면 닉네임 검색
        elif option == "2":
            query = '''
            SELECT 
                DL_Li.*, DL_U.dailylook_title, DL_U.user_nickname, DL_U.dailylook_date, DL_U.dailylook_view, DL_U.dailylook_photo 
            FROM 
                (SELECT DL.dailylook_num, DL.dailylook_title, U.user_nickname, DL.dailylook_date, DL.dailylook_view, DL.dailylook_photo 
                FROM Looklendar_dailylook AS DL 
                JOIN Looklendar_user AS U 
                ON DL.user_id = U.user_id 
                ORDER BY DL.dailylook_date) AS DL_U 
            JOIN 
                (SELECT DL.dailylook_num, COUNT(Li.dailylook_num) AS LIKEE 
                FROM Looklendar_dailylook AS DL 
                LEFT JOIN Looklendar_like AS Li 
                ON DL.dailylook_num = Li.dailylook_num 
                GROUP BY DL.dailylook_num) AS DL_Li 
            ON DL_U.dailylook_num = DL_Li.dailylook_num 
            WHERE DL_U.user_nickname REGEXP %s
            ORDER BY DL_U.dailylook_date DESC, DL_U.dailylook_num DESC  
            LIMIT %s, 12;
            '''
            cursor.execute(query, (text, page,))
    result = cursor.fetchall()
    return result

# 커뮤니티 정렬 글 반환 (option == 1 이면 조회 수 정렬, 2 이면 좋아요 수 정렬)
def boards_select_array(db, page, option):
    with db.cursor() as cursor:
        if option == "1":
            query = '''
            SELECT 
                DL_Li.*, DL_U.dailylook_title, DL_U.user_nickname, DL_U.dailylook_date, DL_U.dailylook_view, DL_U.dailylook_photo 
            FROM 
                (SELECT DL.dailylook_num, DL.dailylook_title, U.user_nickname, DL.dailylook_date, DL.dailylook_view, DL.dailylook_photo 
                FROM Looklendar_dailylook AS DL 
                JOIN Looklendar_user AS U 
                ON DL.user_id = U.user_id 
                ORDER BY DL.dailylook_date) AS DL_U 
            JOIN 
                (SELECT DL.dailylook_num, COUNT(Li.dailylook_num) AS LIKEE 
                FROM Looklendar_dailylook AS DL 
                LEFT JOIN Looklendar_like AS Li 
                ON DL.dailylook_num = Li.dailylook_num 
                GROUP BY DL.dailylook_num) AS DL_Li 
            ON DL_U.dailylook_num = DL_Li.dailylook_num 
            ORDER BY DL_U.dailylook_view DESC, DL_U.dailylook_date DESC, DL_U.dailylook_num DESC 
            LIMIT %s, 12;
            '''
            cursor.execute(query, page*12-12,)
        elif option == "2":
            query = '''
            SELECT 
                DL_Li.*, DL_U.dailylook_title, DL_U.user_nickname, DL_U.dailylook_date, DL_U.dailylook_view, DL_U.dailylook_photo 
            FROM 
                (SELECT DL.dailylook_num, DL.dailylook_title, U.user_nickname, DL.dailylook_date, DL.dailylook_view, DL.dailylook_photo 
                FROM Looklendar_dailylook AS DL 
                JOIN Looklendar_user AS U 
                ON DL.user_id = U.user_id 
                ORDER BY DL.dailylook_date) AS DL_U 
            JOIN 
                (SELECT DL.dailylook_num, COUNT(Li.dailylook_num) AS LIKEE 
                FROM Looklendar_dailylook AS DL 
                LEFT JOIN Looklendar_like AS Li 
                ON DL.dailylook_num = Li.dailylook_num 
                GROUP BY DL.dailylook_num) AS DL_Li 
            ON DL_U.dailylook_num = DL_Li.dailylook_num 
            ORDER BY DL_Li.LIKEE DESC, DL_U.dailylook_date DESC, DL_U.dailylook_num DESC 
            LIMIT %s, 12;
            '''
            cursor.execute(query, page*12-12,)
    result = cursor.fetchall()
    return result

# 커뮤니티 단일 글 반환
def board_select(db, dailylook_num):
    with db.cursor() as cursor:
        query = '''
        SELECT 
            DL_Li.*, DL_U.dailylook_title, NICK, DL_U.dailylook_text, DL_U.dailylook_date, 
            DL_U.dailylook_outer, DL_U.dailylook_top, DL_U.dailylook_bot, DL_U.dailylook_shoes, DL_U.dailylook_acc, DL_U.dailylook_view, DL_U.dailylook_photo 
        FROM 
            (SELECT 
                DL.dailylook_num, DL.dailylook_title, U.user_nickname AS NICK, DL.dailylook_text, DL.dailylook_date, 
                DL.dailylook_outer, DL.dailylook_top, DL.dailylook_bot, DL.dailylook_shoes, DL.dailylook_acc, DL.dailylook_view, DL.dailylook_photo 
            FROM Looklendar_dailylook AS DL 
            JOIN Looklendar_user AS U 
            ON DL.user_id = U.user_id ORDER BY DL.dailylook_date) AS DL_U 
        JOIN 
            (SELECT DL.dailylook_num, COUNT(Li.dailylook_num) AS LIKEE 
            FROM Looklendar_dailylook AS DL 
            LEFT JOIN Looklendar_like AS Li 
            ON DL.dailylook_num = Li.dailylook_num 
            GROUP BY DL.dailylook_num) AS DL_Li 
        ON DL_U.dailylook_num = DL_Li.dailylook_num 
        WHERE DL_U.dailylook_num = %s;
        '''
        cursor.execute(query, (dailylook_num,))
        result = cursor.fetchone()

    return result

# 커뮤니티 글의 주인인지 확인
def board_apply(db, dailylook_num, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT dailylook_num 
        FROM Looklendar_dailylook 
        WHERE dailylook_num = %s AND user_id = %s;
        '''
        cursor.execute(query, (dailylook_num, user_id,))
        result = cursor.fetchone()
    if result:
        return "OK"
    return "FUCK"

# 커뮤니티 글 작성
def board_insert(db, board_data):
    with db.cursor() as cursor:
        query = '''
        INSERT INTO Looklendar_dailylook
            (dailylook_title, dailylook_text, dailylook_date, user_id, 
            dailylook_outer, dailylook_top, dailylook_bot, dailylook_shoes, dailylook_acc, dailylook_photo) 
        VALUES(%s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s);
        '''
        cursor.execute(query, board_data)
    db.commit()

    return "success"

# 커뮤니티 글 수정
def board_modify(db, board_new_data):
    with db.cursor() as cursor:
        query = '''
        UPDATE Looklendar_dailylook 
        SET dailylook_title = %s, dailylook_text = %s, 
            dailylook_outer = %s, dailylook_top = %s, dailylook_bot = %s, dailylook_shoes = %s, dailylook_acc = %s, dailylook_photo = %s 
        WHERE dailylook_num = %s;
        '''
        cursor.execute(query, board_new_data)
    db.commit()

    return "success"

# 커뮤니티 글 수정 (사진은 그대로 유지)
def board_modify2(db, board_new_data):
    with db.cursor() as cursor:
        query = '''
        UPDATE Looklendar_dailylook 
        SET dailylook_title = %s, dailylook_text = %s, 
            dailylook_outer = %s, dailylook_top = %s, dailylook_bot = %s, dailylook_shoes = %s, dailylook_acc = %s 
        WHERE dailylook_num = %s;
        '''
        cursor.execute(query, board_new_data)
    db.commit()

    return "success"

# 커뮤니티 글 삭제
def board_delete(db, dailylook_num):
    with db.cursor() as cursor:
        query = '''
        DELETE 
        FROM Looklendar_dailylook 
        WHERE dailylook_num = %s;
        '''
        cursor.execute(query, (dailylook_num,))
    db.commit()

    return "success"

# 커뮤니티 좋아요 등록 및 취소
def board_like_upNdown(db, dailylook_num, user_id):
    with db.cursor() as cursor:
        # db에서 좋아요 했는지 안 했는지 확인
        query = '''
        SELECT dailylook_num 
        FROM Looklendar_like 
        WHERE dailylook_num = %s AND user_id = %s;
        '''
        cursor.execute(query, (dailylook_num, user_id,))
        result = cursor.fetchone()
        # 만약 좋아요를 눌렀었다면 좋아요 취소
        if result:
            query = '''
            DELETE 
            FROM Looklendar_like 
            WHERE dailylook_num = %s AND user_id = %s;
            '''
            cursor.execute(query, (dailylook_num, user_id,))
            db.commit()
            return "down"
        # 만약 좋아요를 안 눌렀었다면 좋아요 등록
        else:    
            query = '''
            INSERT INTO Looklendar_like
                (dailylook_num, user_id) 
            VALUES(%s, %s);
            '''
            cursor.execute(query, (dailylook_num, user_id,))
            db.commit()
            return "up"

# 조회수 증가
def board_view(db, dailylook_num):
    with db.cursor() as cursor:
        query = '''
        UPDATE Looklendar_dailylook 
        SET dailylook_view = dailylook_view + 1 
        WHERE dailylook_num = %s;
        '''
        cursor.execute(query, (dailylook_num,))
    db.commit()

    return "success"

# 댓글 반환
def comment_select(db, comment_num):
    with db.cursor() as cursor:
        query = '''
        SELECT com.comment_num, com.comment_text, U.user_nickname, com.dailylook_num, com.comment_date 
        FROM Looklendar_comment AS com 
        JOIN Looklendar_user AS U 
        ON com.user_id = U.user_id 
        WHERE com.dailylook_num = %s 
        ORDER BY com.comment_date ASC;
        '''
        cursor.execute(query, (comment_num,))
        result = cursor.fetchall()

    return result

# 댓글 유저 확인
def comment_apply(db, comment_num, user_id):
    with db.cursor() as cursor:
        query = '''
        SELECT comment_num 
        FROM Looklendar_comment 
        WHERE comment_num = %s AND user_id = %s;
        '''
        cursor.execute(query, (comment_num, user_id,))
        result = cursor.fetchone()
    if result:
        return "OK"
    return "FUCK"
# 댓글 작성
def comment_upload(db, comment_data):
    with db.cursor() as cursor:
        query = '''
        INSERT INTO Looklendar_comment
            (comment_text, user_id, dailylook_num, comment_date) 
        VALUES(%s, %s, %s, NOW());
        '''
        cursor.execute(query, comment_data)
    db.commit()

    return "success"

# 댓글 수정
def comment_modify(db, comment_num, comment_text):
    with db.cursor() as cursor:
        query = '''
        UPDATE Looklendar_comment 
        SET comment_text = %s 
        WHERE comment_num = %s;
        '''
        cursor.execute(query, (comment_text, comment_num,))
    db.commit()
    
    return "success"

# 댓글 삭제
def comment_delete(db, comment_num):
    with db.cursor() as cursor:
        query = '''
        DELETE 
        FROM Looklendar_comment 
        WHERE comment_num = %s;
        '''
        cursor.execute(query, (comment_num,))
    db.commit()

    return "success"

# 파일 이름/경로 생성 및 확장자/길이 확인(이미지만! 원본 + 미리보기) 
def file_name_encode(file_name):
    # 허용 확장자 / 길이인지 확인
    if secure_filename(file_name).split('.')[-1].lower() in IMG_EXTENSIONS and len(file_name) < 240:

        # 원본 파일
        path_name = str(datetime.today().strftime("%Y%m%d%H%M%S%f")) + '_' + file_name
        # 오류 방지용 (사진 미등록 시, 기본 이미지로 저장)
        if file_name == "user_image1.jpg":
            path_name = "user_image1.jpg"
        if file_name == "look_default.png":
            path_name = "look_default.png"
        # 미리보기 파일
        s_path_name = 'S-' + path_name

        return {"original": path_name, "resize": s_path_name}

    else:
        return None
