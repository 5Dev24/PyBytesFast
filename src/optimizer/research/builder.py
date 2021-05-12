from typing import List, Tuple, Dict
from types import FunctionType
import sys

def main() -> None:
	src_code: List[str] = []
	cursor_line: int = 1

	def help_cmd(args: List[str]) -> Tuple[int, List[str]]:
		print("""Commands:
	help                 Displays this list of commands
	addl [line number]   Add a new line before the line number and moves the cursor there
	rml  [line number]   Removes a line
	mvc  [line number]   Moves the cursor to the beginning of a line
	qc   (Quick compile) Compiles the current code and displays any errors
	save [file name]     Saves currently typed code to a file
	clear                Removes all lines
	exit                 Closes the builder""")
		return cursor_line, src_code

	def addl_cmd(args: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing required line number argument")
			return cursor_line, src_code
		try:
			line_number = int(args[0])
			if line_number < 1:
				print("Line number must be greater than 0")
				return cursor_line, src_code
		except ValueError:
			print("Line number must be an integer")
			return cursor_line, src_code

		return line_number, src_code[0:line_number - 1] + [""] + src_code[line_number - 1:]

	def rml_cmd(args: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing required line number argument")
			return cursor_line, src_code
		try:
			line_number = int(args[0])
			if line_number < 1:
				print("Line number must be greater than 0")
				return cursor_line, src_code
		except ValueError:
			print("Line number must be an integer")
			return cursor_line, src_code

		return cursor_line, src_code[0:line_number - 1] + src_code[line_number:]

	def mvc_cmd(args: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing required line number argument")
			return cursor_line, src_code
		try:
			line_number = int(args[0])
			if line_number < 1:
				print("Line number must be greater than 0")
				return cursor_line, src_code
		except ValueError:
			print("Line number must be an integer")
			return cursor_line, src_code
		
		return line_number, src_code

	def qc_cmd(args: List[str]) -> Tuple[int, List[str]]:
		return cursor_line, src_code

	def save_cmd(args: List[str]) -> Tuple[int, List[str]]:
		return cursor_line, src_code

	def clear_cmd(args: List[str]) -> Tuple[int, List[str]]:
		return 1, []

	Commands: Dict[str, FunctionType] = {
		"help": help_cmd,
		"addl": addl_cmd,
		"rml": rml_cmd,
		"mvc": mvc_cmd,
		"qc": qc_cmd,
		"save": save_cmd,
		"clear": clear_cmd,
		"exit": lambda _: sys.exit(0)
	}

	print("Trigger a KeyboardInterrupt to access commands")
	print("Type your code below\n")
	while True:
		try:
			line = input(f"{cursor_line:>03}: ")
		except KeyboardInterrupt:
			try:
				print("\b\b  ") # Remove ^C
				print("Type `help` for a list of commands")
				raw = input().lower()
				cmd = raw.split(" ")[0]
				args = raw.split(" ")[1:]
				
				if cmd in Commands:
					cursor_line, src_code = Commands[cmd](args)

					# Redisplay code
					print("\n")
					for i, code in enumerate(src_code):
						if i + 1 > cursor_line: # Only print up to current line
							break

						print(f"{i + 1:>03}: {code}")
				else:
					print("Unknown command, resuming typing")

				continue
			except KeyboardInterrupt:
				break

		# Add padding
		diff = len(src_code) - cursor_line
		print(diff)
		if diff < 0:
			for _ in range(abs(diff)):
				src_code.append("")

		src_code[cursor_line - 1] = line
		cursor_line += 1

if __name__ == "__main__":
	main()