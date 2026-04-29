import argparse
import sys


def calculate(a, op, b):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        if b == 0:
            print("エラー: ゼロ除算はできません", file=sys.stderr)
            sys.exit(1)
        return a / b
    else:
        print(f"エラー: 未対応の演算子 '{op}' (使用可能: +, -, *, /)", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="簡単な電卓CLIツール",
        usage="%(prog)s <num1> <operator> <num2>",
    )
    parser.add_argument("num1", type=float, help="1つ目の数値")
    parser.add_argument("operator", choices=["+", "-", "*", "/"], help="演算子")
    parser.add_argument("num2", type=float, help="2つ目の数値")
    args = parser.parse_args()

    result = calculate(args.num1, args.operator, args.num2)
    print(f"{args.num1} {args.operator} {args.num2} = {result}")


if __name__ == "__main__":
    main()
