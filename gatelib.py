import sys
import os
from os import path, mkdir, listdir, rmdir

##############
# USER INPUT #
##############

"""
	Asks the user a question and returns the number of the response. If an invalid answer is given, the question is repeated.

	Parameters
	----------
	question : str
		The question that is asked.
	choices : list (str)
		An array of the different possible answers.
	allowMultiple : bool
		If True, the user may give multiple answers, each separated by a space. An array of these answers is returned.

	Returns
	-------
	If allowMultiple is True:
	int
		The chosen answer.
	Else:
	list (int)
		An array of ints representing chosen answers.
"""
def makeChoice(question, choices, allowMultiple=False):
	numChoices = len(choices)
	if numChoices == 0:
		print("Warning: A question was asked with no valid answers. Returning None.")
		return None
	if numChoices == 1:
		print("A question was asked with only one valid answer. Returning this answer.")
		return 1
	print("\n"+question)
	for i in range(numChoices):
		print(str(i+1)+": "+choices[i])
	cInput = input("\n").split(" ")
	if not allowMultiple:
		try:
			assert len(cInput) == 1
			choice = int(cInput[0])
			assert choice > 0 and choice <= numChoices
			return choice
		except:
			print("Invalid input.")
			return makeChoice(question, choices, allowMultiple)
	else:
		try:
			choices = [int(c) for c in cInput]
			for choice in choices:
				assert choice > 0 and choice <= numChoices
			return choices
		except:
			print("Invalid input.")
			return makeChoice(question, choices, allowMultiple)

"""
	Asks the user a question. The answer can be any number between the given minVal and maxVal. If an invalid answer is given, the question is repeated.

	Parameters
	----------
	question : str
		The question that is asked.
	minVal : float
		The minimum allowed value.
	maxVal : float
		The maximum allowed value.

	Returns
	-------
	float
		The given value.
"""
def makeChoiceNumInput(question, minVal, maxVal):
	while True:
		print("\n"+question)
		try:
			var = float(input())
			assert minVal <= var <= maxVal
			return var
		except:
			print("Invalid input.")

###########
# SEEDING #
###########

"""
	Encodes an array of variable values into a seed according to a given max value array.

	Parameters
	----------
	varArray : list (int)
		The array of values
	maxValueArray:
		An array of the (number of possible values - 1) of each variable. For example, if you have three variables with the possible values...
		var1 : [0, 1, 2, 3]
		var2 : [0, 1]
		var3 : [0, 1, 2, 3, 4]
		... then the maxValueArray should be [4, 2, 5].
		Note that the maxValueArray's implementation assumes that possible values start at 0 and each increment by 1. For example, if a variable is stated to have 4 possible values, it asusmes those values are [0, 1, 2, 3].
	base : int
		Between 2 and 36. The numerical base used by the seed (in other words, how many values are possible for each character, such as 0-9 and a-z).

	Returns
	-------
	int
		The seed in base-10 numerical form.
	str
		The seed in the given base.
"""
def encodeSeed(varArray, maxValueArray, base=10):
	if base > 36:
		print("Base must be between 2 and 36. Lowering to 36.")
		base = 36
	seed = 0
	baseShift = 0
	for i in range(len(varArray)):
		seed += varArray[i]<<baseShift
		baseShift += maxValueArray[i].bit_length()
	return seed, dec_to_base(seed, base)

"""
	Decodes a string or non-base-10 number into an array of variable values according to a given max value array.

	Parameters
	----------
	seed : str or int
		The seed that will be decoded.
	maxValueArray:
		An array of the (number of possible values - 1) of each variable. For example, if you have three variables with the possible values...
		var1 : [0, 1, 2, 3]
		var2 : [0, 1]
		var3 : [0, 1, 2, 3, 4]
		... then the maxValueArray should be [4, 2, 5].
		Note that the maxValueArray's implementation assumes that possible values start at 0 and each increment by 1. For example, if a variable is stated to have 4 possible values, it asusmes those values are [0, 1, 2, 3].
	base : int
		Unused if seed is an int (base-10 is assumed). Between 2 and 36. The numerical base used by the seed (in other words, how many values are possible for each character, such as 0-9 and a-z).

	Returns
	-------
	list (int)
		An array of variable values decoded from the string. For example, if there are 3 variables, the returned array is [var1's value, var2's value, var3's value]
"""
def decodeSeed(seed, maxValueArray, base=10):
	if type(seed) is str:
		if base > 36:
			print("Base must be between 2 and 36. Lowering to 36.")
			base = 36
		elif base < 2:
			print("Base must be between 2 and 36. Increasing to 2.")
			base = 2
		seed = int(seed, base)
	baseShift = 0
	varArray = []
	for i in range(len(maxValueArray)):
		bitLength = maxValueArray[i].bit_length()
		varArray.append((seed>>baseShift) & ((2**bitLength)-1))
		baseShift += bitLength
	return varArray

