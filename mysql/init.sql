create database fsi2022;
use fsi2022;

create user 'user'@'172.22.0.3' identified by 'th1s_1s_user_p4ssw0rd';

create table users(
	userseq int not null auto_increment primary key,
	userid varchar(50), 
	userpw varchar(50)
);

create table board(
	seq int not null primary key auto_increment,
	subject varchar(255) not null,
	content varchar(65535) not null,
	filepath varchar(255) not null
);

insert into user (userid, userpw) values ("admin", "th1s_1s_adm111n_p4ssw0rd"); # admin password 가리기
insert into board (subject, content, filepath) values ("flag is here!", "fsi2022{n0w_you_4re_g00d_at_xss_m4ybe?}");

grant select, insert on fsi2022.users to 'user'@'172.22.0.3';
grant select, insert on fsi2022.board to 'user'@'172.22.0.3';
grant file on *.* to 'user'@'172.22.0.3';

flush privileges;