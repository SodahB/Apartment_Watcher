USE ROLE USER_ADMIN_ROLE;

USE DATABASE APARTMENT_WATCHER;
USE SCHEMA USERS;

-- Create user table
CREATE TABLE IF NOT EXISTS user (
  id INT AUTOINCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  min_rent DECIMAL(10, 2) NOT NULL,
  max_rent DECIMAL(10, 2) NOT NULL,
  min_rooms INT NOT NULL,
  max_rooms INT NOT NULL,
  min_size DECIMAL(10, 2) NOT NULL,
  max_size DECIMAL(10, 2) NOT NULL,
  balcony_required BOOLEAN DEFAULT FALSE NOT NULL,
  any_floor BOOLEAN DEFAULT TRUE NOT NULL,
  any_floor_except_bottom BOOLEAN DEFAULT FALSE NOT NULL,
  elevator_required BOOLEAN DEFAULT FALSE NOT NULL,
  bottom_floor_required BOOLEAN DEFAULT FALSE NOT NULL,
  bottom_or_elevator_required BOOLEAN DEFAULT FALSE NOT NULL,
  is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Create municipality table
CREATE TABLE IF NOT EXISTS municipality (
  id INT AUTOINCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE
);

-- Insert municipalities into table
INSERT INTO municipality (name) 
VALUES 
('Botkyrka'), 
('Danderyd'), 
('Ekero'), 
('Haninge'), 
('Huddinge'), 
('Håbo'), 
('Järfälla'), 
('Lidingö'), 
('Nacka'), 
('Norrtälje'), 
('Nykvarn'), 
('Nynäshamn'), 
('Salem'), 
('Sigtuna'), 
('Sollentuna'), 
('Solna'), 
('Stockholm'), 
('Strängnäs'), 
('Sundbyberg'), 
('Södertälje'), 
('Tyresö'), 
('Täby'), 
('Upplands Väsby'), 
('Upplands-Bro'), 
('Vallentuna'), 
('Värmdö'), 
('Österåker');


-- Create user_municipality table
CREATE TABLE IF NOT EXISTS user_municipality (
  user_id INT,
  municipality_id INT,
  PRIMARY KEY (user_id, municipality_id),
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (municipality_id) REFERENCES municipality(id)
);

-- Create user_apartment_type_filters table
CREATE TABLE IF NOT EXISTS user_apartment_type_filters (
  id INT AUTOINCREMENT PRIMARY KEY,
  user_id INT,
  standard_lease BOOLEAN DEFAULT FALSE NOT NULL,
  youth BOOLEAN DEFAULT FALSE NOT NULL,
  student BOOLEAN DEFAULT FALSE NOT NULL,
  senior BOOLEAN DEFAULT FALSE NOT NULL,
  short_term BOOLEAN DEFAULT FALSE NOT NULL,
  youth_friendship BOOLEAN DEFAULT FALSE NOT NULL,
  fast_track BOOLEAN DEFAULT FALSE NOT NULL,
  limited_mobility BOOLEAN DEFAULT FALSE NOT NULL,
  limited_orientation BOOLEAN DEFAULT FALSE NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(id)
);
