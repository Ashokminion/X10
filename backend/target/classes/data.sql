INSERT INTO roles (name, description) VALUES
('ADMIN', 'System administrator with full access'),
('HR_MANAGER', 'HR manager with employee and shift management access'),
('OPERATIONS_MANAGER', 'Operations manager with shift and analytics access'),
('WORKER', 'Worker with limited read-only access');

INSERT INTO users (username, email, password_hash, role_id) VALUES
('admin', 'admin@workforce.com', '$2a$10$N9qo8uLOicKfgNmF1K9cA.J3OJHxXdP8zQQ3vY2G5R4LAzHa5Mjeu', 1);

INSERT INTO departments (name, description, budget) VALUES
('Manufacturing', 'Production and assembly operations', 500000.00),
('Healthcare', 'Nursing and patient care', 750000.00),
('Warehouse', 'Storage and logistics', 300000.00),
('Quality Control', 'Quality assurance and testing', 200000.00),
('Maintenance', 'Equipment maintenance and repair', 150000.00);

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
