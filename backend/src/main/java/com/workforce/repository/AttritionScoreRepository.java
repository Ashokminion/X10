package com.workforce.repository;

import com.workforce.entity.AttritionScore;
import com.workforce.enums.RiskLevel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AttritionScoreRepository extends JpaRepository<AttritionScore, Long> {
    List<AttritionScore> findByEmployeeId(Long employeeId);

    List<AttritionScore> findByRiskLevel(RiskLevel riskLevel);

    @Query("SELECT a FROM AttritionScore a WHERE a.employee.id = :empId ORDER BY a.predictionDate DESC LIMIT 1")
    Optional<AttritionScore> findLatestByEmployeeId(@Param("empId") Long employeeId);

    @Query("SELECT a FROM AttritionScore a WHERE a.riskLevel = 'HIGH' ORDER BY a.riskScore DESC")
    List<AttritionScore> findHighRiskEmployees();
}
