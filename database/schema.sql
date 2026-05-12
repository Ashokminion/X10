-- =====================================================
-- AI Workforce Intelligence & Shift Optimization Platform
-- MySQL Database Schema
-- =====================================================

-- Drop existing database if exists
DROP DATABASE IF EXISTS workforce_optimization;
CREATE DATABASE workforce_optimization CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE workforce_optimization;

-- =====================================================
-- 1. ROLES TABLE
-- =====================================================
CREATE TABLE roles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_role_name (name)
) ENGINE=InnoDB;

-- =====================================================
-- 2. USERS TABLE (Authentication)
-- =====================================================
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id BIGINT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role_id)
) ENGINE=InnoDB;

-- =====================================================
-- 3. DEPARTMENTS TABLE
-- =====================================================
CREATE TABLE departments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    manager_id BIGINT,
    budget DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dept_name (name)
) ENGINE=InnoDB;

-- =====================================================
-- 4. SKILLS TABLE
-- =====================================================
CREATE TABLE skills (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_skill_name (name),
    INDEX idx_skill_category (category)
) ENGINE=InnoDB;

-- =====================================================
-- 5. EMPLOYEES TABLE
-- =====================================================
CREATE TABLE employees (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNIQUE,
    employee_code VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department_id BIGINT NOT NULL,
    position VARCHAR(100),
    hourly_wage DECIMAL(10, 2) NOT NULL,
    base_salary DECIMAL(12, 2) NOT NULL,
    overtime_rate DECIMAL(5, 2) DEFAULT 1.5,
    night_shift_allowance DECIMAL(8, 2) DEFAULT 0,
    date_of_joining DATE NOT NULL,
    tenure_months INT GENERATED ALWAYS AS (TIMESTAMPDIFF(MONTH, date_of_joining, CURDATE())) STORED,
    is_available BOOLEAN DEFAULT TRUE,
    max_weekly_hours INT DEFAULT 48,
    preferred_shift_type ENUM('MORNING', 'AFTERNOON', 'NIGHT', 'ANY') DEFAULT 'ANY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
    INDEX idx_employee_code (employee_code),
    INDEX idx_email (email),
    INDEX idx_department (department_id),
    INDEX idx_availability (is_available),
    INDEX idx_date_joining (date_of_joining)
) ENGINE=InnoDB;

-- Add foreign key to departments for manager
ALTER TABLE departments 
ADD FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL;

-- =====================================================
-- 6. EMPLOYEE_SKILLS (Many-to-Many)
-- =====================================================
CREATE TABLE employee_skills (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    proficiency_level ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT') DEFAULT 'INTERMEDIATE',
    years_of_experience DECIMAL(4, 1),
    certified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_skill (employee_id, skill_id),
    INDEX idx_employee (employee_id),
    INDEX idx_skill (skill_id),
    INDEX idx_proficiency (proficiency_level)
) ENGINE=InnoDB;

-- =====================================================
-- 7. SHIFTS TABLE
-- =====================================================
CREATE TABLE shifts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    shift_code VARCHAR(50) NOT NULL UNIQUE,
    shift_name VARCHAR(100) NOT NULL,
    shift_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    shift_type ENUM('MORNING', 'AFTERNOON', 'NIGHT') NOT NULL,
    required_workers INT NOT NULL DEFAULT 1,
    required_skill_id BIGINT,
    department_id BIGINT,
    hourly_rate DECIMAL(10, 2),
    status ENUM('PLANNED', 'OPTIMIZED', 'CONFIRMED', 'COMPLETED', 'CANCELLED') DEFAULT 'PLANNED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (required_skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    INDEX idx_shift_date (shift_date),
    INDEX idx_shift_type (shift_type),
    INDEX idx_status (status),
    INDEX idx_department (department_id),
    INDEX idx_date_range (shift_date, start_time, end_time)
) ENGINE=InnoDB;

