import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math

class AutonVisualizer(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_size = 80  # pixels per grid cell
        self.configure(width=6*self.grid_size, height=6*self.grid_size,
                      bg="#2E2E2E", highlightthickness=0)
        self.start_pos = (3, 3)    # Default start position (grid coordinates)
        self.start_heading = 0     # Default start heading (degrees)
        self.robot_pos = self.start_pos
        self.robot_heading = self.start_heading
        self.objects = []
        self.selected_color = "red"
        self.path = [(self.robot_pos[0] * self.grid_size,
                      self.robot_pos[1] * self.grid_size)]
        self.draw_grid()

    def draw_grid(self):
        self.delete("grid")
        self.delete("start")
        self.delete("robot")
        self.delete("path")
        
        # Draw 6x6 grid lines
        for i in range(8):
            self.create_line(i*self.grid_size, 0, 
                           i*self.grid_size, 6*self.grid_size,
                           fill="#404040", width=2, tags="grid")
            self.create_line(0, i*self.grid_size,
                           6*self.grid_size, i*self.grid_size,
                           fill="#404040", width=2, tags="grid")
        
        # Add vertical center split
        self.create_line(3*self.grid_size, 0,
                       3*self.grid_size, 6*self.grid_size,
                       fill="#FF0000", width=3, dash=(4, 4), tags="grid")
        
        # Redraw objects
        for obj in self.objects:
            x, y, color = obj
            self.create_oval(
                x*self.grid_size - 10, y*self.grid_size - 10,
                x*self.grid_size + 10, y*self.grid_size + 10,
                fill=color, tags="object"
            )
        
        # Draw elements in correct order
        self.draw_start_marker()
        self.draw_path()
        self.draw_robot()

    def set_start_position(self, x, y, heading):
        # Update both position and heading
        self.start_pos = (x, 6 - y)  # Convert Y coordinate
        self.start_heading = heading
        self.robot_pos = self.start_pos
        self.robot_heading = self.start_heading
        self.path = [(self.robot_pos[0] * self.grid_size,
                      self.robot_pos[1] * self.grid_size)]
        self.draw_grid()

    def draw_start_marker(self):
        x = self.start_pos[0] * self.grid_size
        y = self.start_pos[1] * self.grid_size
        self.create_oval(x-12, y-12, x+12, y+12,
                        outline="#00FF00", width=3, tags="start")

    def add_object(self, x, y, color):
        grid_x = x / self.grid_size
        grid_y = y / self.grid_size
        self.objects.append((grid_x, grid_y, color))
        self.draw_grid()

    def update_position(self, distance, angle):
        grid_distance = distance / 24.0  # Convert inches to grid units
        radians = math.radians(self.robot_heading)
        
        # Calculate movement using current heading
        dx = grid_distance * math.cos(radians)
        dy = grid_distance * math.sin(radians)
        
        new_x = self.robot_pos[0] + dx
        new_y = self.robot_pos[1] + dy
        
        pixel_x = new_x * self.grid_size
        pixel_y = new_y * self.grid_size
        
        self.path.append((pixel_x, pixel_y))
        
        self.robot_heading += angle
        self.robot_pos = (new_x, new_y)
        self.draw_grid()

    def draw_path(self):
        if len(self.path) > 1:
            for i in range(1, len(self.path)):
                x1, y1 = self.path[i-1]
                x2, y2 = self.path[i]
                self.create_line(x1, y1, x2, y2, 
                               fill="#00A8FF", width=4, arrow=tk.LAST,
                               arrowshape=(15, 20, 8), tags="path")

    def draw_robot(self):
        x = self.robot_pos[0] * self.grid_size
        y = self.robot_pos[1] * self.grid_size
        
        # Clear previous robot drawing
        self.delete("robot")
        
        # Robot body (rectangle)
        robot_width = 49.5  # Width of the robot
        robot_height = 49.5  # Height of the robot
        
        # Calculate rotated rectangle points
        angle = math.radians(self.robot_heading)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Define the rectangle's corners relative to the center
        corners = [
            (-robot_width / 2, -robot_height / 2),
            (robot_width / 2, -robot_height / 2),
            (robot_width / 2, robot_height / 2),
            (-robot_width / 2, robot_height / 2)
        ]
        
        # Rotate and translate the corners
        rotated_corners = []
        for (cx, cy) in corners:
            rx = cx * cos_a - cy * sin_a + x
            ry = cx * sin_a + cy * cos_a + y
            rotated_corners.extend([rx, ry])
        
        # Draw the rotated rectangle
        self.create_polygon(rotated_corners, 
                            fill="#FF6B6B", outline="#FF5252", width=3, tags="robot")
        
        # Heading arrow (respects current heading)
        arrow_len = 35
        dx = arrow_len * cos_a
        dy = arrow_len * sin_a
        self.create_line(x, y, x + dx, y + dy, 
                        fill="#FFD93D", width=4, arrow=tk.LAST,
                        arrowshape=(10, 15, 6), tags="robot")

    def reset(self):
        self.delete("all")
        self.objects = []
        # Reset to stored start configuration
        self.robot_pos = self.start_pos
        self.robot_heading = self.start_heading
        self.path = [(self.robot_pos[0] * self.grid_size,
                      self.robot_pos[1] * self.grid_size)]
        self.draw_grid()

class AutonGUI:
    def __init__(self, root):
        self.root = root
        root.title("AutoGen PRO - Field Designer")
        root.geometry("1400x900")  # Wider window for side-by-side layout
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.create_main_tab()  # Unified visualization and code tab
        self.create_settings_tab()

    def configure_styles(self):
        self.style.configure(".", background="#333333", foreground="#FFFFFF")
        self.style.configure("TFrame", background="#333333")
        self.style.configure("TLabel", background="#333333", foreground="#FFFFFF",
                           font=("Segoe UI", 10))
        self.style.configure("TButton", background="#4A4A4A", foreground="#FFFFFF",
                           font=("Segoe UI", 10), borderwidth=1)
        self.style.map("TButton",
                      background=[("active", "#5E5E5E"), ("disabled", "#333333")])
        self.style.configure("TEntry", fieldbackground="#4A4A4A", foreground="#FFFFFF",
                           insertcolor="#FFFFFF")
        self.style.configure("TLabelframe", background="#333333", foreground="#FFFFFF")

    def create_main_tab(self):
        main_tab = ttk.Frame(self.notebook)
        
        # Split the main tab into left (visualization) and right (controls)
        main_tab.grid_columnconfigure(0, weight=1)
        main_tab.grid_columnconfigure(1, weight=1)
        main_tab.grid_rowconfigure(0, weight=1)

        # Visualization Panel (Left)
        viz_frame = ttk.Frame(main_tab)
        viz_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.visualizer = AutonVisualizer(viz_frame)
        self.visualizer.pack(fill='both', expand=True)
        self.visualizer.bind("<Button-1>", self.place_object)

        # Controls Panel (Right)
        controls_frame = ttk.Frame(main_tab)
        controls_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Function Name
        name_frame = ttk.Frame(controls_frame)
        name_frame.pack(fill='x', pady=5)
        ttk.Label(name_frame, text="Function Name:").pack(side='left')
        self.fn_name = ttk.Entry(name_frame, width=30)
        self.fn_name.insert(0, "generated_auton")
        self.fn_name.pack(side='left', padx=5)
        
        # Input Area
        input_frame = ttk.LabelFrame(controls_frame, text="Auton Commands")
        input_frame.pack(fill='both', expand=True, pady=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD,
                                                  font=("Consolas", 10), 
                                                  background="#4A4A4A",
                                                  foreground="#FFFFFF")
        self.input_text.pack(fill='both', expand=True)
        
        # Button Row
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill='x', pady=5)
        ttk.Button(button_frame, text="Load Example", command=self.load_example).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Generate Code", command=self.generate_code).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Copy Code", command=self.copy_to_clipboard).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Reset Field", command=self.visualizer.reset).pack(side='right', padx=2)
        
        # Output Area
        output_frame = ttk.LabelFrame(controls_frame, text="Generated Code")
        output_frame.pack(fill='both', expand=True, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD,
                                                   font=("Consolas", 10), 
                                                   background="#4A4A4A",
                                                   foreground="#FFFFFF")
        self.output_text.pack(fill='both', expand=True)
        
        # Status Bar
        self.status = ttk.Label(controls_frame, text="Ready", anchor='w')
        self.status.pack(fill='x', pady=2)
        
        self.notebook.add(main_tab, text="Main Interface")

    def create_settings_tab(self):
        settings_tab = ttk.Frame(self.notebook)
        
        # Color Selection
        color_frame = ttk.LabelFrame(settings_tab, text="Object Colors")
        color_frame.pack(pady=5, fill='x')
        ttk.Button(color_frame, text="Red", command=lambda: self.set_color("red")).pack(side='left', padx=5)
        ttk.Button(color_frame, text="Blue", command=lambda: self.set_color("blue")).pack(side='left', padx=5)
        ttk.Button(color_frame, text="Green", command=lambda: self.set_color("green")).pack(side='left', padx=5)
        
        # Start Position
        pos_frame = ttk.LabelFrame(settings_tab, text="Robot Start Position")
        pos_frame.pack(pady=10, fill='x')
        
        ttk.Label(pos_frame, text="X (0-5.9):").grid(row=0, column=0, padx=5)
        self.start_x = ttk.Entry(pos_frame, width=8)
        self.start_x.insert(0, "3")
        self.start_x.grid(row=0, column=1, padx=5)
        
        ttk.Label(pos_frame, text="Y (0-5.9):").grid(row=0, column=2, padx=5)
        self.start_y = ttk.Entry(pos_frame, width=8)
        self.start_y.insert(0, "3")
        self.start_y.grid(row=0, column=3, padx=5)
        
        ttk.Label(pos_frame, text="Heading (°):").grid(row=0, column=4, padx=5)
        self.start_heading = ttk.Entry(pos_frame, width=8)
        self.start_heading.insert(0, "0")
        self.start_heading.grid(row=0, column=5, padx=5)
        
        ttk.Button(pos_frame, text="Update Start", command=self.update_start_pos).grid(row=0, column=6, padx=10)
        
        self.notebook.add(settings_tab, text="Settings")

    def set_color(self, color):
        self.visualizer.selected_color = color

    def update_start_pos(self):
        try:
            x = float(self.start_x.get())
            y = float(self.start_y.get())
            heading = float(self.start_heading.get())
            if not (0 <= x <= 5.9 and 0 <= y <= 5.9):
                raise ValueError
            self.visualizer.set_start_position(x, y, heading)
            self.status.config(text="Start position updated")
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates! Use X/Y: 0-5.9")

    def place_object(self, event):
        x = event.x
        y = event.y
        self.visualizer.add_object(x, y, self.visualizer.selected_color)
        self.status.config(text=f"Placed {self.visualizer.selected_color} object")

    def load_example(self):
        example = """DRIVE 24 110 1.0
TURN 90 90 2.0
INTAKE 1000 127
DELAY 500
CLAMP OPEN"""
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(tk.END, example)
        self.fn_name.delete(0, tk.END)
        self.fn_name.insert(0, "example_auton")
        self.status.config(text="Example loaded")

    def generate_code(self):
        input_commands = self.input_text.get(1.0, tk.END).strip()
        function_name = self.fn_name.get().strip()
        
        if not function_name:
            messagebox.showwarning("Error", "Please enter a function name!")
            return
            
        if not input_commands:
            messagebox.showwarning("Error", "Please enter commands!")
            return
        
        try:
            if not function_name.isidentifier():
                raise ValueError("Invalid function name - must follow C++ identifier rules")
                
            generated = self.process_commands(input_commands, function_name)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, generated)
            self.status.config(text="Code generated successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Generation failed")

    def process_commands(self, instructions, function_name):
        self.visualizer.reset()
        code = [
            f"void {function_name}() {{",
            "    // Auto-generated code - Verify before use!",
            "    constexpr double GEAR_RATIO = 1.0;",
            "    constexpr int TICKS_PER_REV = 900;",
            ""
        ]
        
        for line in instructions.split('\n'):
            line = line.strip().upper()
            if not line: continue
            
            parts = line.split()
            try:
                if parts[0] == "DRIVE":
                    # Existing DRIVE command handling remains the same
                    dist = float(parts[1])
                    speed = int(parts[2])
                    tol = float(parts[3]) if len(parts) > 3 else 1.0
                    code.append(f"    chassis.pid_drive_set({dist}, {speed}, true);")
                    code.append(f"    chassis.pid_wait_quick_chain();")
                    self.visualizer.update_position(dist, 0)
                    
                elif parts[0] == "TURN":
                    input_angle = float(parts[1])
                    speed = int(parts[2])
                    tol = float(parts[3]) if len(parts) > 3 else 2.0
                    
                    # Calculate absolute angle from start
                    current_heading = self.visualizer.robot_heading
                    absolute_angle = current_heading + input_angle
                    
                    code.append(f"    chassis.pid_turn_set({absolute_angle:.2f}, {speed}, true);")
                    code.append(f"    chassis.pid_wait_quick_chain();")
                    
                    # Update visualizer with relative turn
                    self.visualizer.update_position(0, input_angle)
                    

                elif parts[0] == "INTAKE":
                    duration = int(parts[1])
                    speed = int(parts[2])
                    # code.append(f"     intake_top.move_absolute({duration}, 110);")
                    # code.append(f"     intake_bottom.move_absolute({duration}, 110);")
                    # code.append(f"    pros::delay({duration});")
                    code.append("    intake_top.move(110);")    
                    code.append("    intake_bottom.move(110);") 
                elif parts[0] == "CLAMP":
                    state = parts[1].lower()
                    if state == "open":
                        code.append("    pros::delay(1000);")
                        code.append("    clamp1.set(false);")
                    elif state == "close":
                        code.append("    pros::delay(1000);")
                        code.append("    clamp1.set(true);")
                    else:
                        code.append(f"    // Invalid clamp state: {state}")
                        
                elif parts[0] == "DELAY":
                    duration = int(parts[1])
                    code.append(f"    pros::delay({duration});")
                    
                else:
                    code.append(f"    // Unknown command: {line}")
                    
            except (IndexError, ValueError) as e:
                code.append(f"    // Error processing: {line} - {str(e)}")
        
        code.append("}")
        return '\n'.join(code)

    def copy_to_clipboard(self):
        code = self.output_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        self.status.config(text="Code copied to clipboard")
        messagebox.showinfo("Copied", "Code copied to clipboard!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutonGUI(root)
    root.mainloop()