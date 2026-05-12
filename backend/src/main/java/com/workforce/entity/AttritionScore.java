package com.workforce.entity;

import com.workforce.enums.RiskLevel;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Attrition Score entity for ML predictions
 */
@Entity
@Table(name = "attrition_scores")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AttritionScore {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "employee_id", nullable = false)
    private Employee employee;

    @Column(name = "prediction_date", nullable = false)
    private LocalDate predictionDate;

    @Column(name = "risk_score", precision = 5, scale = 4, nullable = false)
    private BigDecimal riskScore;

    @Enumerated(EnumType.STRING)
    @Column(name = "risk_level", nullable = false, length = 10)
    private RiskLevel riskLevel;

    @Column(name = "overtime_hours_3m", precision = 8, scale = 2)
    private BigDecimal overtimeHours3m;

    @Column(name = "night_shifts_count_3m")
    private Integer nightShiftsCount3m;

    @Column(name = "performance_score", precision = 5, scale = 2)
    private BigDecimal performanceScore;

    @Column(name = "absenteeism_rate", precision = 5, scale = 2)
    private BigDecimal absenteeismRate;

    @Column(name = "tenure_months")
    private Integer tenureMonths;

    @Column(name = "model_version", length = 50)
    private String modelVersion;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (predictionDate == null) {
            predictionDate = LocalDate.now();
        }
    }
}
