from os import path, mkdir, listdir, remove, walk, rename, rmdir
import re
import xml.etree.ElementTree as ET
import zipfile
import numpy
import shutil
from pathlib import Path as plpath
from math import ceil
from time import sleep
from tkinter import filedialog
from tkinter import *

# the same folder where this program is stored
if getattr(sys, 'frozen', False):
	progFolder = path.dirname(sys.executable) # EXE (executable) file
else:
	progFolder = path.dirname(path.realpath(__file__)) # PY (source) file
sys.path.append(progFolder)

try:
	from settings import *
except:
	print("Settings file not found.")
	from settingsRebuilder import *
	rebuildSettingsFile()
	print("Created new settings file as settings.py. Edit settings.py with your own directories.")
	input("Press Enter to exit.")
	sys.exit()

from gatelib import makeChoice, arrayOverlap, getPathArray, createDir, removeEmptyFolders, clearScreen

# User settings
if not path.isdir(profilesFolder):
	print("Profiles folder not found. Creating new folder as "+profilesFolder)
	createDir(profilesFolder)
if romsetFolder == "":
	systemDirs = []
elif not path.isdir(romsetFolder):
	print("WARNING: Could not find romset folder.")
	sleep(2)
	systemDirs = []
else:
	systemDirs = [d for d in listdir(romsetFolder) if path.isdir(path.join(romsetFolder, d))]

if otherFolder == "":
	otherDirs = []
elif not path.isdir(otherFolder):
	print("WARNING: Could not find Other folder.")
	sleep(2)
	otherDirs = []
else:
	otherDirs = [d for d in listdir(otherFolder) if path.isdir(path.join(otherFolder, d))]

biasPriority = [
	"World", "USA", "En", "Europe", "Australia", "Canada", "Japan", "Ja",
	"France", "Fr", "Germany", "De", "Spain", "Es", "Italy", "It", "Norway",
	"Brazil", "Sweden", "China", "Zh", "Korea", "Ko", "Asia", "Netherlands",
	"Russia", "Ru", "Denmark", "Nl", "Pt", "Sv", "No", "Da", "Fi", "Pl",
	"Unknown"
]
zoneBiasValues = {
	"World" : 0,
	"U" : 0,
	"USA" : 0,
	"En" : 1,
	"E" : 2,
	"Europe" : 2,
	"A" : 3,
	"Australia" : 3,
	"Ca" : 4,
	"Canada" : 4,
	"J" : 5,
	"Japan" : 5,
	"Ja" : 5,
	"F" : 6,
	"France" : 6,
	"Fr" : 6,
	"G" : 7,
	"Germany" : 7,
	"De" : 7,
	"S" : 8,
	"Spain" : 8,
	"Es" : 8,
	"I" : 9,
	"Italy" : 9,
	"It" : 9,
	"No" : 10,
	"Norway" : 10,
	"Br" : 11,
	"Brazil" : 11,
	"Sw" : 12,
	"Sweden" : 12,
	"Cn" : 13,
	"China" : 13,
	"Zh" : 13,
	"K" : 14,
	"Korea" : 14,
	"Ko" : 14,
	"As" : 15,
	"Asia" : 15,
	"Ne" : 16,
	"Netherlands" : 16,
	"Ru" : 17,
	"Russia" : 17,
	"Da" : 18,
	"Denmark" : 18,
	"Nl" : 19,
	"Pt" : 20,
	"Sv" : 21,
	"No" : 22,
	"Da" : 23,
	"Fi" : 24,
	"Pl" : 25
}

zoneNumToZone = {
	0 : "U",
	# 1 : "",
	2 : "E",
	3 : "A",
	4 : "Ca",
	5 : "J",
	6 : "F",
	7 : "G",
	8 : "S",
	9 : "I",
	10 : "No",
	11 : "Br",
	12 : "Sw",
	13 : "Cn",
	14 : "K",
	15 : "As",
	16 : "Ne",
	17 : "Ru",
	18 : "Da",
	19 : "Nl",
	20 : "Pt",
	21 : "Sv",
	22 : "No",
	23 : "Da",
	24 : "Fi",
	25 : "Pl"
}

categoryValues = {
	"Games" : 0,
	"Demos" : 1,
	"Bonus Discs" : 2,
	"Applications" : 3,
	"Coverdiscs" : 4
}

compilationArray = [
	"2 Games in 1 -", "2 Games in 1! -", "2 Disney Games -", "2 Great Games! -",
	"2 in 1 -", "2 in 1 Game Pack -", "2-in-1 Fun Pack -", "3 Games in 1 -",
	"4 Games on One Game Pak", "Double Game!", "Double Pack", "2 Jeux en 1",
	"Crash Superpack", "Spyro Superpack", "Crash & Spyro Superpack"
]
classicNESArray = ["Classic NES Series", "Famicom Mini", "Hudson Best Collection"]

skippedAttributes = [
	"Rev", "Beta", "Virtual Console", "Proto", "Unl", "v", "Switch Online",
	"GB Compatible", "SGB Enhanced", "Demo", "Disc", "Promo", "Sample", "DLC",
	"WiiWare", "GameCube", "Minis", "Promotion Card", "Namcot Collection",
	"Namco Museum Archives", "Club Nintendo", "Aftermarket", "Test Program",
	"Competition Cart", "NES Test"
]

# -------------- #
# Main functions #
# -------------- #

