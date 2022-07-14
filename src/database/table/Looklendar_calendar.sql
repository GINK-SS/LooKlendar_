CREATE TABLE IF NOT EXISTS Looklendar_calendar(
    event_num INT NOT NULL AUTO_INCREMENT,
    event_title VARCHAR(45) NOT NULL,
    event_color CHAR(7) NOT NULL,
    event_date DATE NOT NULL,
    event_place VARCHAR(45),
    user_id VARCHAR(20) NOT NULL,
    FOREIGN KEY(user_id) REFERENCES Looklendar_user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(event_num)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;