-- =====================================================
-- 8. SHIFT_ASSIGNMENTS TABLE
-- =====================================================
CREATE TABLE shift_assignments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    shift_id BIGINT NOT NULL,
    assignment_type ENUM('OPTIMIZED', 'MANUAL', 'OVERRIDE') DEFAULT 'OPTIMIZED',
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_hours DECIMAL(5, 2),
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    status ENUM('ASSIGNED', 'CONFIRMED', 'COMPLETED', 'ABSENT', 'CANCELLED') DEFAULT 'ASSIGNED',
    notes TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_shift (employee_id, shift_id),
    INDEX idx_employee (employee_id),
    INDEX idx_shift (shift_id),
    INDEX idx_status (status),
    INDEX idx_assignment_date (assignment_date)
) ENGINE=InnoDB;

-- =====================================================
-- 9. STOCK_LEVELS TABLE
-- =====================================================
CREATE TABLE stock_levels (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    current_stock INT NOT NULL,
    target_stock INT NOT NULL,
    production_demand INT DEFAULT 0,
    required_workforce_count INT GENERATED ALWAYS AS (CEIL(production_demand / 100.0)) STORED,
    department_id BIGINT,
    recorded_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    INDEX idx_product (product_name),
    INDEX idx_date (recorded_date),
    INDEX idx_department (department_id)
) ENGINE=InnoDB;

-- =====================================================
-- 10. MEDICAL_LEAVES TABLE
-- =====================================================
CREATE TABLE medical_leaves (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    leave_type ENUM('SICK_LEAVE', 'EMERGENCY', 'MEDICAL', 'MATERNITY', 'PATERNITY') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count INT GENERATED ALWAYS AS (DATEDIFF(end_date, start_date) + 1) STORED,
    reason TEXT,
    medical_certificate VARCHAR(255),
    status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
    approved_by BIGINT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_employee (employee_id),
    INDEX idx_date_range (start_date, end_date),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- =====================================================
-- 11. PERFORMANCE_REVIEWS TABLE
-- =====================================================
CREATE TABLE performance_reviews (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    performance_score DECIMAL(5, 2) NOT NULL CHECK (performance_score BETWEEN 0 AND 100),
    productivity_rating ENUM('POOR', 'BELOW_AVERAGE', 'AVERAGE', 'GOOD', 'EXCELLENT') DEFAULT 'AVERAGE',
    attendance_rate DECIMAL(5, 2),
    quality_score DECIMAL(5, 2),
    reviewer_id BIGINT,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_employee (employee_id),
    INDEX idx_review_period (review_period_start, review_period_end),
    INDEX idx_performance_score (performance_score)
) ENGINE=InnoDB;

-- =====================================================
-- 12. SALARY_RECORDS TABLE
-- =====================================================
CREATE TABLE salary_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    base_salary DECIMAL(12, 2) NOT NULL,
    regular_hours DECIMAL(8, 2) DEFAULT 0,
    overtime_hours DECIMAL(8, 2) DEFAULT 0,
    overtime_pay DECIMAL(10, 2) DEFAULT 0,
    night_shifts_count INT DEFAULT 0,
    night_shift_allowance DECIMAL(8, 2) DEFAULT 0,
    gross_salary DECIMAL(12, 2) NOT NULL,
    deductions DECIMAL(10, 2) DEFAULT 0,
    net_salary DECIMAL(12, 2) NOT NULL,
    payment_status ENUM('PENDING', 'PROCESSED', 'PAID') DEFAULT 'PENDING',
    payment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    INDEX idx_employee (employee_id),
    INDEX idx_pay_period (pay_period_start, pay_period_end),
    INDEX idx_payment_status (payment_status)
) ENGINE=InnoDB;

-- =====================================================
-- 13. ATTRITION_SCORES TABLE
-- =====================================================
CREATE TABLE attrition_scores (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    prediction_date DATE NOT NULL,
    risk_score DECIMAL(5, 4) NOT NULL CHECK (risk_score BETWEEN 0 AND 1),
    risk_level ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL,
    overtime_hours_3m DECIMAL(8, 2),
    night_shifts_count_3m INT,
    performance_score DECIMAL(5, 2),
    absenteeism_rate DECIMAL(5, 2),
    tenure_months INT,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    INDEX idx_employee (employee_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_prediction_date (prediction_date),
    INDEX idx_risk_score (risk_score DESC)
) ENGINE=InnoDB;

-- =====================================================
-- 14. CHAT_HISTORY TABLE
-- =====================================================
CREATE TABLE chat_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    message_type ENUM('USER', 'BOT') NOT NULL,
    message_text TEXT NOT NULL,
    intent_detected VARCHAR(100),
    response_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_intent (intent_detected)
) ENGINE=InnoDB;

