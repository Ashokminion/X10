package com.workforce.controller;

import com.workforce.entity.Shift;
import com.workforce.service.ShiftService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/shifts")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ShiftController {
    private final ShiftService shiftService;

    @GetMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'HR_MANAGER', 'OPS_MANAGER', 'WORKER')")
    public List<Shift> getAll() {
        return shiftService.getAllShifts();
    }

    @GetMapping("/filter")
    @PreAuthorize("hasAnyRole('ADMIN', 'HR_MANAGER', 'OPS_MANAGER')")
    public List<Shift> getByPeriod(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        return shiftService.getShiftsInPeriod(start, end);
    }

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'OPS_MANAGER')")
    public Shift create(@RequestBody Shift shift) {
        return shiftService.saveShift(shift);
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'OPS_MANAGER')")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        shiftService.deleteShift(id);
        return ResponseEntity.ok().build();
    }
}
