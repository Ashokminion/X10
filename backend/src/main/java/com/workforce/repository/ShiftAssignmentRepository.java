package com.workforce.repository;

import com.workforce.entity.ShiftAssignment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ShiftAssignmentRepository extends JpaRepository<ShiftAssignment, Long> {
    List<ShiftAssignment> findByEmployeeId(Long employeeId);

    List<ShiftAssignment> findByShiftId(Long shiftId);
}
