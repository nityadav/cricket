DROP DATABASE IF EXISTS cricketdb;
CREATE DATABASE cricketdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cricketdb;
GRANT ALL PRIVILEGES ON cricketdb.* TO 'cricket_dev'@'localhost' IDENTIFIED BY 'cricket_is_life';
FLUSH PRIVILEGES;

DROP TABLE IF EXISTS teams;
CREATE TABLE teams (
) ENGINE=InnoDB;

DROP TABLE IF EXISTS players;
CREATE TABLE players (
) ENGINE=InnoDB;

DROP TABLE IF EXISTS matches;
CREATE TABLE matches (
	id INT AUTO_INCREMENT,
	cricinfo_id VARCHAR(50),
	team1 VARCHAR(50),
	team2 VARCHAR(50),
	won_by VARCHAR(50),
	mom VARCHAR(50),
	ground VARCHAR(50),
	dated TIMESTAMP,
	PRIMARY KEY (id),
	UNIQUE(cricinfo_id)
) ENGINE=InnoDB;