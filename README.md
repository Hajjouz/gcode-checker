# G-Code Checker for CNC 3-Axis Machines

Tool for validating, analyzing, and visualizing G-code programs for CNC 3-axis machines. This tool helps machinists, CNC programmers, and operators verify their G-code before running on actual machines, reducing errors and preventing potential crashes.

## 🌟 Features

### ✅ Validation & Analysis
- **Syntax Validation** - Checks G-code command syntax and format
- **Coordinate Validation** - Validates X, Y, Z coordinate values
- **Feed Rate Checking** - Verifies feed rates are within safe limits
- **Travel Range Detection** - Warns if coordinates exceed typical machine limits
- **Program Structure Analysis** - Validates main programs and subprograms
- **Subprogram Auto-Detection** - Automatically finds and analyzes linked subprograms

### 📊 Visualization
- **3D Path Visualization** - Generates visual representation of tool path
- **Multiple View Angles** - Top (XY), Front (XZ), and Side (YZ) views
- **Start/End Markers** - Clearly shows program start and end points
- **High-Resolution Output** - Saves analysis as PNG image (300 DPI)

### 📝 Reporting
- **Detailed Console Report** - Complete analysis printed to terminal
- **Error Detection** - Lists all syntax and logical errors
- **Warning System** - Flags potential issues that may not be critical
- **Statistics Summary** - Command count, travel ranges, program structure

### 🔧 Format Support
- `.nc` - Standard CNC format
- `.txt` - Text-based G-code
- `.gcode` - Generic G-code extension
- `.cnc` - CNC machine format

## 📋 Requirements

- Python 3.6 or higher
- matplotlib library
- numpy library

## 🚀 Installation

1. **Navigate to the directory**

```bash
gitclone https://github.com/Hajjouz/gcode-checker
```

2. **Install dependencies**

```bash
pip install matplotlib numpy
```

Or using requirements file:

```bash
pip install -r requirements.txt
```

## 💡 Usage

### Basic Usage

```bash
python3 gcode.py <gcode_file>
```

### Examples

**Check a single G-code file:**
```bash
python3 gcode.py sample.nc
```

**Check with specific format:**
```bash
python3 gcode.py program.txt
python3 gcode.py machine_code.gcode
python3 gcode.py part_001.cnc
```

### Output

The tool generates two outputs:

1. **Console Report** - Detailed analysis printed to terminal
2. **Visual Report** - PNG image file with 4-panel visualization

**Output filename format:**
```
<input_filename>_analysis.png
```

**Example:**
```
Input:  sample.nc
Output: sample_analysis.png
```

## 📖 Understanding the Output

### Console Report

```
============================================================
G-CODE ANALYSIS REPORT
============================================================
Total Commands Processed: 245

Program Structure:
  Main Programs: O1000
  Subprogram Calls: P2000, P2001

Travel Ranges:
  X: -50.00 to 150.00 mm
  Y: -30.00 to 100.00 mm
  Z: -25.00 to 5.00 mm

Validation Results:
  Errors: 0
  Warnings: 2

WARNINGS:
  ⚠ High feed rate: 5000.0 mm/min
  ⚠ Subprogram P2001 called but not defined

FINAL STATUS: PASS
============================================================
```

### Visual Report

The generated PNG image contains 4 panels:

#### 1. **XY Path (Top View)** - Blue line
- Shows tool path from above
- Green dot = Start position
- Red square = End position

#### 2. **XZ Path (Front View)** - Red line
- Shows depth (Z-axis) changes
- Useful for checking plunge depths

#### 3. **YZ Path (Side View)** - Green line
- Side profile of the machining operation
- Visualizes vertical movements

#### 4. **Statistics Panel**
- Command count
- Program structure info
- Travel range summary
- Error/warning counts
- Pass/Fail status

## 🎯 What Gets Checked

### Syntax Validation

✅ Valid G-code commands (G00, G01, G02, G03, etc.)  
✅ M-code commands (M03, M05, M98, M99, etc.)  
✅ Coordinate formats (X, Y, Z values)  
✅ Feed rate commands (F)  
✅ Spindle speed commands (S)  
✅ Tool commands (T)  
❌ Invalid command formats  
❌ Malformed coordinates  