-- =====================================================
-- INITIAL DATA POPULATION
-- =====================================================

-- Insert default roles
INSERT INTO roles (name, description) VALUES
('ADMIN', 'System administrator with full access'),
('HR_MANAGER', 'HR manager with employee and shift management access'),
('OPERATIONS_MANAGER', 'Operations manager with shift and analytics access'),
('WORKER', 'Worker with limited read-only access');

-- Insert default admin user (password: admin123 - hashed with BCrypt)
INSERT INTO users (username, email, password_hash, role_id) VALUES
('admin', 'admin@workforce.com', '$2a$10$N9qo8uLOicKfgNmF1K9cA.J3OJHxXdP8zQQ3vY2G5R4LAzHa5Mjeu', 1);

-- Insert default departments
INSERT INTO departments (name, description, budget) VALUES
('Manufacturing', 'Production and assembly operations', 500000.00),
('Healthcare', 'Nursing and patient care', 750000.00),
('Warehouse', 'Storage and logistics', 300000.00),
('Quality Control', 'Quality assurance and testing', 200000.00),
('Maintenance', 'Equipment maintenance and repair', 150000.00);

-- Insert default skills
INSERT INTO skills (name, category, description) VALUES
('Forklift Operation', 'Warehouse', 'Licensed forklift operator'),
('Nursing', 'Healthcare', 'Registered nurse certification'),
('Assembly', 'Manufacturing', 'Product assembly skills'),
('Quality Inspection', 'Quality Control', 'Product quality inspection'),
('Welding', 'Manufacturing', 'Metal welding certification'),
('Patient Care', 'Healthcare', 'Patient care and assistance'),
('Inventory Management', 'Warehouse', 'Stock tracking and management'),
('Machine Operation', 'Manufacturing', 'Industrial machine operation'),
('First Aid', 'Healthcare', 'Basic first aid certification'),
('Heavy Machinery', 'Maintenance', 'Heavy equipment operation and repair');

-- =====================================================
-- VIEWS FOR ANALYTICS
-- =====================================================

-- View: High Attrition Risk Employees
CREATE VIEW v_high_risk_employees AS
SELECT 
    e.id,
    e.employee_code,
    CONCAT(e.first_name, ' ', e.last_name) AS full_name,
    e.email,
    d.name AS department,
    a.risk_score,
    a.risk_level,
    a.prediction_date
FROM employees e
JOIN attrition_scores a ON e.id = a.employee_id
JOIN departments d ON e.department_id = d.id
WHERE a.risk_level = 'HIGH'
  AND a.prediction_date = (
      SELECT MAX(prediction_date) 
      FROM attrition_scores 
      WHERE employee_id = e.id
  );

-- View: Overtime Analysis
CREATE VIEW v_overtime_analysis AS
SELECT 
    e.id AS employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    d.name AS department,
    SUM(sr.overtime_hours) AS total_overtime_hours,
    SUM(sr.overtime_pay) AS total_overtime_pay,
    COUNT(DISTINCT sr.id) AS pay_periods_count
FROM employees e
JOIN salary_records sr ON e.id = sr.employee_id
JOIN departments d ON e.department_id = d.id
WHERE sr.pay_period_start >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY e.id, d.name
ORDER BY total_overtime_hours DESC;

-- View: Department Performance
CREATE VIEW v_department_performance AS
SELECT 
    d.id AS department_id,
    d.name AS department_name,
    COUNT(DISTINCT e.id) AS employee_count,
    AVG(pr.performance_score) AS avg_performance_score,
    AVG(pr.attendance_rate) AS avg_attendance_rate,
    COUNT(DISTINCT ml.id) AS total_medical_leaves
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
LEFT JOIN performance_reviews pr ON e.id = pr.employee_id
LEFT JOIN medical_leaves ml ON e.id = ml.employee_id
WHERE pr.review_period_end >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY d.id, d.name;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

DELIMITER $$

