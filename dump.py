
from modules.maestro import wake_up_maestro
from utils import ban


if __name__ == "__main__":
    try:
        ban("DUMPER")
        wake_up_maestro()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
    except Exception as e:
        print("The file has been deleted due to an error: ", e)
        exit(1)
