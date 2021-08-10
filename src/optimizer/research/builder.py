from typing import List, Tuple, Dict
from types import FunctionType
from traceback import print_exception
from os import path, system
from time import sleep
import sys

sys.path.append(path.dirname(path.dirname(path.realpath(__file__))))
import decompiler # Resolves at runtime

saves_path = path.abspath(path.dirname(path.realpath(__file__)) + "/saves/") + "/"

def main() -> None:
	_src_code: List[str] = []
	_cursor_line: int = 1

	def help_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		print("""Commands:
	help                    Displays this list of commands
	addl [line number]      Add a new line before the line number and moves the cursor there
	rml  [line number]      Removes a line
	mvc  [line number]      Moves the cursor to the beginning of a line
	qc   [module/statement] Compiles the current code and displays any errors
	save [file name] [y/n]  Saves currently typed code to a file, second argument sets if the code should be wrapped in a function first
	load [file name]        Loads a saved file
 	decompiled [y/n]        Compiles then decompiles and shows the output, argument sets if the code should be wrapped in a function first
	clear                   Removes all lines
	exit                    Closes the builder

Sleeping for 5 seconds""")
		sleep(5)
		return cursor_line, src_code

	def addl_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing required line number argument")
			sleep(2)
			return cursor_line, src_code
		try:
			line_number = int(args[0])
			if line_number < 1:
				print("Line number must be greater than 0")
				sleep(2)
				return cursor_line, src_code
		except ValueError:
			print("Line number must be an integer")
			sleep(2)
			return cursor_line, src_code

		return line_number, src_code[0:line_number - 1] + [""] + src_code[line_number - 1:]

	def rml_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing required line number argument")
			sleep(2)
			return cursor_line, src_code
		try:
			line_number = int(args[0])
			if line_number < 1:
				print("Line number must be greater than 0")
				sleep(2)
				return cursor_line, src_code
		except ValueError:
			print("Line number must be an integer")
			sleep(2)
			return cursor_line, src_code

		if cursor_line > line_number:
			cursor_line -= 1

		return cursor_line, src_code[0:line_number - 1] + src_code[line_number:]

	def mvc_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing required line number argument")
			sleep(2)
			return cursor_line, src_code
		try:
			if args[0] == "end":
				return len(src_code) + 1, src_code
			elif args[0] == "start":
				return 1, src_code

			line_number = int(args[0])
			if line_number < 1:
				print("Line number must be greater than 0")
				sleep(2)
				return cursor_line, src_code
		except ValueError:
			print("Line number must be an integer")
			sleep(2)
			return cursor_line, src_code
		
		return line_number, src_code

	def qc_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing required type argument must be either `module` or `statement`")
		else:
			if args[0].lower() == "module":
				try:
					compile("\n".join(src_code), "<string>", "exec", dont_inherit = True)
					print("No errors raised")
				except Exception as e:
					print("\nRaised while compiling:")
					print_exception(type(e), e, None, file = sys.stdout, chain=False)
			elif args[0].lower() == "statement":
				try:
					compile("\n".join(src_code), "<string>", "eval", dont_inherit = True)
					print("No errors raised")
				except Exception as e:
					print("\nRaised while compiling:")
					print_exception(type(e), e, None, file = sys.stdout, chain=False)
			else:
				print("Type argument must be either 'module` or `statement`")

		sleep(2)
		return cursor_line, src_code

	def save_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 2:
			if len(args) < 1:
				print("Missing filename argument")
			else:
				print("Missing optimizer setting")
		else:
			filename = saves_path + " ".join(args[:-1])
			if path.exists(filename):
				print("File already exists, override?")
				answer = ""
				while answer not in ("y", "yes", "n", "no", "c", "cancel"):
					answer = input("Override [Y/N]?").lower()
				
				if answer in ("n", "no", "c", "cancel"):
					print("Code wasn't saved")
					sleep(2)
					return cursor_line, src_code

			with open(filename, "w") as file:
				file.write(decompiler.generate_side_by_side(src_code, args[1].lower() in ("yes", "y", "true", "t")))
			print(f"Saved code to {filename}")

		sleep(2)
		return cursor_line, src_code

	def clear_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		return 1, []

	def decompiled_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing optimizer setting")
			sleep(2)
		else:
			system("clear")
			print(decompiler.generate_side_by_side(src_code, args[0].lower() in ("yes", "y", "true", "t")))
			input("Press enter to exit")

		return cursor_line, src_code

	def load_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> Tuple[int, List[str]]:
		if len(args) < 1:
			print("Missing filename argument")
		else:
			filename = saves_path + " ".join(args)
			print(f"Finding \"{filename}\"")
			if path.exists(filename):
				with open(filename, "r") as file:
					lines = []
					for line in file.readlines():
						line = line.split(" # ")[0].rstrip()
						if line:
							lines.append(line)

					return len(lines) + 1, lines
			else:
				print("File doesn't exists")
				sleep(2)

		return cursor_line, src_code

	def exit_cmd(args: List[str], cursor_line: int, src_code: List[str]) -> None:
		system("clear")
		sys.exit(0)

	Commands: Dict[str, FunctionType[Tuple[int, List[str]]]] = {
		"help": help_cmd,
		"addl": addl_cmd,
		"rml": rml_cmd,
		"mvc": mvc_cmd,
		"mvl": mvc_cmd,
		"qc": qc_cmd,
		"save": save_cmd,
		"decompiled": decompiled_cmd,
		"load": load_cmd,
		"clear": clear_cmd,
		"exit": exit_cmd
	}

	print("Trigger a KeyboardInterrupt to access commands")
	print("Type your code below\n")
	while True:
		try:
			system("clear")
			line_number_padding = len(str(_cursor_line))
			for i, code in enumerate(_src_code):
				if i + 1 >= _cursor_line: # Only print up to current line
					break

				print(f"{i + 1:>0{line_number_padding}}:\t{code}")

			line = input(f"{_cursor_line:>0{line_number_padding}}:\t")
		except KeyboardInterrupt:
			try:
				print("\b\b  ") # Remove ^C
				print("Type `help` for a list of commands")
				raw = input(">").lower()
				cmd = raw.split(" ")[0]
				args = raw.split(" ")[1:]
				
				if cmd in Commands:
					_cursor_line, _src_code = Commands[cmd](args, _cursor_line, _src_code)
				else:
					print("Unknown command, resuming typing")
					sleep(2)

				continue
			except KeyboardInterrupt:
				print("\b\b  ")
				break

		# Add padding
		diff = len(_src_code) - _cursor_line
		if diff < 0:
			for _ in range(abs(diff)):
				_src_code.append("")

		_src_code[_cursor_line - 1] = line.expandtabs()
		_cursor_line += 1

if __name__ == "__main__":
	main()