# Troubleshooting Guide — DVA Platform v2

## Common Issues and Solutions

### Installation Issues

#### Python Version Not Supported

**Error**: `Python 3.12+ required`  
**Cause**: An older Python version is installed.  
**Solution**: Install Python 3.12 or later:
```bash
# Ubuntu/Debian
sudo apt install python3.12

# Check version
python3 --version
```

#### Dependency Installation Fails

**Error**: `pip install` fails with compilation errors  
**Cause**: Missing system build dependencies for native packages.  
**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential

# RHEL/CentOS
sudo dnf install python3-devel gcc

# Retry installation
pip install -r requirements.txt
```

#### Port Already in Use

**Error**: `Port 8080 is already in use`  
**Cause**: Another application is using port 8080.  
**Solution**:
```bash
# Find the process using port 8080
sudo lsof -i :8080

# Change DVA port
export DVA_PORT=8081
python3 -m ui.app
```

### Application Startup Issues

#### Application Won't Start

**Symptoms**: Terminal hangs, no output, or immediate exit.  
**Checklist**:
1. Run dependency checker: `python3 scripts/dependency_checker.py`
2. Run environment validation: `python3 scripts/environment_validation.py`
3. Check Python version: `python3 -c "import sys; print(sys.version)"`
4. Verify NiceGUI is installed: `python3 -c "import nicegui; print(nicegui.__version__)"`
5. Check for port conflicts: `ss -tlnp | grep 8080`

#### Blank Page in Browser

**Symptoms**: Application starts but browser shows blank page.  
**Solutions**:
1. Hard refresh browser (`Ctrl+F5`)
2. Clear browser cache
3. Check browser console for errors (`F12` → Console)
4. Try a different browser
5. Ensure no proxy is interfering with localhost connections

#### Workspace Not Loading

**Symptoms**: Click sidebar item but workspace content doesn't appear.  
**Solutions**:
1. Check terminal for Python errors
2. Verify workspace is registered in `ui/app.py`
3. Check workspace render function for exceptions
4. Run with debug logging: `DVA_LOG_LEVEL=DEBUG python3 -m ui.app`

### Connection Issues

#### Cannot Connect to Local Folder

**Symptoms**: Connection fails when selecting a local folder.  
**Checklist**:
1. Verify the path exists: `ls -la /path/to/folder`
2. Check permissions: `ls -ld /path/to/folder`
3. Ensure the path is not a symlink to an inaccessible location
4. On Windows, use forward slashes or escaped backslashes

#### Cannot Connect to Network Share

**Symptoms**: Network share connection times out or fails.  
**Solutions**:
1. Verify network connectivity: `ping <server>`
2. Check share is accessible: `smbclient -L //server/share`
3. Ensure credentials are correct
4. Check firewall settings
5. On Linux, verify `cifs-utils` or `gvfs` is installed

#### File List Returns Empty

**Symptoms**: Connection succeeds but no files are listed.  
**Solutions**:
1. Verify files exist: `ls -la /path/`
2. Check file extension filters
3. Ensure user has read permission on files
4. Check if directory contains subdirectories only

### Detection Issues

#### Wrong File Type Detected

**Symptoms**: File type detected incorrectly (e.g., delimited instead of fixed-width).  
**Solutions**:
1. Manually override file type in Detection workspace
2. Check file for unusual characters or mixed record types
3. Increase sample size for better detection
4. Verify file encoding is correctly detected

#### Delimiter Detection Wrong

**Symptoms**: Columns not split correctly.  
**Solutions**:
1. Manually specify delimiter in Detection workspace
2. Check if file uses multiple delimiters
3. Verify quote characters are properly handled
4. Check for multiline records that may confuse detection

#### Encoding Issues

**Symptoms**: Garbled text or question marks in preview.  
**Solutions**:
1. Manually select correct encoding in Detection workspace
2. Common encodings: UTF-8, Latin-1 (ISO-8859-1), Windows-1252
3. Use `file` command to check: `file -i /path/to/file`
4. Try opening the file in a text editor that auto-detects encoding

#### Header Not Detected

**Symptoms**: First row treated as data instead of header.  
**Solutions**:
1. Manually mark header in Detection workspace
2. Check if header row has special characters
3. Verify header row doesn't contain data-like values
4. Set header_start_line manually if header is on a specific row

### Canonical Mapping Issues

#### Wrong Column Mapping

**Symptoms**: Columns mapped to incorrect canonical names.  
**Solutions**:
1. Review mapping suggestions in Canonical workspace
2. Manually correct column mappings
3. Create mapping rules for automated correction
4. Check candidate role detection confidence scores

#### Missing Columns After Mapping

**Symptoms**: Fewer columns after canonical transformation.  
**Solutions**:
1. Check ignored columns in CanonicalMetadata
2. Verify all physical columns have mappings
3. Check for unmapped columns log
4. Ensure quantity recommendation is properly applied

#### Quantity Column Not Resolved

**Symptoms**: No quantity column identified.  
**Solutions**:
1. Check if file contains both weighted and unit quantity columns
2. Manually select quantity column
3. Review quantity intelligence recommendations
4. Verify column data types are numeric

### Processing Issues

