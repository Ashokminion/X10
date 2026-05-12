@echo off
set "BASE_DIR=%~dp0"
set "MVN_PATH=%BASE_DIR%..\tmp_tools\apache-maven-3.9.6\bin\mvn.cmd"
cd /d "%BASE_DIR%"
"%MVN_PATH%" clean package -DskipTests