-- Procedure: Calculate Payroll
CREATE PROCEDURE sp_calculate_payroll(
    IN p_employee_id BIGINT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    DECLARE v_base_salary DECIMAL(12, 2);
    DECLARE v_hourly_wage DECIMAL(10, 2);
    DECLARE v_overtime_rate DECIMAL(5, 2);
    DECLARE v_night_allowance DECIMAL(8, 2);
    DECLARE v_regular_hours DECIMAL(8, 2);
    DECLARE v_overtime_hours DECIMAL(8, 2);
    DECLARE v_night_shifts INT;
    DECLARE v_overtime_pay DECIMAL(10, 2);
    DECLARE v_night_pay DECIMAL(8, 2);
    DECLARE v_gross_salary DECIMAL(12, 2);
    DECLARE v_deductions DECIMAL(10, 2);
    DECLARE v_net_salary DECIMAL(12, 2);
    
    -- Get employee details
    SELECT base_salary, hourly_wage, overtime_rate, night_shift_allowance
    INTO v_base_salary, v_hourly_wage, v_overtime_rate, v_night_allowance
    FROM employees
    WHERE id = p_employee_id;
    
    -- Calculate hours worked
    SELECT 
        SUM(CASE WHEN sa.duration_hours <= 40 THEN sa.duration_hours ELSE 40 END),
        SUM(CASE WHEN sa.duration_hours > 40 THEN sa.duration_hours - 40 ELSE 0 END),
        COUNT(CASE WHEN s.shift_type = 'NIGHT' THEN 1 END)
    INTO v_regular_hours, v_overtime_hours, v_night_shifts
    FROM shift_assignments sa
    JOIN shifts s ON sa.shift_id = s.id
    WHERE sa.employee_id = p_employee_id
      AND s.shift_date BETWEEN p_start_date AND p_end_date
      AND sa.status = 'COMPLETED';
    
    -- Calculate pay components
    SET v_overtime_pay = v_overtime_hours * v_hourly_wage * v_overtime_rate;
    SET v_night_pay = v_night_shifts * v_night_allowance;
    SET v_gross_salary = v_base_salary + v_overtime_pay + v_night_pay;
    SET v_deductions = v_gross_salary * 0.10; -- 10% tax
    SET v_net_salary = v_gross_salary - v_deductions;
    
    -- Insert salary record
    INSERT INTO salary_records (
        employee_id, pay_period_start, pay_period_end,
        base_salary, regular_hours, overtime_hours,
        overtime_pay, night_shifts_count, night_shift_allowance,
        gross_salary, deductions, net_salary, payment_status
    ) VALUES (
        p_employee_id, p_start_date, p_end_date,
        v_base_salary, COALESCE(v_regular_hours, 0), COALESCE(v_overtime_hours, 0),
        COALESCE(v_overtime_pay, 0), COALESCE(v_night_shifts, 0), COALESCE(v_night_pay, 0),
        v_gross_salary, v_deductions, v_net_salary, 'PENDING'
    );
    
    SELECT 'Payroll calculated successfully' AS message, v_net_salary AS net_salary;
END$$

DELIMITER ;

-- =====================================================
-- TRIGGERS
-- =====================================================

DELIMITER $$

-- Trigger: Update shift assignment duration
CREATE TRIGGER trg_calculate_shift_duration
BEFORE INSERT ON shift_assignments
FOR EACH ROW
BEGIN
    DECLARE v_start_time TIME;
    DECLARE v_end_time TIME;
    
    SELECT start_time, end_time
    INTO v_start_time, v_end_time
    FROM shifts
    WHERE id = NEW.shift_id;
    
    SET NEW.duration_hours = TIMESTAMPDIFF(HOUR, v_start_time, v_end_time);
END$$

DELIMITER ;

-- =====================================================
-- INDEXING OPTIMIZATION
-- =====================================================

-- Composite indexes for common queries
CREATE INDEX idx_employee_dept_available ON employees(department_id, is_available);
CREATE INDEX idx_shift_date_type ON shifts(shift_date, shift_type, status);
CREATE INDEX idx_assignment_employee_date ON shift_assignments(employee_id, assignment_date);

-- =====================================================
-- SCHEMA COMPLETE
-- =====================================================
