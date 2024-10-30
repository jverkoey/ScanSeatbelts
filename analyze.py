from modules.utils import list_files
from modules.analyzer import analyze
from utils import ban


if __name__ == "__main__":
    try:
        ban("ANALYZER")
        datas = list_files()
        ind = int(input("Which data do you want to analyze ?\n> "))
        assert 0 < ind <= len(datas)
        analyze(datas[ind])

    except Exception as e:
        print(f"An error occured: {e}")
        exit(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
