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
    is_active bool default 1 NOT NULL,
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

create table voting_types(
    seq int not null auto_increment primary key,
    type_desc varchar(20),
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq)
);

create table vote_perms(
    seq int auto_increment PRIMARY KEY,
    user_seq INT NOT NULL,
    vote_seq INT NOT NULL,
    granted tinyint NOT NULL default 0,
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (user_seq) references users(seq),
    CONSTRAINT FOREIGN KEY (vote_seq) references voting_types(seq)
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


create table inv_line(
    line_seq int not null primary key auto_increment,
    inv_seq int not null,
    line_id int not null,
    item_desc varchar(30),
    item_price decimal(8,3),
    qty int,
    added_by int not null,
    updated_by int not null,
    dt_added timestamp default current_timestamp,
    dt_updated timestamp default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (inv_seq) references inv_head(seq)
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
    vote_type int not null default 1,
    CONSTRAINT FOREIGN KEY (created_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (status) references docket_status(seq),
    CONSTRAINT FOREIGN KEY (vote_type) references voting_types(seq)
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
    created_by int not null,
    updated_by int not null,
    created_at datetime default current_timestamp,
    updated_at datetime default current_timestamp on update current_timestamp,
    CONSTRAINT FOREIGN KEY (created_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (assigned_to) references users(seq),
    CONSTRAINT FOREIGN KEY (docket_seq) references officer_docket(seq)
);

create table docket_attachments(
    seq int not null auto_increment primary key,
    docket_seq int not null,
    file_name text,
    file_data longblob,
    added_by int not null,
    updated_by int not null,

    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (updated_by) references users(seq),
    CONSTRAINT FOREIGN KEY (docket_seq) references officer_docket(seq)

);

create table docket_conversations (
    seq int not null auto_increment primary key,
    docket_seq int not null,
    docket_text text,
    added_by int not null,
    dt_added timestamp default current_timestamp,
    CONSTRAINT FOREIGN KEY (added_by) references users(seq),
    CONSTRAINT FOREIGN KEY (docket_seq) references officer_docket(seq)
);

create table user_requests (
    seq int not null auto_increment primary key,
    `name` varchar(40),
    email varchar(30),
    reason text,
    dt_added timestamp default current_timestamp
);



-- Insert a 'root' system user - No password set! Don't set one plz
INSERT INTO users (seq, user_name, first_name, last_name, email, finance_pin, password, system_user, theme, added_by, updated_by) VALUES
(1, '~', 'System', 'Account', '', '0000', '', 1, 0, 1, 1);
INSERT INTO permissions (user_seq, inv_edit, inv_view, doc_edit, doc_view, inv_admin, doc_admin, approve_invoices, receive_emails, user_admin, added_by, updated_by) VALUES
(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1);

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

INSERT INTO docket_status (stat_desc, added_by, updated_by) VALUES
('Proposed',        1,1),
('In Debate',       1,1),
('In Vote',         1,1),
('Approved',        1,1),
('Denied',          1,1),
('Tabled',          1,1),
('Need more info',  1,1),
('In Process',      1,1),
('Confirmed',       1,1);


INSERT INTO voting_types (type_desc, added_by, updated_by) VALUES
("Standard Vote", 1, 1),
("Constitution Vote", 1, 1),
("No Vote", 1, 1);
