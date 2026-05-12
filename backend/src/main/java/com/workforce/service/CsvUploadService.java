package com.workforce.service;

import com.workforce.entity.Employee;
import lombok.RequiredArgsConstructor;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class CsvUploadService {
    private final EmployeeService employeeService;

    public List<String> processEmployeeCsv(MultipartFile file) {
        List<String> errors = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream()));
                CSVParser csvParser = new CSVParser(reader,
                        CSVFormat.Builder.create().setHeader().setSkipHeaderRecord(true).build())) {

            for (CSVRecord record : csvParser) {
                try {
                    Employee employee = Employee.builder()
                            .code(record.get("code"))
                            .fullName(record.get("full_name"))
                            .email(record.get("email"))
                            .phone(record.get("phone"))
                            .baseSalary(new BigDecimal(record.get("base_salary")))
                            .isActive(true)
                            .build();
                    employeeService.saveEmployee(employee);
                } catch (Exception e) {
                    errors.add("Error at row " + record.getRecordNumber() + ": " + e.getMessage());
                }
            }
        } catch (Exception e) {
            errors.add("Failed to parse CSV: " + e.getMessage());
        }
        return errors;
    }
}
