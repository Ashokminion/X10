package com.workforce;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Main application class for AI Workforce Intelligence & Shift Optimization Platform
 * 
 * @author Workforce Intelligence Team
 * @version 1.0.0
 */
@SpringBootApplication
@EnableJpaAuditing
@EnableAsync
@EnableScheduling
public class WorkforceOptimizationApplication {

    public static void main(String[] args) {
        SpringApplication.run(WorkforceOptimizationApplication.class, args);
        System.out.println("==============================================");
        System.out.println("AI Workforce Intelligence Platform Started");
        System.out.println("API Documentation: http://localhost:8080/swagger-ui.html");
        System.out.println("==============================================");
    }
}