def main():
	global systemName
	global deviceName
	global deviceProfile
	global outputFolder
	global systemFolder
	global databaseFile
	global isNoIntro
	global skippedFoldersOnDevice

	clearScreen()
	print("\n########################")
	print("# Rom Organizer Deluxe #")
	print("########################\n")

	deviceProfiles = listdir(profilesFolder)
	if len(deviceProfiles) > 0:
		dp = makeChoice("\nSelect a device profile (which device are you copying to?)", [path.splitext(prof)[0] for prof in deviceProfiles]+["Create new profile"])
		if dp == len(deviceProfiles)+1:
			createDeviceProfile()
		else:
			dn = deviceProfiles[dp-1]
			deviceProfile = path.join(profilesFolder, dn)
			deviceName = path.splitext(dn)[0]
	else:
		print("\nNo device profiles found. Please follow these steps to create a new profile.")
		createDeviceProfile()
	currProfileSystemDirs = [d for d in systemDirs if getRomsetCategory(d) != "None"]
	if len(currProfileSystemDirs) == 0:
		if len(systemDirs) > 0:
			print("The current profile does not allow any romsets.")
		systemChoices = []
	else:
		systemChoices = makeChoice("Select romset(s). You can select multiple choices by separating them with spaces:", currProfileSystemDirs+["All", "None"], allowMultiple=True)
		if len(currProfileSystemDirs)+2 in systemChoices:
			systemChoices = []
		elif len(currProfileSystemDirs)+1 in systemChoices:
			systemChoices = list(range(1, len(currProfileSystemDirs)+1))
	if otherFolder != "":
		otherFolderName = path.basename(otherFolder)
		currProfileOtherDirs = [d for d in otherDirs if getOtherCategory(d) == "True"]
		if len(currProfileSystemDirs) == 0:
			if len(otherDirs) > 0:
				print("The current profile does not allow any "+otherFolderName+" folders.")
			otherChoices = []
		else:
			otherChoices = makeChoice("Select system(s) from "+otherFolderName+" folder. You can select multiple choices by separating them with spaces:", currProfileOtherDirs+["All", "None"], allowMultiple=True)
			if len(currProfileOtherDirs)+2 in otherChoices:
				otherChoices = []
			elif len(currProfileOtherDirs)+1 in otherChoices:
				otherChoices = list(range(1, len(currProfileOtherDirs)+1))
		if updateFromDeviceFolder != "":
			updateOtherChoice = makeChoice("Update \""+path.basename(updateFromDeviceFolder)+"\" folder by adding any files that are currently exclusive to "+deviceName+"?", ["Yes", "No"])
		else:
			updateOtherChoice = 2
	ignoredAttributes = getIgnoredAttributes()
	primaryRegions = getPrimaryRegions()
	skippedFoldersOnDevice = getSkippedOtherFolders()
	if len(systemChoices) > 0:
		ai = makeChoice("How should unfound database entries be handled?", ["Pause when a database entry is not found so I can correct it", "Skip all interruptions"])
		allowInterruptions = (ai == 1)
	else:
		allowInterruptions = False
	print("\nPlease select the ROM directory of your "+deviceName+" (example: F:/Roms).")
	root = Tk()
	root.withdraw()
	outputFolder = ""
	while outputFolder == "":
		outputFolder = filedialog.askdirectory()
		if outputFolder != "":
			isCorrect = makeChoice("Are you sure this is the correct folder?\n"+outputFolder, ["Yes", "No"])
			if isCorrect == 2:
				outputFolder = ""
	clearScreen()
	if logFolder != "":
		createDir(logFolder)
	for sc in systemChoices:
		systemName = currProfileSystemDirs[sc-1]
		romsetCategory = getRomsetCategory(systemName)
		if romsetCategory in ["Full", "1G1R", "1G1R Primary"]:
			systemFolder = path.join(romsetFolder, systemName)
			systemNameLower = systemName.lower()
			numParenInSN = systemNameLower.count("(")
			isNoIntro = True
			databaseFile = ""
			for f in listdir(redumpDir):
				if f.split(" - Datfile")[0].strip().lower() == systemNameLower:
					databaseFile = path.join(redumpDir, f)
					isNoIntro = False
					break
			if databaseFile == "":
				for f in listdir(noIntroDir):
					if f.split(" (XMDB)")[0].replace(" (Encrypted)", "").replace(" (Decrypted)", "").replace(" (BigEndian)", "").replace(" (LittleEndian)", "").replace(" (WAD)", "").strip().lower() == systemNameLower:
						databaseFile = path.join(noIntroDir, f)
						break
				if databaseFile == "":
					print("Database file for current system not found.")
					print("Skipping current system.")
					continue
			fixNamesAndGenerateMergeDict(allowInterruptions)
			copyRomset(romsetCategory, ignoredAttributes, primaryRegions)
	if otherFolder != "":
		for oc in otherChoices:
			otherChoice = currProfileOtherDirs[oc-1]
			systemName = otherChoice
			otherCategory = getOtherCategory(systemName)
			if otherCategory == "True":
				copyOther(ignoredAttributes)
	if updateFromDeviceFolder != "":
		if updateOtherChoice == 1:
			updateOther()
	if logFolder != "":
		print("\nReview the log files for more information on what files were excanged between the main drive and "+deviceName+".")
	input("Press Enter to exit.")

