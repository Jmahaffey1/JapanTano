drop table if exists profile;
create table profile (
    id integer primary key autoincrement,
    username text unique not null,
    hPassword text not null,
    login int default 0
);