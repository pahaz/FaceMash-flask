drop table if exists scores;
create table scores (
  id integer primary key autoincrement,
  date text not null,
  win_id integer not null,
  lose_id integer not null
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  photo text not null
);