#### Processing Hangs

**Symptoms**: Processing starts but never completes.  
**Solutions**:
1. Check if file is very large (> 1GB)
2. Reduce chunk size in processing configuration
3. Monitor memory usage in Health workspace
4. Check for infinite loops in custom calculations
5. Restart application and retry with smaller dataset

#### Out of Memory

**Symptoms**: Application crashes during processing of large files.  
**Solutions**:
1. Enable streaming mode in processing configuration
2. Reduce chunk size (try 5,000 instead of 10,000)
3. Disable statistics computation
4. Process file in smaller batches by splitting input
5. Increase system memory or reduce concurrent operations

#### Aggregation Results Incorrect

**Symptoms**: Aggregated values don't match expected results.  
**Solutions**:
1. Verify group columns are correct
2. Check for null values in grouping columns
3. Verify aggregation strategy (sum vs count vs mean)
4. Review source data for duplicates
5. Check calculation expressions for errors

#### Calculation Errors

**Symptoms**: Derived columns show errors or unexpected values.  
**Solutions**:
1. Verify column names in expressions
2. Check for division by zero in ratio calculations
3. Ensure numeric columns have correct data types
4. Review expression syntax against Polars documentation

### Validation Issues

#### Too Many Validation Errors

**Symptoms**: Validation reports excessive errors.  
**Solutions**:
1. Adjust severity thresholds in validation configuration
2. Disable specific validation rules that aren't relevant
3. Check data quality — errors may reflect actual data issues
4. Increase null percentage tolerance for sparse datasets
5. Review range check bounds

#### Validation Misses Known Issues

**Symptoms**: Known data problems not caught by validation.  
**Solutions**:
1. Add custom validation rules
2. Adjust validation rule parameters
3. Check that required columns are specified
4. Verify validation configuration is applied correctly

### Export Issues

#### Excel Export Fails

**Symptoms**: Excel file not generated.  
**Solutions**:
1. Install openpyxl: `pip install openpyxl`
2. Check output directory permissions
3. Reduce the number of export sheets
4. Check for special characters in data that may cause Excel issues
5. Try CSV export instead

#### CSV Export Encoding

**Symptoms**: CSV file has wrong encoding or garbled text.  
**Solutions**:
1. Set explicit UTF-8 encoding for CSV exports
2. Open CSV file with UTF-8 encoding in your editor
3. Check source data encoding

#### Exported Files Empty

**Symptoms**: Export generates files with no data.  
**Solutions**:
1. Verify processing completed successfully
2. Check processing results for data
3. Review execution logs for errors
4. Ensure output configuration includes data

### Performance Issues

#### Application Slow

**Symptoms**: General sluggishness across all operations.  
**Solutions**:
1. Clear cache in Administration workspace
2. Restart application to free memory
3. Reduce number of open projects
4. Check system resource usage
5. Increase system memory if possible

#### Slow File Processing

**Symptoms**: File processing takes longer than expected.  
**Solutions**:
1. Enable streaming mode for large files
2. Increase chunk size for better throughput
3. Disable statistics computation
4. Use Polars-native operations (avoid row-wise operations)
5. Profile with Developer workspace performance metrics

#### High Memory Usage

**Symptoms**: Application consumes excessive memory.  
**Solutions**:
1. Reduce cache size in settings
2. Process smaller datasets
3. Close unused projects and connections
4. Restart application periodically
5. Monitor with Health workspace

### Session and Persistence Issues

#### Session Not Saved

**Symptoms**: Workspace state lost after restart.  
**Solutions**:
1. Check `~/.dva/` directory exists and is writable
2. Verify auto-save is enabled in settings
3. Check permission on `~/.dva/session.json`
4. Run environment validation script

#### Cannot Restore Session

**Symptoms**: Application starts fresh despite previous use.  
**Solutions**:
1. Check `~/.dva/session.json` exists and is valid JSON
2. Run migration: `python3 -c "from ui.shared import persistence; persistence.run_migrations()"`
3. Check for session file corruption
4. Restore from backup if available

### Error Messages

#### "No such file or directory"

**Cause**: File path doesn't exist or connection lost.  
**Solution**: Verify path and reconnect.

#### "Permission denied"

**Cause**: Insufficient file system permissions.  
**Solution**: Check file/directory permissions and user access.

#### "Connection refused"

**Cause**: Cannot connect to data source.  
**Solution**: Verify source is accessible and credentials are correct.

#### "Invalid UTF-8 sequence"

**Cause**: File has non-UTF-8 characters.  
**Solution**: Detect correct encoding or use Latin-1 fallback.

#### "Execution cancelled"

**Cause**: User cancelled operation.  
**Solution**: Re-start execution if needed.

## Getting Additional Help

If you cannot resolve your issue:

1. **Check this guide** for relevant troubleshooting steps
2. **Review application logs** in `~/.dva/logs/dva.log`
3. **Use the Health workspace** for system status
4. **Contact your system administrator** for deployment issues
5. **Report bugs** to the development team with:
   - DVA Platform version
   - Operating system and Python version
   - Steps to reproduce the issue
   - Full error message and stack trace
   - Log files from `~/.dva/logs/`
