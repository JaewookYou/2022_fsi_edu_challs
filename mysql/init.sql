SET collation_connection = 'utf8_general_ci';

#drop database fsi2022;
create database fsi2022;
ALTER DATABASE fsi2022 CHARACTER SET utf8 COLLATE utf8_general_ci;

use fsi2022;

#drop table users;
#drop table board;

create user 'user'@'%' identified by 'th1s_1s_user_p4ssw0rd';

create table users(
	userseq int not null auto_increment primary key,
	userid varchar(50) not null, 
	userpw varchar(255) not null
);

create table board(
	seq int not null primary key auto_increment,
	subject varchar(255) not null,
	content varchar(255) not null,
	author varchar(255) not null,
	loginid varchar(255),
	filepath varchar(255)
);

ALTER TABLE users CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE board CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;

insert into users (userid, userpw) values ("admin", "th1s_1s_adm111n_p4ssw0rd"); # admin password 가리기
insert into board (subject, content, author, loginid, filepath) values ("flag is here!", "fsi2022{n0w_you_4re_g00d_at_xss_m4ybe?}", "admin", "admin", null);

grant select, insert on users to 'user'@'%';
grant select, insert on board to 'user'@'%';
grant file on *.* to 'user'@'%';

flush privileges;