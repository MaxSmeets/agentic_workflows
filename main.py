from workflows.my_workflows.test_workflow import every_minute_trigger
import time

def main():
    print("Starting scheduled workflow system")
    
    # Start the trigger
    every_minute_trigger.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping workflow system...")
        every_minute_trigger.stop()
        print("System shutdown complete")

if __name__ == "__main__":
    main()