### Coordinate Validation

✅ X, Y, Z position tracking  
✅ Travel range calculation  
⚠️  Warns if coordinates exceed 1000mm (typical limit)  
⚠️  Detects extreme values  

### Program Structure

✅ Main program detection (O numbers)  
✅ Subprogram calls (M98 P)  
✅ Subprogram definitions  
✅ Program end commands (M30, M02)  
✅ Subprogram returns (M99)  
⚠️  Warns if called subprogram not found  
⚠️  Warns if defined subprogram never called  

### Feed Rate Validation

✅ Feed rate value extraction  
⚠️  Warns if feed rate > 10,000 mm/min  
❌ Error if feed rate ≤ 0  

## 🔍 Auto-Detection of Subprograms

The tool automatically searches for and analyzes subprogram files when it detects a subprogram call (M98 P).

### Supported Naming Conventions

When the main program calls `M98 P2000`, the tool searches for:

```
O2000.txt
O2000.nc
o2000.txt
o2000.nc
2000.txt
2000.nc
```

### Example Structure

```
project_folder/
├── main.nc          (calls M98 P2000 and M98 P2001)
├── O2000.nc         (subprogram 1) ← Auto-detected
└── O2001.nc         (subprogram 2) ← Auto-detected
```

**When you run:**
```bash
python3 gcode.py main.nc
```

**The tool will:**
1. Analyze main.nc
2. Detect M98 P2000 and M98 P2001 calls
3. Search for O2000.nc and O2001.nc
4. Analyze both subprograms automatically
5. Include subprogram errors/warnings in main report

## 📊 Exit Codes

The tool returns appropriate exit codes for automation:

- **0** - PASS (no errors found)
- **1** - FAIL (errors detected or file not found)

**Use in scripts:**
```bash
python3 gcode.py sample.nc
if [ $? -eq 0 ]; then
    echo "G-code validation passed!"
else
    echo "G-code validation failed!"
fi
```

## 🎮 Example G-Code Files

### Simple Circle Program

Create `circle.nc`:
```gcode
O1000
G21 G90 G40
G00 X0 Y0 Z5
G01 Z-5 F100
G02 X0 Y0 I25 J0 F200
G00 Z5
M30
```

**Run check:**
```bash
python3 gcode.py circle.nc
```

### Program with Subprogram

**Main program** `main.nc`:
```gcode
O1000
G21 G90
M98 P2000
G00 X50 Y50
M98 P2000
M30
```

**Subprogram** `O2000.nc`:
```gcode
O2000
G01 X10 Y10 F100
G01 X20 Y10
G01 X20 Y20
G01 X10 Y20
G01 X10 Y10
M99
```

**Run check:**
```bash
python3 gcode.py main.nc
```

The tool will automatically detect and analyze `O2000.nc`!

## ⚙️ Configuration

### Modifying Travel Limits

Edit `gcode.py` to change maximum travel range:

```python
def check_coordinates(self, line):
    max_travel = 1000  # Change this value (in mm)
```

### Modifying Feed Rate Limits

Edit the feed rate warning threshold:

```python
def check_feed_rate(self, line):
    if feed_rate > 10000:  # Change this value (in mm/min)
```

### Adding More File Extensions

Add custom extensions to the supported list:

```python
def __init__(self):
    self.supported_extensions = ['.nc', '.txt', '.gcode', '.cnc', '.tap', '.mpf']
```

## 🐛 Troubleshooting

### Issue: Module not found error

```
ModuleNotFoundError: No module named 'matplotlib'
```

**Solution:**
```bash
pip install matplotlib numpy
```

### Issue: No visualization generated

```
No position data to visualize
```

**Solution:**
- Check if G-code file contains movement commands (G00, G01, G02, G03)
- Verify coordinates are specified (X, Y, Z values)

### Issue: Encoding errors with special characters

**Solution:**
The tool uses `utf-8` encoding with error handling:
```python
with open(filename, 'r', encoding='utf-8', errors='ignore')
```

