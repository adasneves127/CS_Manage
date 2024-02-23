DROP DATABASE IF EXISTS Invoices;
CREATE DATABASE IF NOT EXISTS Invoices;
USE Invoices;

create table users(
    seq int primary key auto_increment not null,
    user_name varchar(20),
    first_name varchar(20),
    last_name varchar(20),
    email varchar(30),
    password varchar(255),
    system_user bool default 0,
    theme bool default 1,
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq)
);

create table permissions(
    seq            INT auto_increment PRIMARY KEY,
    user_seq            INT                  NOT NULL,
    inv_edit            bool default 0 NULL,
    inv_view            bool default 0 NULL,
    doc_edit            bool default 0 NULL,
    doc_view            bool default 0 NULL,
    inv_admin           bool default 0 NULL,
    doc_admin           bool default 0 NULL,
    approve_invoices    bool default 0 NOT NULL,
    receive_emails      bool default 0 NULL,
    user_admin          bool default 0 NULL,
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (user_seq) references users(seq)
);

create table statuses(
    seq int not null auto_increment primary key,
    stat_desc varchar(20),
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq)
);

create table record_types(
    seq int not null auto_increment primary key,
    type_desc varchar(20),
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq)
);

create table inv_head(
    seq int not null auto_increment primary key,
    id varchar(10) UNIQUE,
    creator int not null,
    approver int not null,
    record_status int not null,
    record_type int not null,
    tax decimal(8,2),
    fees decimal(8,2),
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (creator) references users(seq),
    CONSTRAINT FOREIGN KEY (approver) references users(seq),
    CONSTRAINT FOREIGN KEY (record_type) references record_types(seq),
    CONSTRAINT FOREIGN KEY (record_status) references statuses(seq)
);

create table valid_items (
    seq int not null primary key auto_increment,
    item_desc varchar(30),
    item_price decimal(8,3),
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq)
);

create table inv_line(
    inv_seq int not null primary key auto_increment,
    item_seq int not null,
    qty int,
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (inv_seq) references inv_head(seq),
    CONSTRAINT FOREIGN KEY (item_seq) references valid_items(seq)
);


CREATE TABLE password_reset
(
    seq int auto_increment primary key,
    user_seq int not null unique,
    token varchar(40) not null unique,
    created_at datetime default CURRENT_TIMESTAMP,
    created_by varchar(15),

    constraint foreign key (user_seq) references users (seq)
);

create trigger date_check_update_users
before update on users
for each row
begin
    if (old.dt_added IS NOT NULL and old.dt_added != new.dt_added) then
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set date';
    end if ;
    if (old.added_by IS NOT NULL and old.added_by != new.added_by) then
       SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set added_by';
   end if;
end;

create trigger date_check_update_permissions
before update on permissions
for each row
begin
    if (old.dt_added IS NOT NULL and old.dt_added != new.dt_added) then
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set date';
    end if ;
    if (old.added_by IS NOT NULL and old.added_by != new.added_by) then
       SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set added_by';
   end if;
end;

create trigger date_check_update_inv_head
before update on inv_head
for each row
begin
    if (old.dt_added IS NOT NULL and old.dt_added != new.dt_added) then
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set date';
    end if ;
    if (old.added_by IS NOT NULL and old.added_by != new.added_by) then
       SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set added_by';
   end if;
end;

create trigger date_check_update_valid_items
before update on valid_items
for each row
begin
    if (old.dt_added IS NOT NULL and old.dt_added != new.dt_added) then
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set date';
    end if ;
    if (old.added_by IS NOT NULL and old.added_by != new.added_by) then
       SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set added_by';
   end if;
end;

create trigger date_check_update_inv_line
before update on inv_line
for each row
begin
    if (old.dt_added IS NOT NULL and old.dt_added != new.dt_added) then
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set date';
    end if ;
    if (old.added_by IS NOT NULL and old.added_by != new.added_by) then
       SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set added_by';
   end if;
end;
# inv_line

create trigger date_check_update_statuses
before update on statuses
for each row
begin
    if (old.dt_added IS NOT NULL and old.dt_added != new.dt_added) then
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set date';
    end if ;
    if (old.added_by IS NOT NULL and old.added_by != new.added_by) then
       SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set added_by';
   end if;
end;


create trigger date_check_update_record_types
before update on record_types
for each row
begin
    if (old.dt_added IS NOT NULL and old.dt_added != new.dt_added) then
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set date';
    end if ;
    if (old.added_by IS NOT NULL and old.added_by != new.added_by) then
       SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot set added_by';
   end if;
end;



create trigger check_user_approve_vs_create
before update on inv_head
for each row
begin
    if (new.approver = new.creator) then
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot approve own invoice';
    end if;
end;