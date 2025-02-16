import tkinter as tk
from tkinter import ttk, messagebox
from connector_models import ConnectorGenerator
import cadquery as cq
import os
from pathlib import Path

class ConnectorGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connector Generator")
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Board Dimensions Frame
        dims_frame = ttk.LabelFrame(main_frame, text="Board Dimensions", padding="5")
        dims_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Width
        ttk.Label(dims_frame, text="Width (mm):").grid(row=0, column=0, sticky=tk.W)
        self.width_var = tk.StringVar(value="100")
        ttk.Entry(dims_frame, textvariable=self.width_var).grid(row=0, column=1, padx=5)
        
        # Thickness
        ttk.Label(dims_frame, text="Thickness (mm):").grid(row=1, column=0, sticky=tk.W)
        self.thickness_var = tk.StringVar(value="10")
        ttk.Entry(dims_frame, textvariable=self.thickness_var).grid(row=1, column=1, padx=5)
        
        # Depth
        ttk.Label(dims_frame, text="Depth (mm):").grid(row=2, column=0, sticky=tk.W)
        self.depth_var = tk.StringVar(value="50")
        ttk.Entry(dims_frame, textvariable=self.depth_var).grid(row=2, column=1, padx=5)

        # Connector Parameters Frame
        params_frame = ttk.LabelFrame(main_frame, text="Connector Parameters", padding="5")
        params_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Wall thickness
        ttk.Label(params_frame, text="Wall Thickness (mm):").grid(row=0, column=0, sticky=tk.W)
        self.wall_thickness_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.wall_thickness_var).grid(row=0, column=1, padx=5)

        # Tolerance
        ttk.Label(params_frame, text="Tolerance (mm):").grid(row=1, column=0, sticky=tk.W)
        self.tolerance_var = tk.StringVar(value="0.2")
        ttk.Entry(params_frame, textvariable=self.tolerance_var).grid(row=1, column=1, padx=5)

        # Output filename
        ttk.Label(params_frame, text="Output Filename:").grid(row=2, column=0, sticky=tk.W)
        self.filename_var = tk.StringVar(value="connector")
        ttk.Entry(params_frame, textvariable=self.filename_var).grid(row=2, column=1, padx=5)

        # Features Frame
        features_frame = ttk.LabelFrame(main_frame, text="Features", padding="5")
        features_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Taper option
        self.taper_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(features_frame, text="Add entrance taper", 
                       variable=self.taper_var).grid(row=0, column=0, sticky=tk.W)

        # Reinforcement ribs option
        self.ribs_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(features_frame, text="Add reinforcement ribs", 
                       variable=self.ribs_var).grid(row=1, column=0, sticky=tk.W)

        # Screw holes option
        self.screw_holes_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(features_frame, text="Add screw holes (5mm)", 
                       variable=self.screw_holes_var).grid(row=2, column=0, sticky=tk.W)
        
        # Connector Type Frame
        type_frame = ttk.LabelFrame(main_frame, text="Connector Type", padding="5")
        type_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Connector type radio buttons
        self.connector_type = tk.StringVar(value="end_to_end")
        
        ttk.Radiobutton(type_frame, text="End to End", 
                       variable=self.connector_type, 
                       value="end_to_end").grid(row=0, column=0, sticky=tk.W)
        
        ttk.Radiobutton(type_frame, text="Angle", 
                       variable=self.connector_type, 
                       value="angle").grid(row=1, column=0, sticky=tk.W)
        
        ttk.Radiobutton(type_frame, text="T-Connection", 
                       variable=self.connector_type, 
                       value="t_conn").grid(row=2, column=0, sticky=tk.W)
        
        ttk.Radiobutton(type_frame, text="Cross", 
                       variable=self.connector_type, 
                       value="cross").grid(row=3, column=0, sticky=tk.W)
        
        # Angle input (only for angle connector)
        angle_frame = ttk.Frame(type_frame)
        angle_frame.grid(row=1, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(angle_frame, text="Angle:").grid(row=0, column=0, sticky=tk.W)
        self.angle_var = tk.StringVar(value="90")
        ttk.Entry(angle_frame, textvariable=self.angle_var, width=5).grid(row=0, column=1, padx=5)
        ttk.Label(angle_frame, text="degrees").grid(row=0, column=2, sticky=tk.W)
        
        # Update angle frame visibility based on connector type
        def update_angle_visibility(*args):
            if self.connector_type.get() == "angle":
                angle_frame.grid()
            else:
                angle_frame.grid_remove()
        
        self.connector_type.trace_add("write", update_angle_visibility)
        update_angle_visibility()  # Initial state
        
        # Generate Button
        ttk.Button(main_frame, text="Generate Connector", 
                  command=self.generate_connector).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        for child in main_frame.winfo_children():
            child.grid_configure(padx=5, pady=2)
            
    def validate_inputs(self):
        """Validate all numeric inputs"""
        try:
            width = float(self.width_var.get())
            thickness = float(self.thickness_var.get())
            depth = float(self.depth_var.get())
            wall_thickness = float(self.wall_thickness_var.get())
            tolerance = float(self.tolerance_var.get())
            
            if self.connector_type.get() == "angle":
                angle = float(self.angle_var.get())
                if not 0 < angle < 360:
                    raise ValueError("Angle must be between 0 and 360 degrees")
            
            if any(dim <= 0 for dim in [width, thickness, depth, wall_thickness]):
                raise ValueError("Dimensions must be positive numbers")
            
            if tolerance < 0:
                raise ValueError("Tolerance must be positive")
                
            return True
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return False
            
    def generate_connector(self):
        """Generate the connector based on current settings"""
        if not self.validate_inputs():
            return
            
        try:
            # Create generator instance with all parameters
            generator = ConnectorGenerator(
                float(self.width_var.get()),
                float(self.thickness_var.get()),
                float(self.depth_var.get()),
                float(self.wall_thickness_var.get()),
                float(self.tolerance_var.get()),
                self.taper_var.get(),
                self.ribs_var.get(),
                self.screw_holes_var.get()
            )
            
            # Generate the appropriate connector
            connector_type = self.connector_type.get()
            if connector_type == "end_to_end":
                result = generator.create_end_to_end_connector()
            elif connector_type == "angle":
                result = generator.create_angle_connector(float(self.angle_var.get()))
            elif connector_type == "t_conn":
                result = generator.create_t_connector()
            elif connector_type == "cross":
                result = generator.create_cross_connector()
                
            # Get output filename and add connector type
            filename = self.filename_var.get().strip()
            if not filename:
                filename = "connector"  # Default if empty
            
            # Add connector type to filename
            connector_type = self.connector_type.get().lower().replace(" ", "_")
            if not filename.endswith(connector_type):
                filename = f"{filename}_{connector_type}"
            
            # Add extension if needed
            if not filename.endswith(".step"):
                filename += ".step"
            
            # Create output directory if it doesn't exist
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            # Export to STEP file
            output_file = output_dir / filename
            cq.exporters.export(result, str(output_file))
            
            messagebox.showinfo("Success", 
                              f"Connector generated successfully!\nSaved as: {output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate connector: {str(e)}")

def main():
    root = tk.Tk()
    app = ConnectorGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
