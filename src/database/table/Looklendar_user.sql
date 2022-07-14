CREATE TABLE IF NOT EXISTS Looklendar_user(
    user_id VARCHAR(20) NOT NULL,
    user_pw VARCHAR(100) NOT NULL,
    user_email VARCHAR(30) NOT NULL,
    user_name VARCHAR(20) NOT NULL,
    user_nickname VARCHAR(20) NOT NULL,
    user_birth DATE,
    user_gender TINYINT NOT NULL DEFAULT 1,
    user_date DATETIME NOT NULL DEFAULT NOW(),
    user_photo VARCHAR(100) NOT NULL,
    PRIMARY KEY(user_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;