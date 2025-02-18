import os
import sys
from connector_models import ConnectorGenerator

def test_connector_segments():
    sys.stdout.write("Starting connector segment tests...\n")
    sys.stdout.flush()
    
    # Create output directory if it doesn't exist
    output_dir = "test_outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        sys.stdout.write(f"Created output directory: {output_dir}\n")
        sys.stdout.flush()
    
    sys.stdout.write("\nInitializing ConnectorGenerator...\n")
    sys.stdout.flush()
    
    try:
        # Initialize connector generator with some test dimensions
        generator = ConnectorGenerator(
            board_width=20,    # 20mm width
            board_thickness=10, # 10mm thickness
            board_depth=30,    # 30mm depth
            add_ribs=True,     # Enable reinforcement ribs
            add_taper=True,    # Enable tapered entries
            add_screw_holes=True  # Enable screw holes
        )
        sys.stdout.write("ConnectorGenerator initialized successfully\n")
        sys.stdout.flush()

        # Test each segment type and save in different formats
        sys.stdout.write("\nTesting segment creation:\n")
        sys.stdout.flush()

        # Test T-junction segment specifically first
        sys.stdout.write("\nTesting T-junction segment...\n")
        sys.stdout.flush()
        try:
            t_junction = generator.create_t_junction_segment()
            filepath = f"{output_dir}/t_junction_segment"
            full_path = generator.save_segment(t_junction, filepath, "step")
            sys.stdout.write(f"✓ T-junction created and saved as: {full_path}\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"✕ Error creating T-junction: {str(e)}\n")
            sys.stderr.flush()
            import traceback
            traceback.print_exc()

        # Test other segments
        for segment_test in [
            ("straight", "create_single_slot_segment", "stl"),
            ("corner", "create_corner_segment", "step"),
            ("cross_junction", "create_cross_junction_segment", "step")
        ]:
            name, method, format = segment_test
            sys.stdout.write(f"\nCreating {name} segment...\n")
            sys.stdout.flush()
            try:
                # Create segment
                segment = getattr(generator, method)()
                sys.stdout.write(f"✓ {name} segment created\n")
                sys.stdout.flush()
                
                # Save segment
                filepath = f"{output_dir}/{name}_segment"
                full_path = generator.save_segment(segment, filepath, format)
                sys.stdout.write(f"✓ Saved as: {full_path}\n")
                sys.stdout.flush()
                
                # Verify file exists
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    sys.stdout.write(f"✓ File verified ({file_size} bytes)\n")
                    sys.stdout.flush()
                else:
                    sys.stderr.write(f"⚠ Warning: File not found at {full_path}\n")
                    sys.stderr.flush()
                    
            except Exception as e:
                sys.stderr.write(f"✕ Error creating {name} segment: {str(e)}\n")
                sys.stderr.flush()
                import traceback
                traceback.print_exc()

        sys.stdout.write("\nTest complete!\n")
        sys.stdout.flush()

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.stderr.flush()
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_connector_segments() 