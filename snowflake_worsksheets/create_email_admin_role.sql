--- #### email_admin_role
USE ROLE USERADMIN;
CREATE ROLE IF NOT EXISTS email_admin_role;
USE ROLE SECURITYADMIN;

--- #### GRANTING ROLES
GRANT ROLE email_admin_role TO USER sodahb;
GRANT ROLE email_admin_role TO USER jassef;


--- #### USERS LAYER GRANTS
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE email_admin_role;
GRANT USAGE ON DATABASE apartment_watcher TO ROLE email_admin_role;
GRANT USAGE ON SCHEMA apartment_watcher.USERS TO ROLE email_admin_role;
GRANT CREATE TABLE ON SCHEMA apartment_watcher.USERS TO ROLE email_admin_role;
GRANT SELECT ON ALL TABLES IN SCHEMA apartment_watcher.USERS TO ROLE email_admin_role;
GRANT SELECT ON FUTURE TABLES IN SCHEMA apartment_watcher.USERS TO ROLE email_admin_role;
GRANT TRUNCATE ON ALL TABLES IN SCHEMA apartment_watcher.USERS TO ROLE email_admin_role;
GRANT TRUNCATE ON FUTURE TABLES IN SCHEMA apartment_watcher.USERS TO ROLE email_admin_role;

GRANT SELECT ON ALL VIEWS IN SCHEMA apartment_watcher.USERS TO ROLE email_admin_role;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA apartment_watcher.USERS TO ROLE email_admin_role;

--- #### Testing
USE ROLE email_admin_role;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE apartment_watcher;
CREATE TABLE IF NOT EXISTS USERS.test(
    test INTEGER PRIMARY KEY
);
INSERT INTO USERS.test (test) 
VALUES(2);

SELECT * FROM USERS.test;
DROP TABLE USERS.test;


--- #### SHOW GRANTS

USE ROLE SECURITYADMIN;
SHOW GRANTS TO ROLE email_admin_role;
SHOW GRANTS ON SCHEMA apartment_watcher.USERS;


--- #### Grant reading permissions on warehouse layer

GRANT USAGE ON SCHEMA apartment_watcher.Warehouse TO ROLE email_admin_role;
GRANT SELECT ON ALL TABLES IN SCHEMA apartment_watcher.Warehouse TO ROLE email_admin_role;
GRANT SELECT ON FUTURE TABLES IN SCHEMA apartment_watcher.Warehouse TO ROLE email_admin_role;
GRANT SELECT ON ALL VIEWS IN SCHEMA apartment_watcher.Warehouse TO ROLE email_admin_role;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA apartment_watcher.Warehouse TO ROLE email_admin_role;

--- ### Testing

USE ROLE EMAIL_ADMIN_ROLE;
SHOW VIEWS IN SCHEMA WAREHOUSE;
SELECT * FROM WAREHOUSE.DIM_AD LIMIT 10;


--- #### SHOW GRANTS
USE ROLE SECURITYADMIN;
SHOW GRANTS TO ROLE email_admin_role;
SHOW GRANTS ON SCHEMA apartment_watcher.Warehouse;