create database fracfocus;
create user fracfocus;
grant all on database fracfocus to fracfocus;
grant all privileges on database fracfocus to fracfocus;
grant usage on schema public to fracfocus;
grant all privileges on all tables in schema public to fracfocus;
grant all privileges on all sequences in schema public to fracfocus;
alter default privileges in schema public grant all on tables to fracfocus;
alter default privileges in schema public grant all on sequences to fracfocus;