"""
	Returns whether or not a seed is possible given a maxValueArray and base.

	Parameters
	----------
	seed : str or int
		The seed that will be verified.
	maxValueArray:
		An array of the (number of possible values - 1) of each variable. For example, if you have three variables with the possible values...
		var1 : [0, 1, 2, 3]
		var2 : [0, 1]
		var3 : [0, 1, 2, 3, 4]
		... then the maxValueArray should be [4, 2, 5].
		Note that the maxValueArray's implementation assumes that possible values start at 0 and each increment by 1. For example, if a variable is stated to have 4 possible values, it asusmes those values are [0, 1, 2, 3].
	base : int
		Between 2 and 36. The numerical base used by the seed (in other words, how many values are possible for each character, such as 0-9 and a-z).

	Returns
	-------
	bool
		Whether or not the seed is valid.
	list (int)
		An array of variable values decoded from the string. For example, if there are 3 variables, the returned array is [var1's value, var2's value, var3's value]
"""
def verifySeed(seed, maxValueArray, base=10):
	if base > 36:
		print("Base must be between 2 and 36. Lowering to 36.")
		base = 36
	elif base < 2:
		print("Base must be between 2 and 36. Increasing to 2.")
		base = 2
	if type(seed) is int:
		base = 10
		seed = dec_to_base(seed,base)
	seed = seed.upper().strip()

	try:
		maxSeed = 0
		baseShift = 0
		for i in range(len(maxValueArray)):
			maxSeed += maxValueArray[i]<<baseShift
			baseShift += maxValueArray[i].bit_length()
		assert int(seed, 36) <= maxSeed
		varsInSeed = decodeSeed(seed, maxValueArray, base)
		for i in range(len(varsInSeed)):
			assert 0 <= varsInSeed[i] <= maxValueArray[i]
		return True, varsInSeed
	except:
		return False, None

"""
	From https://www.codespeedy.com/inter-convert-decimal-and-any-base-using-python/

	Converts a base-10 int into a different base.

	Parameters
	----------
	num : int
		The number that will be converted.
	base : int
		Between 2 and 36. The numerical base used by the seed (in other words, how many values are possible for each character, such as 0-9 and a-z).

	Returns
	-------
	str
		The number in the given base.
"""
def dec_to_base(num,base):  #Maximum base - 36
    base_num = ""
    while num>0:
        dig = int(num%base)
        if dig<10:
            base_num += str(dig)
        else:
            base_num += chr(ord('A')+dig-10)  #Using uppercase letters
        num //= base
    base_num = base_num[::-1]  #To reverse the string
    return base_num

########################
# FILE/PATH MANAGEMENT #
########################

"""
	Writes a value to a file at a given address. Supports multi-byte addresses.

	Parameters
	----------
	file : str
		The file that will be modified.
	address : int
		The value (ideally, a hex value such as 0x12345) that will be modified.
	val : int
		The value that will be written to this address.
	numBytes : int
		The number of bytes that this value will take up.

	Retruns
	-------
	False if the value is too large to be written within the given number of bytes; True otherwise.

	Examples
	--------
	Example 1
		writeToAddress(file.exe, 0x12345, 0x41, 1) will write the following value:
		0x12345 = 41
	Example 2
		writeToAddress(file.exe, 0x12345, 0x6D18, 2) will write the following values:
		0x12345 = 6D
		0x12346 = 18
	Example 3
		writeToAddress(file.exe, 0x12345, 0x1C, 2) will write the following values:
		0x12345 = 00
		0x12346 = 1C
"""
def writeToAddress(file, address, val, numBytes=1):
	if val.bit_length() > numBytes*8:
		print("Given value is greater than "+str(numBytes)+" bytes.")
		return False
	address += (numBytes-1)
	for i in range(numBytes):
		file.seek(address)
		currByte = val & 0xFF
		file.write(bytes([currByte]))
		address -= 1
		val = val>>8
	return True

"""
	From https://gist.github.com/jacobtomlinson/9031697

	Removes all empty folders, including nested empty folders, in a directory.

	Parameters
	----------
	p : str
		The path of the starting directory; all empty folders that are children (or grandchildren, etc) of this directory are removed.
"""
def removeEmptyFolders(p):
	if not path.isdir(p):
		return
	files = listdir(p)
	if len(files):
		for f in files:
			fullpath = path.join(p, f)
			if path.isdir(fullpath):
				removeEmptyFolders(fullpath)
	files = listdir(p)
	if len(files) == 0:
		rmdir(p)

"""
	Returns an array of the individual components of a given path.

	Parameters
	----------
	p : str
		The path.

	Returns
	-------
	list (str)
		The path array.

	Example
	-------
	Input
		"C:/early folder/test2/thing.exe"
	Output
		["C:", "early folder", "test2", "thing.exe"]
"""
def getPathArray(p):
	p1, p2 = path.split(p)
	if p2 == "":
		p = p1
	pathArray = []
	while True:
		p1, p2 = path.split(p)
		pathArray = [p2] + pathArray
		if p2 == "":
			pathArray = [p1] + pathArray
			try:
				while pathArray[0] == "":
					del pathArray[0]
			except:
				pass
			return pathArray
		p = p1

