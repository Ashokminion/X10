package com.workforce.service;

import com.workforce.entity.Shift;
import com.workforce.repository.ShiftRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ShiftService {
    private final ShiftRepository shiftRepository;

    public List<Shift> getAllShifts() {
        return shiftRepository.findAll();
    }

    public List<Shift> getShiftsInPeriod(LocalDateTime start, LocalDateTime end) {
        return shiftRepository.findByStartTimeBetween(start, end);
    }

    @Transactional
    public Shift saveShift(Shift shift) {
        return shiftRepository.save(shift);
    }

    @Transactional
    public void deleteShift(Long id) {
        shiftRepository.deleteById(id);
    }
}