Files with special characters will be processed, but non-UTF8 characters may be skipped.

### Issue: Subprograms not detected

**Solution:**
- Ensure subprogram files are in the same directory as main program
- Check file naming follows conventions (O2000.nc, O2000.txt, etc.)
- Verify subprogram call uses correct format (M98 P2000)

## 📈 Advanced Usage

### Batch Processing

Create a script to check multiple files:

```bash
#!/bin/bash
for file in *.nc; do
    echo "Checking $file..."
    python3 gcode.py "$file"
    if [ $? -ne 0 ]; then
        echo "❌ $file FAILED"
    else
        echo "✅ $file PASSED"
    fi
done
```

### Integration with CI/CD

Use in GitHub Actions or GitLab CI:

```yaml
- name: Validate G-code
  run: |
    python3 gcode.py program.nc
    if [ $? -ne 0 ]; then
      exit 1
    fi
```

### Python Module Usage

Import and use in your own scripts:

```python
from gcode import GCodeChecker

checker = GCodeChecker()

if checker.analyze_file('sample.nc'):
    checker.create_visualization('output.png')
    checker.print_report()
    
    # Access results programmatically
    print(f"Errors: {len(checker.errors)}")
    print(f"Warnings: {len(checker.warnings)}")
    print(f"Travel X: {min(checker.x_positions)} to {max(checker.x_positions)}")
```

## 🛠️ Supported G-Code Commands

### Motion Commands
- **G00** - Rapid positioning
- **G01** - Linear interpolation
- **G02** - Circular interpolation CW
- **G03** - Circular interpolation CCW

### Machine Commands
- **M03** - Spindle on CW
- **M05** - Spindle off
- **M98** - Subprogram call
- **M99** - Subprogram return
- **M30** - Program end
- **M02** - Program end

### Coordinate Commands
- **X** - X-axis position
- **Y** - Y-axis position
- **Z** - Z-axis position
- **I, J, K** - Arc center offsets
- **R** - Arc radius

### Other Commands
- **F** - Feed rate
- **S** - Spindle speed
- **T** - Tool number
- **N** - Line number
- **O** - Program number

## 🔒 Safety & Best Practices

### Before Running on Machine

1. ✅ Always check G-code with this tool first
2. ✅ Review the visualization carefully
3. ✅ Check all errors and warnings
4. ✅ Verify tool paths make sense
5. ✅ Confirm coordinates within machine limits
6. ✅ Check feed rates are appropriate
7. ✅ Test with dry run on machine
8. ✅ Keep original backups

### What This Tool Cannot Do

❌ **Cannot verify:**
- Tool holder collisions
- Workpiece clamping clearance
- Tool length compensation accuracy
- Actual machine capabilities
- Material-specific feed rates
- Coolant requirements

⚠️ **This tool is a helper, not a replacement for proper CNC programming knowledge and machine testing!**

## 📚 G-Code Resources

### Learning G-Code
- [CNC Cookbook G-Code Tutorial](https://www.cnccookbook.com/g-code-tutorial/)
- [Fusion 360 G-Code Basics](https://www.autodesk.com/products/fusion-360/)
- [Haas Automation Programming Workbook](https://www.haascnc.com/)

### G-Code Standards
- ISO 6983 - CNC Programming Standard
- RS-274D - G-Code Standard

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Support for more G-code dialects (Fanuc, Siemens, Heidenhain)
- 4-axis and 5-axis support
- Tool change validation
- Cycle time estimation
- More advanced collision detection
- Interactive 3D viewer
- Web interface

## 📝 License

This tool is provided as-is for educational and professional use.

## 🆘 Support

If you encounter issues:

1. Check Python version (3.6+)
2. Verify all dependencies installed
3. Test with simple G-code first
4. Check file encoding (UTF-8 recommended)
5. Review error messages carefully

## 📊 Version History

### Version 1.0.0
- Initial release
- Basic syntax validation
- 3-axis path visualization
- Subprogram auto-detection
- Console and image reports
- Multiple file format support

---

**Created for CNC machinists and programmers who value safety and quality! 🔧**

**Always double-check your G-code before running on real machines!**