"""
	Creates the given directory. Unlike mkdir, this will also create any necessary parent directories that do not already exist.

	Parameters
	----------
	p : str
		The path of the folder that will be created.
"""
def createDir(p):
	if path.isdir(p):
		return
	pathArray = getPathArray(p)
	currPath = pathArray[0]
	for i in range(1, len(pathArray)):
		currPath = path.join(currPath, pathArray[i])
		if not path.isdir(currPath):
			mkdir(currPath)

"""
	Returns the directory containing the current program, regardless of whether it is a standalone script or a wrapped executable.

	Returns
	-------
	str
		The directory containing the current program.
"""
def getCurrFolder():
	if getattr(sys, 'frozen', False):
		mainFolder = path.dirname(sys.executable) # EXE (executable) file
	else:
		mainFolder = path.dirname(path.realpath(__file__)) # PY (source) file
	sys.path.append(mainFolder)
	return mainFolder

"""
	Returns the file extension (including the ".") of the first file found in the given folder that matches the given file name.

	Parameters
	----------
	folder : str
		The given folder.
	fileName : str
		The given file name.

	Returns:
	str
		The file extension (including the ".") of the first file found in folder named fileName (with any extension); if no file with that name is found, return an empty string.
"""
def getFileExt(folder, fileName):
	for f in listdir(folder):
		fName, fExt = path.splitext(f)
		if fName == fileName:
			return fExt
	return ""

####################
# ARRAY MANAGEMENT #
####################

"""
	Returns whether or not two arrays overlap. In other words, return True if and only if at least one element of arr1 exists in arr2.

	Parameters
	----------
	arr1 : list
		The first array.
	arr2 : list
		The second array.

	Returns
	-------
	bool
		Whether or not there is an overlap.
"""
def arrayOverlap(arr1, arr2):
	for a in arr1:
		if a in arr2:
			return True
	return False

"""
	Merges a nested array into a single one-dimensional array.

	Parameters
	----------
	arr : list
		The nested array that will be merged.
	finalArr : list (str)
		Should be ignored (only used in recursion). The created array so far.

	Returns
	-------
	list (str):
		The merged array.

	Example
	-------
	Input
		[item1, [item2, item3], item4, [item 5, [item6, item7], item8]]
	Output
		[item1, item2, item3, item4, item5, item6, item7, item8]
"""
def mergeNestedArray(arr, finalArr=[]):
	for val in arr:
		if not isinstance(val, list):
			finalArr.append(val)
		else:
			finalArr = mergeNestedArray(val, finalArr)
	return finalArr

"""
	From https://www.geeksforgeeks.org/python-find-most-frequent-element-in-a-list/

	Returns the most common element in a list, along with how many times it occurrs.

	Parameters
	----------
	arr : list
		The array.

	Returns
	-------
	anything
		The most frequently-occurring element.
	int
		How many instances of this element there are in the array.
"""
def most_frequent(arr): 
    counter = 0
    elem = arr[0]
    for i in arr:
        curr_frequency = arr.count(i)
        if (curr_frequency > counter):
            counter = curr_frequency
            elem = i
    return elem, counter

"""
	Returns whether or not arr1 is an ordered subset of arr2.

	Parameters
	----------
	arr1 : list
		The first array.
	arr2: list
		The second array.

	Returns
	-------
	bool
		Whether or not arr1 is an ordered subset of arr2.

	Examples
	--------
	Input 1
		[3, 5], [1, 3, 5, 7, 9]
	Output 1
		True
	Input 2
		[3, 5], [1, 2, 3, 4, 5, 6, 7]
	Output 2
		False
"""
def arrayInArray(arr1, arr2):
	for i in range(len(arr2)-len(arr1)+1):
		passed = True
		for j in range(len(arr1)):
			if arr1[j] != arr2[i+j]:
				passed = False
				break
		if passed:
			return True
	return False

###############################
# CONSOLE/TERMINAL MANAGEMENT #
###############################

"""
	Clears the console screen.
"""
def clearScreen():
	os.system('clear' if os.name =='posix' else 'cls')

"""
	From https://www.quora.com/How-can-I-delete-the-last-printed-line-in-Python-language

	Clears ("backspaces") the last n console lines.

	PARAMETERS
	----------
	n : int
		The number of lines to clear.
"""
def delete_last_lines(n=1): 
	for _ in range(n): 
		sys.stdout.write('\x1b[1A')
		sys.stdout.write('\x1b[2K')

"""
SOURCES

dec_to_base
https://www.codespeedy.com/inter-convert-decimal-and-any-base-using-python/

removeEmptyFolders
https://gist.github.com/jacobtomlinson/9031697

most_frequent
https://www.geeksforgeeks.org/python-find-most-frequent-element-in-a-list/

All other functions made by GateGuy
"""
