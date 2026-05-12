package com.workforce.config;

import com.workforce.entity.Role;
import com.workforce.entity.User;
import com.workforce.repository.RoleRepository;
import com.workforce.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Seeds initial data (roles, admin user) on startup if not already present.
 */
@Component
public class DataSeeder implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DataSeeder.class);

    @Autowired
    private RoleRepository roleRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        seedRoles();
        seedAdminUser();
    }

    private void seedRoles() {
        if (roleRepository.count() == 0) {
            roleRepository
                    .save(Role.builder().name("ADMIN").description("System administrator with full access").build());
            roleRepository.save(Role.builder().name("HR_MANAGER")
                    .description("HR manager with employee and shift management access").build());
            roleRepository.save(Role.builder().name("OPERATIONS_MANAGER")
                    .description("Operations manager with shift and analytics access").build());
            roleRepository
                    .save(Role.builder().name("WORKER").description("Worker with limited read-only access").build());
            logger.info("Default roles seeded.");
        }
    }

    private void seedAdminUser() {
        java.util.Optional<User> adminOpt = userRepository.findByUsername("admin");
        if (adminOpt.isEmpty()) {
            Role adminRole = roleRepository.findByName("ADMIN")
                    .orElseThrow(() -> new RuntimeException("ADMIN role not found"));

            User admin = User.builder()
                    .username("admin")
                    .email("admin@workforce.com")
                    .passwordHash(passwordEncoder.encode("admin123"))
                    .role(adminRole)
                    .isActive(true)
                    .build();

            userRepository.save(admin);
            logger.info("Default admin user created. Username: admin, Password: admin123");
        } else {
            User admin = adminOpt.get();
            admin.setUsername("admin");
            admin.setPasswordHash(passwordEncoder.encode("admin123"));
            userRepository.save(admin);
            logger.info("Admin user already exists. Password reset to default admin123.");
        }
    }
}