def createDeviceProfile():
	global deviceName
	global deviceProfile

	deviceName = ""
	while deviceName == "":
		print("\n(1/5) What would you like to name this profile?")
		deviceName = input().strip()
	deviceProfile = path.join(profilesFolder, deviceName+".txt")
	dpFile = open(deviceProfile, "w")
	dpFile.writelines(": Romsets\n")
	print("\n(2/5) Please define how each romset should be copied to this device.")
	for d in systemDirs:
		copyType = makeChoice(d, ["Full (copy all contents)",
			"1G1R (copy only the most significant rom for each game)",
			"1G1R Primary (same as 1G1R, but ignore games that do not have a rom for a primary region (explained in question 4)",
			"None (skip this system)"])
		if copyType == 1:
			copyType = "Full"
		elif copyType == 2:
			copyType = "1G1R"
		elif copyType == 3:
			copyType = "1G1R Primary"
		else:
			copyType = "None"
		dpFile.writelines(d+"\n"+copyType+"\n")
	if otherFolder != "":
		dpFile.writelines("\n\n\n: Other\n")
		print("\nPlease define whether or not each folder in the Other category should be copied to this device.")
		for d in otherDirs:
			copyType = makeChoice(d, ["Yes", "No"])
			if copyType == 1:
				copyType = "True"
			else:
				copyType = "False"
			dpFile.writelines(d+"\n"+copyType+"\n")
	else:
		print("\n(2/5) [You do not have an Other folder. Skipping this question.")
	dpFile.writelines("\n\n\n: Ignore\n")
	print("\n(3/5) Please type the exact names of any folders you would like to skip in copying. Remember that subfolders generated by this program are included in brackets [].")
	print("For example, if you wanted to skip all Japanese roms, you would type [Japan] (including the brackets), followed by Enter.")
	print("Type DONE (in all caps) followed by Enter when you are done.")
	print("Common subfolders are [USA], [Europe], [Japan], [Other (English)], [Other (non-English)],")
	print("[Unlicensed], [Unreleased], [Compilation] (only for 2/3/4 in 1 GBA games), [NES & Famicom] (only for GBA ports of NES/Famicom games), and [GBA Video]")
	while True:
		currChoice = input().strip()
		if currChoice == "DONE":
			break
		if currChoice != "":
			dpFile.writelines(currChoice+"\n")
	dpFile.writelines("\n\n\n: Primary Regions\n")
	print("\n(4/5) Please type the exact names of any folders you would like to prioritize in copying. Remember that subfolders generated by this program are included in brackets [].")
	print("These folders will not be created in romset organization; instead, their contents are added to the root folder of the current system.")
	print("For example, if you wanted all USA roms in the root folder instead of a [USA] subfolder, you would type [USA] (including the brackets), followed by Enter.")
	print("Type DONE (in all caps) followed by Enter when you are done.")
	print("Common subfolders are [USA], [Europe], [Japan], [Other (English)], and [Other (non-English)]")
	while True:
		currChoice = input().strip()
		if currChoice == "DONE":
			break
		if currChoice != "":
			dpFile.writelines(currChoice+"\n")
	dpFile.writelines("\n\n\n: Skipped Folders on Device\n")
	print("\n(5/5) Please type the exact names of any folders in your device's rom folder that you do not want to copy back to the main drive.")
	print("These folders will be skipped; this is useful if you keep roms and non-rom PC games in the same folder.")
	print("For example, if you wanted to ignore anything in the \"Steam\" folder, you would type \"Steam\" (no quotes), followed by Enter.")
	print("Type DONE (in all caps) followed by Enter when you are done.")
	print("Common subfolders are Steam, Windows, and PC Games")
	while True:
		currChoice = input().strip()
		if currChoice == "DONE":
			break
		if currChoice != "":
			dpFile.writelines(currChoice+"\n")
	dpFile.close()
	print("\nDevice Profile saved as "+deviceProfile+".")
	sleep(2)

