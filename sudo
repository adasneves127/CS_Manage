DROP DATABASE IF EXISTS management;
CREATE DATABASE IF NOT EXISTS management;
USE management;

create table users(
    seq int primary key auto_increment not null,
    user_name varchar(20),
    first_name varchar(20),
    last_name varchar(20),
    email varchar(30),
    password varchar(255),
    system_user bool default 0 NOT NULL,
    finance_pin char(4),
    theme int default 1,
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
    inv_edit            bool default 0 NOT NULL,
    inv_view            bool default 0 NOT NULL,
    doc_edit            bool default 0 NOT NULL,
    doc_view            bool default 0 NOT NULL,
    doc_vote            bool default 0 NOT NULL,
    inv_admin           bool default 0 NOT NULL,
    doc_admin           bool default 0 NOT NULL,
    approve_invoices    bool default 0 NOT NULL,
    receive_emails      bool default 0 NOT NULL,
    user_admin          bool default 0 NOT NULL,
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
    inv_date datetime default current_timestamp,
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
    id varchar(10) not null,
    item_desc varchar(30),
    item_price decimal(8,3),
    item_type enum('debit', 'credit'),
    added_by int not null,
    updated_by int not null,
    effective_start timestamp default current_timestamp,
    effective_end timestamp not null,
    is_active tinyint,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq)
);

create table inv_line(
    line_seq int not null primary key auto_increment,
    inv_seq int not null,
    line_id int not null,
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
    user_seq int not null,
    token varchar(40) not null unique,
    created_at datetime default CURRENT_TIMESTAMP,
    created_by varchar(15),

    constraint foreign key (user_seq) references users (seq)
);

create table docket_status(
    seq int auto_increment primary key,
    stat_desc varchar(20),
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq)
);

create table officer_docket(
    seq int auto_increment primary key,
    created_by int,
    updated_by int,
    title varchar(80),
    body text,
    created_at datetime default current_timestamp,
    updated_at datetime default current_timestamp on update current_timestamp,
    status int,
    CONSTRAINT FOREIGN KEY (created_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (status) references docket_status(seq)
);

create table officer_votes(
    seq int auto_increment primary key,
    user int,
    docket_item int,
    vote_type enum('In Favor', 'Opposed', 'Abstained'),
    CONSTRAINT FOREIGN KEY (user) references users(seq),
    CONSTRAINT FOREIGN KEY (docket_item) references officer_docket(seq)
);

create table docket_assignees(
    seq int auto_increment primary key,
    docket_seq int not null,
    assigned_to int not null,
    CONSTRAINT FOREIGN KEY (assigned_to) references users(seq),
    CONSTRAINT FOREIGN KEY (docket_seq) references officer_docket(seq)
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

create trigger check_user_can_approve
before update on inv_head
for each row
begin
    IF new.approver not in (
            select a.user_seq
            From permissions a  -- CHANGED THE ALIAS TO A
            where (a.approve_invoices = 1 and new.approver = a.user_seq)
        ) THEN -- MISSING THEN
           SIGNAL SQLSTATE '45000'
           SET MESSAGE_TEXT = 'User cannot approve finances';

        END IF;
end;

create trigger check_eff_dates
before update on valid_items
for each row
begin
    if new.effective_start > new.effective_end then
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Effective End must be greater than or equal to Effective End!';
    end if;
end;

CREATE USER IF NOT EXISTS 'invoices'@'localhost' IDENTIFIED WITH mysql_native_password BY 'invoices123!';
GRANT INSERT, UPDATE, SELECT on management.* TO 'invoices'@'localhost';
GRANT DELETE on management.password_reset TO 'invoices'@'localhost';

-- Insert a 'root' system user - No password set! Don't set one plz
INSERT INTO users (seq, user_name, first_name, last_name, email, finance_pin, password, system_user, theme, added_by, updated_by) VALUES
(1, '~', '', '', '', '0000', '', 1, 0, 1, 1);
INSERT INTO permissions (user_seq, inv_edit, inv_view, doc_edit, doc_view, doc_vote, inv_admin, doc_admin, approve_invoices, receive_emails, user_admin, added_by, updated_by) VALUES
(1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1);

-- Insert some typical Statuses and Types
INSERT INTO statuses (stat_desc, added_by, updated_by) VALUES
('Closed', 1, 1),
('Paid', 1, 1),
('Open', 1, 1),
('Granted', 1, 1),
('Pending', 1, 1),
('Denied', 1, 1),
('Cancelled', 1, 1);

INSERT INTO record_types (type_desc, added_by, updated_by) VALUES
('Invoice [Debit]', 1, 1),
('Invoice [Credit]', 1, 1),
('Budget Request', 1, 1);

-- Create an account that can backup the database using mysqldump
create user if not exists invoice_backup_account@localhost
    identified with 'mysql_native_password' by 'LyRk5ASv2hY0';
GRANT INSERT, UPDATE, LOCK TABLES, SELECT, DELETE, PROCESS, TRIGGER, SHOW VIEW on *.* to invoice_backup_account@localhost;
