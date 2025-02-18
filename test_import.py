print("Starting test...")
try:
    from connector_models import ConnectorGenerator
    print("Successfully imported ConnectorGenerator")
except Exception as e:
    print(f"Error importing: {str(e)}")
    import traceback
    traceback.print_exc() 