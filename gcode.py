#!/usr/bin/env python3
"""
G-Code Checker for CNC 3-Axis
Tool for validating and visualizing G-code with image output
"""

import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import sys
import os

class GCodeChecker:
    def __init__(self):
        self.x_positions = []
        self.y_positions = []
        self.z_positions = []
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.errors = []
        self.warnings = []
        self.commands = []
        self.main_programs = []
        self.subprograms = {}
        self.program_calls = []
        self.supported_extensions = ['.nc', '.txt', '.gcode', '.cnc']

    def parse_coordinate(self, line, axis):
        """Extract coordinate value for given axis (X, Y, Z)"""
        pattern = f'{axis}([+-]?\\d*\\.?\\d+)'
        match = re.search(pattern, line.upper())
        if match:
            return float(match.group(1))
        return None

    def check_syntax(self, line):
        """Check basic G-code syntax"""
        line = line.strip().upper()
        if not line or line.startswith(';') or line.startswith('('):
            return True

        # Check for program structure commands
        self.check_program_structure(line)

        # Check for valid G-code command
        if not re.match(r'^[GM]\d+', line):
            if not re.match(r'^[XYZIJKR]', line) and not line.startswith('F') and not line.startswith('S') and not line.startswith('T') and not line.startswith('N') and not re.match(r'^[OP]\d+', line):
                self.errors.append(f"Invalid command format: {line}")
                return False
        return True

    def check_coordinates(self, line):
        """Validate coordinate values"""
        x = self.parse_coordinate(line, 'X')
        y = self.parse_coordinate(line, 'Y')
        z = self.parse_coordinate(line, 'Z')

        # Update current position
        if x is not None:
            self.current_x = x
        if y is not None:
            self.current_y = y
        if z is not None:
            self.current_z = z

        # Store positions for visualization
        self.x_positions.append(self.current_x)
        self.y_positions.append(self.current_y)
        self.z_positions.append(self.current_z)

        # Check for extreme values
        max_travel = 1000  # mm
        if abs(self.current_x) > max_travel:
            self.warnings.append(f"X coordinate {self.current_x} exceeds typical travel range")
        if abs(self.current_y) > max_travel:
            self.warnings.append(f"Y coordinate {self.current_y} exceeds typical travel range")
        if abs(self.current_z) > max_travel:
            self.warnings.append(f"Z coordinate {self.current_z} exceeds typical travel range")

    def check_program_structure(self, line):
        """Check for main programs and subprograms"""
        line_upper = line.upper().strip()

        # Check for program start (O number or %)
        if re.match(r'^O\d+', line_upper):
            prog_num = re.search(r'O(\d+)', line_upper).group(1)
            if prog_num not in self.main_programs:
                self.main_programs.append(prog_num)

        # Check for subprogram calls (M98 P)
        if 'M98' in line_upper and 'P' in line_upper:
            sub_match = re.search(r'P(\d+)', line_upper)
            if sub_match:
                sub_num = sub_match.group(1)
                self.program_calls.append(sub_num)

        # Check for subprogram definition start
        if re.match(r'^%', line_upper):
            return

        # Check for subprogram end (M99)
        if 'M99' in line_upper:
            return

        # Check for program end (M30, M02)
        if re.match(r'^M(30|02)', line_upper):
            return

    def auto_detect_and_analyze_subprograms(self, main_filename):
        """Automatically detect and analyze subprogram files"""
        main_dir = os.path.dirname(main_filename)
        if not main_dir:
            main_dir = "."

        detected_subprograms = []

        for call in self.program_calls:
            # Try different naming conventions for subprogram files
            possible_names = [
                f"O{call}.txt",
                f"O{call}.nc",
                f"o{call}.txt",
                f"o{call}.nc",
                f"{call}.txt",
                f"{call}.nc"
            ]

            for name in possible_names:
                subprogram_path = os.path.join(main_dir, name)
                if os.path.exists(subprogram_path):
                    print(f"Found subprogram: {subprogram_path}")

                    # Analyze the subprogram
                    sub_checker = GCodeChecker()
                    if sub_checker.analyze_file(subprogram_path):
                        detected_subprograms.append({
                            'file': name,
                            'path': subprogram_path,
                            'errors': len(sub_checker.errors),
                            'warnings': len(sub_checker.warnings),
                            'commands': len(sub_checker.commands)
                        })

                        # Add subprogram errors/warnings to main report
                        for error in sub_checker.errors:
                            self.errors.append(f"Subprogram {name}: {error}")
                        for warning in sub_checker.warnings:
                            self.warnings.append(f"Subprogram {name}: {warning}")

                        # Mark as found
                        if call in self.program_calls:
                            self.main_programs.append(call)

                        print(f"✅ Auto-detected and analyzed subprogram: {name}")
                        print(f"   Commands: {len(sub_checker.commands)}, Errors: {len(sub_checker.errors)}, Warnings: {len(sub_checker.warnings)}")
                    break

        return detected_subprograms

    def validate_program_structure(self):
        """Validate program structure and subprogram calls"""
        # Check if all called subprograms exist
        for call in self.program_calls:
            if call not in self.main_programs:
                self.warnings.append(f"Subprogram P{call} called but not defined")

        # Check for unused subprograms
        for prog in self.main_programs[1:]:  # Skip main program
            if prog not in self.program_calls:
                self.warnings.append(f"Subprogram O{prog} defined but never called")

    def check_file_format(self, filename):
        """Check if file format is supported"""
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in self.supported_extensions:
            self.warnings.append(f"File extension '{file_ext}' may not be standard G-code format")
        return True

    def check_feed_rate(self, line):
        """Check feed rate commands"""
        if 'F' in line.upper():
            feed_match = re.search(r'F(\d*\.?\d+)', line.upper())
            if feed_match:
                feed_rate = float(feed_match.group(1))
                if feed_rate > 10000:  # mm/min
                    self.warnings.append(f"High feed rate: {feed_rate} mm/min")
                elif feed_rate <= 0:
                    self.errors.append(f"Invalid feed rate: {feed_rate}")

    def analyze_file(self, filename):
        """Analyze G-code file"""
        # Check file format
        self.check_file_format(filename)

        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue

                self.commands.append((line_num, line))

                # Check syntax
                self.check_syntax(line)

                # Check coordinates and movement
                if any(axis in line.upper() for axis in ['X', 'Y', 'Z']):
                    self.check_coordinates(line)

                # Check feed rate
                self.check_feed_rate(line)

            # Validate program structure after reading all lines
            self.auto_detect_and_analyze_subprograms(filename)
            self.validate_program_structure()

        except FileNotFoundError:
            self.errors.append(f"File not found: {filename}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False

        return True

    def create_visualization(self, output_filename):
        """Create visualization of G-code path"""
        if not self.x_positions or not self.y_positions:
            print("No position data to visualize")
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('G-Code Analysis Report', fontsize=16, fontweight='bold')

        # XY Plot (Top view)
        ax1.plot(self.x_positions, self.y_positions, 'b-', linewidth=1, alpha=0.7)
        ax1.scatter(self.x_positions[0], self.y_positions[0], color='green', s=100, marker='o', label='Start')
        if len(self.x_positions) > 1:
            ax1.scatter(self.x_positions[-1], self.y_positions[-1], color='red', s=100, marker='s', label='End')
        ax1.set_xlabel('X (mm)')
        ax1.set_ylabel('Y (mm)')
        ax1.set_title('XY Path (Top View)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.axis('equal')

        # XZ Plot (Front view)
        ax2.plot(self.x_positions, self.z_positions, 'r-', linewidth=1, alpha=0.7)
        ax2.scatter(self.x_positions[0], self.z_positions[0], color='green', s=100, marker='o', label='Start')
        if len(self.x_positions) > 1:
            ax2.scatter(self.x_positions[-1], self.z_positions[-1], color='red', s=100, marker='s', label='End')
        ax2.set_xlabel('X (mm)')
        ax2.set_ylabel('Z (mm)')
        ax2.set_title('XZ Path (Front View)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # YZ Plot (Side view)
        ax3.plot(self.y_positions, self.z_positions, 'g-', linewidth=1, alpha=0.7)
        ax3.scatter(self.y_positions[0], self.z_positions[0], color='green', s=100, marker='o', label='Start')
        if len(self.y_positions) > 1:
            ax3.scatter(self.y_positions[-1], self.z_positions[-1], color='red', s=100, marker='s', label='End')
        ax3.set_xlabel('Y (mm)')
        ax3.set_ylabel('Z (mm)')
        ax3.set_title('YZ Path (Side View)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # Statistics and Errors
        ax4.axis('off')
        stats_text = f"""G-Code Analysis Summary:

Total Commands: {len(self.commands)}
Main Programs: {len(self.main_programs)}
Subprogram Calls: {len(self.program_calls)}

Travel Range:
  X: {min(self.x_positions):.2f} to {max(self.x_positions):.2f} mm
  Y: {min(self.y_positions):.2f} to {max(self.y_positions):.2f} mm
  Z: {min(self.z_positions):.2f} to {max(self.z_positions):.2f} mm

Errors: {len(self.errors)}
Warnings: {len(self.warnings)}

Status: {'✓ PASS' if len(self.errors) == 0 else '✗ FAIL'}
"""

        ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

        if self.errors:
            error_text = "ERRORS:\n" + "\n".join([f"• {error}" for error in self.errors[:5]])
            if len(self.errors) > 5:
                error_text += f"\n... and {len(self.errors) - 5} more errors"
            ax4.text(0.05, 0.45, error_text, transform=ax4.transAxes, fontsize=9,
                    verticalalignment='top', fontfamily='monospace', color='red',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="mistyrose", alpha=0.8))

        if self.warnings:
            warning_text = "WARNINGS:\n" + "\n".join([f"• {warning}" for warning in self.warnings[:3]])
            if len(self.warnings) > 3:
                warning_text += f"\n... and {len(self.warnings) - 3} more warnings"
            ax4.text(0.05, 0.15, warning_text, transform=ax4.transAxes, fontsize=9,
                    verticalalignment='top', fontfamily='monospace', color='orange',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))

        plt.tight_layout()
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Visualization saved as: {output_filename}")

    def print_report(self):
        """Print analysis report to console"""
        print("\n" + "="*60)
        print("G-CODE ANALYSIS REPORT")
        print("="*60)

        print(f"Total Commands Processed: {len(self.commands)}")

        if self.main_programs:
            print(f"\nProgram Structure:")
            print(f"  Main Programs: {', '.join(['O' + p for p in self.main_programs])}")
            if self.program_calls:
                print(f"  Subprogram Calls: {', '.join(['P' + p for p in self.program_calls])}")

        if self.x_positions:
            print(f"\nTravel Ranges:")
            print(f"  X: {min(self.x_positions):.2f} to {max(self.x_positions):.2f} mm")
            print(f"  Y: {min(self.y_positions):.2f} to {max(self.y_positions):.2f} mm")
            print(f"  Z: {min(self.z_positions):.2f} to {max(self.z_positions):.2f} mm")

        print(f"\nValidation Results:")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if self.errors:
            print(f"\nERRORS:")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print(f"\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")

        status = "PASS" if len(self.errors) == 0 else "FAIL"
        print(f"\nFINAL STATUS: {status}")
        print("="*60)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 gcode_checker.py <gcode_file>")
        print("Example: python3 gcode_checker.py sample.nc")
        print("Supported formats: .nc, .txt, .gcode, .cnc")
        sys.exit(1)

    gcode_file = sys.argv[1]
    if not os.path.exists(gcode_file):
        print(f"Error: File '{gcode_file}' not found")
        sys.exit(1)

    checker = GCodeChecker()

    print(f"Analyzing G-code file: {gcode_file}")

    if checker.analyze_file(gcode_file):
        # Generate output filename
        base_name = os.path.splitext(gcode_file)[0]
        output_image = f"{base_name}_analysis.png"

        # Create visualization
        checker.create_visualization(output_image)

        # Print report
        checker.print_report()

        # Exit with appropriate code
        sys.exit(0 if len(checker.errors) == 0 else 1)
    else:
        print("Failed to analyze G-code file")
        sys.exit(1)

if __name__ == "__main__":
    main()