def fixNamesAndGenerateMergeDict(allowInterruptions=True, verbose=False):
	global mergeDict
	global categoryDict

	print("\nScanning romset for "+systemName)
	mergedClones = []
	unmergedClones = []
	skipAll = not allowInterruptions
	mergeDict = {}
	categoryDict = {}
	allFiles = [f for f in listdir(systemFolder) if path.isfile(path.join(systemFolder, f))]
	tree = ET.parse(databaseFile)
	root = tree.getroot()
	numCurrZoned = 0
	if isNoIntro:
		zoneContainer = root[0][1]
	else:
		zoneContainer = root[1:]
	numZoneds = len(zoneContainer)
	step = max(numZoneds//20, 1)
	for currZoned in zoneContainer:
		if isNoIntro:
			allBiases = [bias.get("name") for bias in currZoned.findall("bias")]
			allZones = [bias.get("zone") for bias in currZoned.findall("bias")]
			allClones = [clone.get("name") for clone in currZoned.findall("clone")]
			category = "Games"
		else:
			allClones = [currZoned.get("name")]
			allBiases = [clone.split(" (")[0] for clone in allClones]
			allZones = []
			category = currZoned.find("category").text
			for clone in allClones:
				bestZoneNum = 99
				bestZone = ""
				for att in getAttributeSplit(clone):
					currZoneNum = zoneBiasValues.get(att)
					if currZoneNum is not None and currZoneNum < bestZoneNum:
						bestZoneNum = currZoneNum
						bestZone = zoneNumToZone.get(bestZoneNum)
				allZones.append(bestZone)
		allClonesLower = [clone.lower() for clone in allClones]
		for file in allFiles:
			# if the file exists, but the capitalization is wrong (example: "Sega" instead of "SEGA"), fix it
			for i in range(len(allClones)):
				fileExt = path.splitext(file)[1]
				if file.lower() == allClonesLower[i]+fileExt and file != allClones[i]+fileExt:
					currFilePath = path.join(systemFolder, file)
					newFilePath = path.join(systemFolder, allClones[i]+fileExt)
					print("Capitalization fix:")
					if zipfile.is_zipfile(currFilePath):
						renameArchiveAndContent(currFilePath, newFilePath, allClones[i])
					else:
						rename(currFilePath, newFilePath)
		mergeRegionIndex, mergeName = getBestMergeName(allBiases, allZones)
		gameCurrLocation = getGameLocation(mergeName)
		if gameCurrLocation is not None:
			print("Attempting to resolve naming conflict for "+mergeName+"\n")
			mergeName = handleDuplicateName(mergeName, allClones, path.join(systemFolder, gameCurrLocation))
		allClonesList = list(dict.fromkeys(allClones))
		for currCloneName in allClonesList:
			currCloneNameWithExt = currCloneName+getFileExt(systemFolder, currCloneName)
			currCloneFile = path.join(systemFolder, currCloneNameWithExt)
			cloneExists = False
			if path.isfile(currCloneFile):
				cloneExists = True
			else:
				print("\nThe following ROM was not found:")
				print(currCloneName)
				print("\nAll clones for this game:")
				for c in allClonesList:
					print(c)
				recommendations = [f for f in allFiles if f.startswith(currCloneName.split("(")[0]+"(") and not path.splitext(f)[0] in mergedClones]
				if currCloneName+" [b].zip" in recommendations:
					print("Romset contains bad dump of this rom. Skipping.")
					currWrongName = "SKIP"
				else:
					cwn = guessOldName(recommendations, currCloneName)
					if cwn == 0:
						if skipAll:
							currWrongName = "SKIP"
						else:
							cwn = makeChoice("Which ROM in your romset matches the missing ROM? It will be renamed.", recommendations+["OTHER", "SKIP", "SKIP ALL"])
					if (not skipAll) or cwn > 0:
						if cwn == len(recommendations) + 1:
							print("Enter the exact name of this ROM file in your romset (with extension if the extension isn\'t ZIP), or type \"SKIP\" (no quotes) to skip this ROM.")
							currWrongName = input()
						elif cwn == len(recommendations) + 2:
							currWrongName = "SKIP"
						elif cwn == len(recommendations) + 3:
							currWrongName = "SKIP"
							skipAll = True
						else:
							currWrongName = recommendations[cwn-1]
						if path.splitext(currWrongName)[1] == "" and currWrongName != "SKIP":
							currWrongName = currWrongName + ".zip"
						currWrongClone = path.join(systemFolder, currWrongName)
				if currWrongName == "SKIP":
					print()
				elif path.isfile(currWrongClone):
					currCloneFile = path.splitext(currCloneFile)[0]+path.splitext(currWrongClone)[1]
					currCloneNameWithExt = path.basename(currCloneFile)
					if zipfile.is_zipfile(currWrongClone):
						renameArchiveAndContent(currWrongClone, currCloneFile, currCloneName)
					else:
						rename(currWrongClone, currCloneFile)
					cloneExists = True
				else:
					print("\nInvalid name. Skipping.")
			if cloneExists:
				addGameFileLocationToDict((mergeName, mergeRegionIndex), currCloneNameWithExt)
				if isNoIntro:
					categoryDict[mergeName] = "Games"
				else:
					try:
						catDictVal = categoryDict[mergeName]
					except:
						catDictVal = None
					try:
						oldVal = categoryValues[catDictVal]
					except:
						oldVal = None
					newVal = categoryValues[category]
					if catDictVal is None or oldVal is None:
						categoryDict[mergeName] = category
					elif newVal is not None:
						categoryDict[mergeName] = categoryDict[mergeName] if oldVal < newVal else category
				mergedClones.append(currCloneName)
			else:
				unmergedClones.append(currCloneName)
		if verbose:
			print("Scanned all versions of "+mergeName)
		numCurrZoned += 1
		if numCurrZoned % step == 0:
			print(str(round(numCurrZoned*100/numZoneds, 1))+"% - Scanned "+str(numCurrZoned)+" of "+str(numZoneds)+".")
	print("Finished scanning romset.")
	if logFolder != "":
		print("Creating romset log.")
		createRomsetLog(mergedClones, unmergedClones)
		print("Done.")

def getRomsetCategory(currSystemName):
	profile = open(deviceProfile,"r")
	lines = profile.readlines()
	inCategory = False
	for i in range(len(lines)):
		if not inCategory:
			if lines[i].startswith(": Romsets"):
				inCategory = True
			continue
		if lines[i].strip() == currSystemName:
			return lines[i+1].strip()
	print("WARNING: "+currSystemName+" not found in current profile. Please add it manually.\nDefaulting to None.")
	sleep(2)
	return "None"

def getOtherCategory(currSystemName):
	profile = open(deviceProfile,"r")
	lines = profile.readlines()
	inCategory = False
	for i in range(len(lines)):
		if not inCategory:
			if lines[i].startswith(": Other"):
				inCategory = True
			continue
		if lines[i].strip() == currSystemName:
			return lines[i+1].strip()
	print("WARNING: "+currSystemName+" not found in current profile. Please add it manually.\nDefaulting to False.")
	sleep(2)
	return "False"

def getIgnoredAttributes():
	profile = open(deviceProfile,"r")
	lines = profile.readlines()
	inCategory = False
	ignoredAttributes = []
	for i in range(len(lines)):
		if not inCategory:
			if lines[i].startswith(": Ignore"):
				inCategory = True
			continue
		currLine = lines[i].strip()
		if currLine == "":
			return ignoredAttributes
		else:
			ignoredAttributes.append(currLine)
	return ignoredAttributes

def getPrimaryRegions():
	profile = open(deviceProfile,"r")
	lines = profile.readlines()
	inCategory = False
	primaryRegions = []
	for i in range(len(lines)):
		if not inCategory:
			if lines[i].startswith(": Primary Regions"):
				inCategory = True
			continue
		currLine = lines[i].strip()
		if currLine == "":
			return primaryRegions
		else:
			primaryRegions.append(currLine)
	return primaryRegions

def getSkippedOtherFolders():
	profile = open(deviceProfile,"r")
	lines = profile.readlines()
	inCategory = False
	skippedFoldersOnDevice = []
	for i in range(len(lines)):
		if not inCategory:
			if lines[i].startswith(": Skipped Folders on Device"):
				inCategory = True
			continue
		currLine = lines[i].strip()
		if currLine == "":
			return skippedFoldersOnDevice
		else:
			skippedFoldersOnDevice.append(currLine)
	return skippedFoldersOnDevice

def copyRomset(romsetCategory, ignoredAttributes, primaryRegions):
	if romsetCategory not in ["Full", "1G1R", "1G1R Primary"]:
		return
	print("\nCopying romset for "+systemName+".")
	newRomsetFiles = []
	failedRomsetFiles = []
	numGames = len(mergeDict.keys())
	step = max(numGames//20, 1)
	currGameNum = 0
	numNewFilesInOutput = 0
	for gameNameAndRegionNum in mergeDict.keys():
		gameName, gameRegionNum = gameNameAndRegionNum
		currGame = mergeDict[gameNameAndRegionNum]
		bestRom = getBestRom(currGame)
		attributes = getAttributeSplit(bestRom)
		if gameName.startswith("[BIOS]"):
			gameRegion = "[BIOS]"
		elif "Test Program" in attributes:
			gameRegion = "[Test Program]"
		elif gameRegionNum == 0:
			gameRegion = "[USA]"
		elif gameRegionNum == 2:
			gameRegion = "[Europe]"
		elif gameRegionNum in [1,3,4]:
			gameRegion = "[Other (English)]"
		elif gameRegionNum == 5:
			gameRegion = "[Japan]"
		else:
			gameRegion = "[Other (non-English)]"
		if gameRegion in primaryRegions:
			gameRegion = ""
		unlicensedStr = "[Unlicensed]" if "Unl" in attributes else ""
		unreleasedStr = "[Unreleased]" if "Proto" in attributes else ""
		compilationStr = "[Compilations]" if (systemName == "Nintendo - Game Boy Advance" and any([gameName.startswith(comp) for comp in compilationArray])) else ""
		classicNESStr = "[NES & Famicom]" if (systemName == "Nintendo - Game Boy Advance" and any([gameName.startswith(nes) for nes in classicNESArray])) else ""
		gbaVideoStr = "[GBA Video]" if gameName.startswith("Game Boy Advance Video") else ""
		demoStr = "[Demos]" if "Sample" in attributes or "Demo" in attributes else ""
		redumpCategory = categoryDict[gameName]
		if redumpCategory == "Games":
			redumpCategory = ""
		else:
			if redumpCategory in [unlicensedStr, unreleasedStr, compilationStr, classicNESStr, gbaVideoStr, demoStr]:
				redumpCategory = ""
			else:
				redumpCategory = "["+redumpCategory+"]"
		if romsetCategory == "Full":
			for rom in currGame:
				oldFile = path.join(systemFolder, rom)
				newDir = path.join(outputFolder, systemName, gameRegion, compilationStr, classicNESStr, gbaVideoStr, unlicensedStr, demoStr, redumpCategory, unreleasedStr, gameName)
				newDirPathArray = getPathArray(newDir)
				if arrayOverlap(ignoredAttributes, newDirPathArray):
					continue
				newFile = path.join(newDir, rom)
				if not path.isfile(newFile):
					createDir(newDir)
					try:
						shutil.copy(oldFile, newFile)
						newRomsetFiles.append(rom)
					except:
						print("The following rom failed to copy: "+rom)
						failedRomsetFiles.append(rom)
		elif romsetCategory == "1G1R" or gameRegion == "":
			oldFile = path.join(systemFolder, bestRom)
			newDir = path.join(outputFolder, systemName, gameRegion, compilationStr, classicNESStr, gbaVideoStr, unlicensedStr, unreleasedStr, gameName)
			newDirPathArray = getPathArray(newDir)
			if arrayOverlap(ignoredAttributes, newDirPathArray):
				continue
			newFile = path.join(newDir, bestRom)
			if not path.isfile(newFile):
				createDir(newDir)
				try:
					shutil.copy(oldFile, newFile)
					newRomsetFiles.append(bestRom)
				except:
					print("The following rom failed to copy: "+bestRom)
					failedRomsetFiles.append(bestRom)
					if listdir(newDir) == 0:
						rmdir(newDir)
		currGameNum += 1
		if currGameNum%step == 0:
			print(str(round(currGameNum*100.0/numGames, 1))+"% - Confirmed "+str(currGameNum)+" of "+str(numGames)+" game folders.")
	print("\nCopied "+str(len(newRomsetFiles))+" new files.")
	print("Finished copying romset.")
	if logFolder != "":
		print("Generating New Romset log.")
		createNewRomsetLog(newRomsetFiles, failedRomsetFiles)
		print("Done.")

def copyOther(ignoredAttributes):
	print("\nCopying Other folder for "+systemName+".")
	newOtherFiles = []
	failedOtherFiles = []
	numFiles = 0
	for root, dirs, files in walk(path.join(otherFolder, systemName)):
		for file in files:
			numFiles += 1
	step = max(numFiles//20, 1)
	currFileNum = 0
	sourceSystemOtherDir = path.join(otherFolder, systemName)
	for root, dirs, files in walk(sourceSystemOtherDir):
		for fileName in files:
			currRoot = root.split(sourceSystemOtherDir)[1][1:]
			oldFileDirPathArray = getPathArray(root)
			if arrayOverlap(ignoredAttributes, oldFileDirPathArray):
				continue
			newFileDir = path.join(outputFolder, systemName, currRoot)
			newFile = path.join(newFileDir, fileName)
			if not path.isfile(newFile):
				createDir(newFileDir)
				oldFile = path.join(root, fileName)
				try:
					shutil.copy(oldFile, newFile)
					newOtherFiles.append(newFile)
				except:
					print("The following file failed to copy: "+oldFile)
					failedOtherFiles.append(oldFile)
					if listdir(newFileDir) == 0:
						rmdir(newFileDir)
			currFileNum += 1
			if currFileNum%step == 0:
				print(str(round(currFileNum*100.0/numFiles, 1))+"% - Confirmed "+str(currFileNum)+" of "+str(numFiles)+".")
	print("\nCopied "+str(len(newOtherFiles))+" new files.")
	print("Finished copying Other folder.")
	if logFolder != "":
		print("Generating New Other log.")
		createNewFromOtherLog(newOtherFiles, failedOtherFiles)
		print("Done.")

def updateOther():
	updateFolderName = path.basename(updateFromDeviceFolder)
	print("\nUpdating "+updateFolderName+" folder from "+deviceName+".")
	newFilesInOther = []
	failedOtherFiles = []
	for root, dirs, files in walk(outputFolder):
		dirs[:] = [d for d in dirs if d not in skippedFoldersOnDevice]
		currRoot = root.split(outputFolder)[1][1:]
		try:
			currSystem = getPathArray(currRoot)[0]
		except:
			currSystem = ""
		for file in files:
			fileInOutput = path.join(root, file)
			fileInRomset = path.join(romsetFolder, currSystem, file)
			fileInOther = path.join(otherFolder, currRoot, file)
			updateFolder = path.join(updateFromDeviceFolder, currRoot)
			fileInUpdate = path.join(updateFolder, file)
			if not (path.isfile(fileInRomset) or path.isfile(fileInOther) or path.isfile(fileInUpdate)):
				createDir(updateFolder)
				try:
					shutil.copy(fileInOutput, fileInUpdate)
					print("From "+deviceName+" to "+updateFolderName+": "+fileInUpdate)
					newFilesInOther.append(fileInUpdate)
				except:
					print("The following file failed to copy: "+fileInOutput)
					failedOtherFiles.append(fileInOutput)
	print("\nSuccessfully updated "+updateFolderName+" folder with "+str(len(newFilesInOther))+" new files.")
	print("\nRemoving empty folders from "+updateFolderName+"...")
	removeEmptyFolders(updateFromDeviceFolder)
	print("Done.")
	if logFolder != "":
		print("Generating New Files In "+updateFolderName+" log.")
		createNewInOtherLog(newFilesInOther, failedOtherFiles)
		print("Done.")

# -------------- #
# Helper methods #
# -------------- #

def renameArchiveAndContent(currPath, newPath, newName):
	replaceArchive = False
	newFullFileName = ""
	fileExt = ""
	extractedFile = ""
	with zipfile.ZipFile(currPath, 'r', zipfile.ZIP_DEFLATED) as zippedClone:
		zippedFiles = zippedClone.namelist()
		if len(zippedFiles) > 1:
			print("\nThis archive contains more than one file. Skipping.")
		else:
			zippedClone.extract(zippedFiles[0], systemFolder)
			fileExt = path.splitext(zippedFiles[0])[1]
			extractedFile = path.join(systemFolder, zippedFiles[0])
			newFullFileName = path.splitext(newPath)[0]+fileExt
			rename(extractedFile, newFullFileName)
			replaceArchive = True
	if replaceArchive:
		remove(currPath)
		with zipfile.ZipFile(newPath, 'w', zipfile.ZIP_DEFLATED) as newZip:
			newZip.write(newFullFileName, arcname='\\'+newName+fileExt)
		remove(newFullFileName)
		print("Renamed "+path.splitext(path.basename(currPath))[0]+" to "+newName+"\n")

def getBestMergeName(biases, zones, indexOnly=False):
	zoneValues = []
	for zone in zones:
		currVal = zoneBiasValues.get(zone)
		if currVal is None:
			currVal = 99
		zoneValues.append(currVal)
	mergeIndex = numpy.min(zoneValues)
	if indexOnly:
		return mergeIndex, ""
	mergeName = biases[numpy.argmin(zoneValues)]
	mergeNameArray = getAttributeSplit(mergeName)
	regionIndex = 1
	for i in range(1, len(mergeNameArray)):
		if mergeNameArray[i] in biasPriority:
			mergeName = mergeNameArray[0]
			for j in range(1,i):
				mergeName = mergeName + " (" + mergeNameArray[j] + ")"
			regionIndex = i+1
			break
	suffix = ""
	if len(mergeNameArray) > regionIndex:
		suffix = getSuffix(mergeNameArray[regionIndex:], mergeName)
	mergeName = mergeName + suffix
	mergeName = mergeName.rstrip(".")
	return mergeIndex, mergeName

def getSuffix(attributes, mergeName):
	for att in attributes:
		if att in biasPriority:
			continue
		skip = False
		for skippedAtt in skippedAttributes:
			if att.startswith(skippedAtt):
				skip = True
				break
		if skip:
			continue
		if "Collection" in att:
			continue
		if att.count("-") >= 2:
			continue
		if not " ("+att+")" in mergeName:
			return " ("+att+")"
	return ""

def addGameFileLocationToDict(key, game):
	global mergeDict

	if key not in mergeDict.keys():
		mergeDict[key] = []
	mergeDict[key].append(game)

def getGameLocation(game):
	global mergeDict

	for key in mergeDict.keys():
		if game in mergeDict[key]:
			return key[0]
	return None

def handleDuplicateName(mergeName, secondArchiveClones, mergeNameFirstLocation):
	mergeNameOnly = path.splitext(mergeName)[0]
	if "[BIOS]" in mergeName: # auto-merge BIOS files
		return mergeName
	firstArchiveClones = listdir(mergeNameFirstLocation)
	firstMatchingRegion = getMatchingRegion(firstArchiveClones)
	secondMatchingRegion = getMatchingRegion(secondArchiveClones)
	# rename first archive to region
	if firstMatchingRegion != "" and secondMatchingRegion == "":
		newName = mergeNameOnly+" ("+firstMatchingRegion+")"
		try:
			rename(mergeNameFirstLocation, path.join(mergedFolder, newName))
		except:
			pass
		return mergeName
	# rename second archive to region
	if firstMatchingRegion == "" and secondMatchingRegion != "":
		newName = mergeNameOnly+" ("+secondMatchingRegion+")"
		return newName
	# rename both archives to region
	if firstMatchingRegion != "" and secondMatchingRegion != "":
		newName1 = mergeNameOnly+" ("+firstMatchingRegion+")"
		try:
			rename(mergeNameFirstLocation, path.join(mergedFolder, newName1))
		except:
			pass
		newName2 = mergeNameOnly+" ("+secondMatchingRegion+")"
		return newName2
	# rename neither (merge)
	return mergeName

def getMatchingRegion(clones):
	try:
		matchingRegion = getAttributeSplit(clones[0])[1]
		for i in range(1, len(clones)):
			if matchingRegion != getAttributeSplit(clones[i])[1]:
				return ""
		return matchingRegion
	except:
		return ""

def getAttributeSplit(name):
	mna = [s.strip() for s in re.split('\(|\)', name) if s.strip() != ""]
	mergeNameArray = []
	mergeNameArray.append(mna[0])
	if len(mna) > 1:
		for i in range(1, len(mna)):
			if not ("," in mna[i] or "+" in mna[i]):
				mergeNameArray.append(mna[i])
			else:
				arrayWithComma = [s.strip() for s in re.split('\,|\+', mna[i]) if s.strip() != ""]
				for att2 in arrayWithComma:
					mergeNameArray.append(att2)
	return mergeNameArray

def guessOldName(recommendations, ccn):
	currCloneName = ccn.replace("&amp;", "&")
	replacementArr = [
		("(Rev A)", "(Rev 1)"),
		("(Rev B)", "(Rev 2)"),
		("(Rev C)", "(Rev 3)"),
		("(Rev D)", "(Rev 4)"),
		("(Rev E)", "(Rev 5)"),
		("(Rev F)", "(Rev 6)"),
		("(Beta A)", "(Beta 1)"),
		("(Beta B)", "(Beta 2)"),
		("(Beta C)", "(Beta 3)"),
		("(Beta D)", "(Beta 4)"),
		("(Beta E)", "(Beta 5)"),
		("(Beta F)", "(Beta 6)"),
		("(Proto A)", "(Proto 1)"),
		("(Proto B)", "(Proto 2)"),
		("(Proto C)", "(Proto 3)"),
		("(Proto D)", "(Proto 4)"),
		("(Proto E)", "(Proto 5)"),
		("(Proto F)", "(Proto 6)"),
		("(Rev A)", "(Reprint)"),
		("(Rev 1)", "(Reprint)"),
		("(USA, Australia)", "(USA)"),
		("(USA, Europe)", "(USA)"),
	]
	for i in range(len(recommendations)):
		currRec = path.splitext(recommendations[i])[0].replace("&amp;", "&")
		for j in range(len(replacementArr)):
			elem1, elem2 = replacementArr[j]
			if currRec.replace(elem1, elem2) == currCloneName or currRec.replace(elem2, elem1) == currCloneName:
				return i+1
	return 0

def getFileExt(folder, fileName):
	for f in listdir(folder):
		fName, fExt = path.splitext(f)
		if fName == fileName:
			return fExt
	return ""

def getBestRom(clones):
	zoneValues = []
	cloneScores = []
	sortedClones = sorted(clones)
	for clone in sortedClones:
		attributes = getAttributeSplit(clone)[1:]
		revCheck = [a for a in attributes if len(a) >= 3]
		versionCheck = [a[0] for a in attributes]
		betaCheck = [a for a in attributes if len(a) >= 4]
		protoCheck = [a for a in attributes if len(a) >= 5]
		currZoneVal = 99
		for i in range(len(biasPriority)):
			if biasPriority[i] in attributes:
				currZoneVal = i
				break
		zoneValues.append(currZoneVal)
		currScore = 100
		if "Rev" in revCheck:
			currScore += 30
		if "v" in versionCheck:
			currScore += 30
		if "Beta" in betaCheck or "Proto" in protoCheck:
			currScore -= 50
		if "Virtual Console" in attributes or "GameCube" in attributes or "Collection" in attributes:
			currScore -= 10
		if "Sample" in attributes or "Demo" in attributes or "Promo" in attributes:
			currScore -= 90
		cloneScores.append(currScore)
	bestZones = numpy.where(zoneValues == numpy.min(zoneValues))[0].tolist()
	finalZone = 99
	bestScore = -500
	for zone in bestZones:
		currScore = cloneScores[zone]
		if currScore >= bestScore:
			bestScore = currScore
			finalZone = zone
	return sortedClones[finalZone]

def createRomsetLog(mergedClones, unmergedClones):
	mergedClones.sort()
	unmergedClones.sort()
	romsetLogFile = open(path.join(logFolder, "Log - Romset - "+systemName+".txt"), "w", encoding="utf-8", errors="replace")
	romsetLogFile.writelines("=== "+systemName+" ===\n")
	numMergedClones = len(mergedClones)
	numUnmergedClones = len(unmergedClones)
	romsetLogFile.writelines("=== This romset contains "+str(numMergedClones)+" of "+str(numMergedClones+numUnmergedClones)+" known ROMs ===\n\n")
	romsetLogFile.writelines("= CONTAINS =\n")
	for clone in mergedClones:
		romsetLogFile.writelines(clone+"\n")
	if len(unmergedClones) > 0:
		romsetLogFile.writelines("\n= MISSING =\n")
		for clone in unmergedClones:
			romsetLogFile.writelines(clone+"\n")
	romsetLogFile.close()

def createNewRomsetLog(newOtherFiles, failedRomsetFiles):
	if len(newOtherFiles) > 0:
		newOtherFiles.sort()
		failedRomsetFiles.sort()
		romsetLogFile = open(path.join(logFolder, "Log - Romset (to "+deviceName+") - "+systemName+".txt"), "w", encoding="utf-8", errors="replace")
		romsetLogFile.writelines("=== Copied "+str(len(newOtherFiles))+" new ROMs from "+systemName+" to "+deviceName+" ===\n\n")
		for file in newOtherFiles:
			romsetLogFile.writelines(file+"\n")
		if len(failedRomsetFiles) > 0:
			romsetLogFile.writelines("\n= FAILED TO COPY =\n")
			for file in failedRomsetFiles:
				romsetLogFile.writelines(file+"\n")
		romsetLogFile.close()

def createNewFromOtherLog(newOtherFiles, failedOtherFiles):
	updateFolderName = path.basename(updateFromDeviceFolder)
	if len(newOtherFiles) > 0:
		newOtherFiles.sort()
		otherLogFile = open(path.join(logFolder, "Log - "+updateFolderName+" (to "+deviceName+").txt"), "w", encoding="utf-8", errors="replace")
		otherLogFile.writelines("=== Copied "+str(len(newOtherFiles))+" new files from "+updateFolderName+" to "+deviceName+" ===\n\n")
		for file in newOtherFiles:
			otherLogFile.writelines(file+"\n")
		if len(failedOtherFiles) > 0:
			otherLogFile.writelines("\n= FAILED TO COPY =\n")
			for file in failedOtherFiles:
				otherLogFile.writelines(file+"\n")
		otherLogFile.close()

def createNewInOtherLog(newFilesInOther, failedOtherFiles):
	updateFolderName = path.basename(updateFromDeviceFolder)
	if len(newFilesInOther):
		newFilesInOther.sort()
		otherLogFile = open(path.join(logFolder, "Log - "+updateFolderName+" (from "+deviceName+").txt"), "w", encoding="utf-8", errors="replace")
		otherLogFile.writelines("=== Copied "+str(len(newFilesInOther))+" new files from "+deviceName+" to "+updateFolderName+" ===\n\n")
		for file in newFilesInOther:
			otherLogFile.writelines(file+"\n")
		if len(failedOtherFiles) > 0:
			otherLogFile.writelines("\n= FAILED TO COPY =\n")
			for file in failedOtherFiles:
				otherLogFile.writelines(file+"\n")
		otherLogFile.close()

if __name__ == '__main__':
	main()
