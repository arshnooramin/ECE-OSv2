DROP TABLE IF EXISTS project;
DROP TABLE IF EXISTS eorder;
DROP TABLE IF EXISTS item;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    auth_level INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES project (id)
);

CREATE TABLE project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    total DECIMAL NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE eorder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    vendor TEXT NOT NULL,
    vendor_url NVARCHAR(255) NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    order_time INTEGER NOT NULL,
    shipping_speed INTEGER NOT NULL,
    status INTEGER NOT NULL DEFAULT 0, 
    item_costs DECIMAL NOT NULL DEFAULT 0,
    courier INTEGER,
    track_url NVARCHAR(255),
    shipping_costs DECIMAL NOT NULL DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES project (id)
);

CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    item_number TEXT NOT NULL,
    price DECIMAL NOT NULL,
    quantity INTEGER NOT NULL,
    justification TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES eorder (id)
);