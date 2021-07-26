
DROP DATABASE discordia;
CREATE DATABASE discordia;

USE discordia;

CREATE TABLE users(
    user_id BIGINT PRIMARY KEY NOT NULL,
    guild_id BIGINT,
    money INT DEFAULT 0,
    level INT DEFAULT 1,
    xp INT DEFAULT 0,
    life SMALLINT DEFAULT 100,
    pos_x INT NOT NULL,
    pos_y INT NOT NULL,
    info JSON,
    comp JSON,
    equipments JSON,
    sex BOOLEAN,
    fight_comp JSON
);

CREATE TABLE equipments(
    obj_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    user_id BIGINT,
    comp JSON,
    fight_comp JSON,
    name CHAR(25),
    type CHAR(15),
    max_upgrade SMALLINT NOT NULL,
    upgrade SMALLINT NOT NULL,
    sex BOOLEAN
);

CREATE TABLE equipments_specimens(
    comp JSON,
    fight_comp JSON,
    name CHAR(25),
    type CHAR(15),
    sex BOOLEAN,
    finition_possible BOOLEAN
);

CREATE TABLE guilds(
    guild_id BIGINT PRIMARY KEY NOT NULL,
    pos_x INT NOT NULL,
    pos_y INT NOT NULL,
    king_id BIGINT,
    city_name CHAR(25),
    resource_info JSON,
    works JSON,
    techs JSON,
    link CHAR(45)
);

CREATE TABLE worldmap_resources(
    pos_x INT NOT NULL,
    pos_y INT NOT NULL,
    resources_type SMALLINT NOT NULL
);

CREATE TABLE buildings(
    guild_id BIGINT,
    building_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    info JSON,
    pos_x INT NOT NULL,
    pos_y INT NOT NULL,
    is_construct BOOLEAN,
    building_type SMALLINT
);

CREATE TABLE coffre(
    user_id BIGINT PRIMARY KEY NOT NULL,
    consumable JSON,
    basic_obj JSON,
    wood INT DEFAULT 0,
    food INT DEFAULT 0,
    rock INT DEFAULT 0,
    metal INT DEFAULT 0
);

CREATE TABLE seller(
    pos_x INT NOT NULL,
    pos_y INT NOT NULL,
    info JSON
);

CREATE TABLE tasks(
    user_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    stop_task BOOLEAN DEFAULT FALSE
);