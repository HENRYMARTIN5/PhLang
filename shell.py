import phlang.core as core
import sys


def main():
	try:
		if sys.argv[1]:
			with open(sys.argv[1], "r") as f:
				text = f.read() 
			core.run(sys.argv[1], text)
	except:
		try:
			while True:
				text = input('phlang > ')
				if text.strip() == "": continue
				result, error = core.run('<stdin>', text)

				if error:
					print(error.as_string())
				elif result:
					if len(result.elements) == 1:
						print(repr(result.elements[0]))
					else:
						print(repr(result))
		except Exception as e:
			print("Uncaught exception:", e)
			main()

if __name__ == "__main__":
	main()