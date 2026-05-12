package com.workforce.controller;

import com.workforce.service.CsvUploadService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/upload")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class CsvController {
    private final CsvUploadService csvUploadService;

    @PostMapping("/employees")
    @PreAuthorize("hasAnyRole('ADMIN', 'HR_MANAGER')")
    public ResponseEntity<List<String>> uploadEmployees(@RequestParam("file") MultipartFile file) {
        List<String> errors = csvUploadService.processEmployeeCsv(file);
        if (errors.isEmpty()) {
            return ResponseEntity.ok(List.of("CSV processed successfully"));
        } else {
            return ResponseEntity.badRequest().body(errors);
        }
    }
}
