# Written by Chippy
# 2022, 2023

import os, sys, struct

# default to big endian
# this is overwritten right away anyways
endian = 1

def read_byte_big(fd):
    return struct.unpack('>b', fd.read(1))[0]
    
def read_short_big(fd):
    return struct.unpack('>h', fd.read(2))[0]

def read_ushort_big(fd):
    return struct.unpack('>H', fd.read(2))[0]

def read_int_big(fd):
    return struct.unpack('>i', fd.read(4))[0]

def read_uint_big(fd):
    return struct.unpack('>I', fd.read(4))[0]

def read_byte_little(fd):
    return struct.unpack('<b', fd.read(1))[0]
    
def read_short_little(fd):
    return struct.unpack('<h', fd.read(2))[0]
    
def read_ushort_little(fd):
    return struct.unpack('<H', fd.read(2))[0]

def read_int_little(fd):
    return struct.unpack('<i', fd.read(4))[0]

def read_uint_little(fd):
    return struct.unpack('<I', fd.read(4))[0]

def read_uint_endian(fd):
    if endian == 1:
        return read_uint_big(fd)
    return read_uint_little(fd)

def read_int_endian(fd):
    if endian == 1:
        return read_int_big(fd)
    return read_int_little(fd)

def read_ushort_endian(fd):
    if endian == 1:
        return read_ushort_big(fd)
    return read_ushort_little(fd)

def read_short_endian(fd):
    if endian == 1:
        return read_short_big(fd)
    return read_short_little(fd)

def read_string(fd):
    res = ''
    byte = fd.read(1)
    while byte != b'\x00':
        res += (byte.decode('ascii'))
        byte = fd.read(1)
    return res

def read_string_len(fd, len):
    res = ''
    while len != 0:
        byte = fd.read(1)
        res += (byte.decode('ascii'))
        len -= 1
    return res

def stricmp(s1, s2):
    s1 = s1.lower()
    s2 = s2.lower()
    if s1 == s2:
        return 0
    if s1 < s2:
        return -1
    return 1

def StringHash(string, div):
    strlen = len(string)
    strhash = 0;
    for i in range(strlen):
        strhash = (strhash * 0x11) + (string.encode('utf-8')[i] | 0x20)
    return strhash % div

"""void* Util_BinarySearch(const void *valueToFind, void *arr,
            int count, int elemSize, int (*compareFunc)(const void *, const void *)) {
	int cmpResult;
	int low;
	int high;
	int mid;
	void *currEntry;

	high = count - 1;
	low = 0;
	while (low <= high) {
		mid = (low + high) >> 1;
		currEntry = (u8 *)arr + ((mid * elemSize)); // need the u8* cast here
		cmpResult = compareFunc(valueToFind, currEntry);
		if (cmpResult == 0) {
			return currEntry;
		}
		if (cmpResult < 0) {
			high = mid - 1;
		} else {
			low = mid + 1;
		}
	}
	return NULL;
}"""

def iniSectionCompare(s1, s2):
    return stricmp(s1, s2)

# specialized binary search function
def Util_BinarySearch(valueToFind, array, count, elemSize, compareFunc, bni):
    high = count - 1
    low = 0
    print("unk48: %d" % bni["unk48"])
    bni["fd"].seek(bni["unk48"], 0)
    global endian
    if endian == 1:
        data = struct.unpack('>' + 'h' * count, bni["fd"].read(elemSize * count))
    else:
        data = struct.unpack('<' + 'h' * count, bni["fd"].read(elemSize * count))
    print(data)
    while low <= high:
        mid = (low + high) // 2
        currIdx = data[mid]
        currLine = bni["mLines"][currIdx]
        cmpResult = compareFunc(valueToFind, currLine["sectionName"])
        if cmpResult == 0:
            return currIdx
        if cmpResult < 0:
            high = mid - 1
        else:
            low = mid + 1
    return -1
        

def ReadLines(fd, bni):
    lineOffset = 0x44
    fd.seek(lineOffset, 0)
    lines = []
    for i in range(bni["lineCount"]):
        line = {
            "unk0": read_short_endian(fd),
            "unk2": read_ushort_endian(fd),
            "unk4": read_ushort_endian(fd),
            "unk6": read_ushort_endian(fd),
            "unk8": read_short_endian(fd),
            "unkA": read_ushort_endian(fd)
        }
        line["sectionName"] = ""
        line["fieldName"] = ""
        line["maskName"] = ""
        line["strings"] = []
        if line["unk0"] != -1:
            if line["unk2"] != 0xFFFF:
                fd.seek(bni["stringTable"] + ((line["unk2"] * 4) & 0x3FFFC), 0)
                line["sectionName"] = read_string(fd)
            if line["unk4"] != 0xFFFF:
                fd.seek(bni["stringTable"] + ((line["unk4"] * 4) & 0x3FFFC), 0)
                line["fieldName"] = read_string(fd)
            maskName = ""
            if line["unkA"] != 0xFFFF:
                fd.seek(bni["stringTable"] + ((line["unkA"] * 4) & 0x3FFFC), 0)
                line["fieldName"] = read_string(fd)
            for str_idx in range(line["unk0"]):
                idx = (line["unk6"] + str_idx) * 2
                fd.seek(bni["unk4"] + idx, 0)
                tableIdx = (read_ushort_endian(fd) * 4) & 0x3FFFC
                fd.seek(bni["stringTable"] + tableIdx, 0)
                line["strings"].append(read_string(fd))
        lines.append(line)
        lineOffset += 0x10
        fd.seek(lineOffset, 0)
    return lines

def ReadBNI(fd):
    fd.seek(0, 0)
    iniName = read_string(fd)
    fd.seek(0x2C, 0) # seek to beginning of data
    stringTable = 0x44 + read_int_endian(fd)
    shortTableUnk4 = 0x44 + read_int_endian(fd)
    shortTableUnk8 = 0x44 + read_int_endian(fd)
    unkC = read_int_endian(fd)
    unk48 = 0x44 + read_int_endian(fd)
    unk4C = read_int_endian(fd)
    fd.seek(0x24, 0)
    lineCount = read_int_endian(fd)
    bni = {
        "name": iniName,
        "stringTable": stringTable,
        "unk4": shortTableUnk4,
        "unk8": shortTableUnk8,
        "unkC": unkC,
        "lineCount": lineCount,
        "unk48": unk48,
        "unk4C": unk4C,
        "fd": fd
    }
    bni["mLines"] = ReadLines(fd, bni)
    return bni

# this is not guaranteed to work
# s1 = section name
# s2 = field
def BNI_GotoLine(bni, s1, s2):
    if len(bni["mLines"]) == 0 or bni["mLines"][0]["unk0"] == -1:
        return "" # what should i return for NULL pointer in C++, 0 or empty string?
    # not sure how to handle NULL pointer checks, whether I should check if the type is a string or not
    if s1 == "" and s2 == "":
        return bni["mLines"][0]
    lineIdx = 0
    line = bni["mLines"][lineIdx]
    r3 = 0
    if (s1 and bni["unkC"] and bni["unk4C"]):
        strHash = (StringHash(s1, bni["unkC"]) * 2) & 0x1fffe
        print(bni["unk8"] + strHash)
        bni["fd"].seek(bni["unk8"] + strHash, 0)
        sectionIdx = read_ushort_endian(bni["fd"])
        print(sectionIdx)
        if sectionIdx == 0xFFFF or (stricmp(bni["mLines"][sectionIdx]["sectionName"], s1) != 0):
            foundIdx = Util_BinarySearch(s1, [], bni["unk4C"], 2, iniSectionCompare, bni)
            if foundIdx == -1:
                return 0
            lineIdx = foundIdx
            line = bni["mLines"][lineIdx]
        else:
            lineIdx = sectionIdx
            line = bni["mLines"][lineIdx]
        r3 = 1
    if (type(s2) == str):
        if s1 != "":
        #if (type(s1) != str):
            print("hsd")
            while lineIdx > 0 and line["sectionName"] == "":
                lineIdx -= 1
                line = bni["mLines"][lineIdx]
            if line["sectionName"] != "":
                lineIdx += 1
                line = bni["mLines"][lineIdx]
        elif r3 == 1:
            lineIdx += 1
            line = bni["mLines"][lineIdx]
        while line["unk0"] != -1:
            if line["sectionName"] != "":
                return 0
            if line["fieldName"] != "":
                if stricmp(s2, line["fieldName"]) == 0:
                    break
            lineIdx += 1
            line = bni["mLines"][lineIdx]
        if line["unk0"] == -1:
            return 0
    
    if line["unk0"] == -1:
        return 0
    return line

def BNI_GetPrevLine(bni, pLine):
    if pLine == None or pLine not in bni["mLines"] or pLine["unk0"] == -1:
        return None
    line = bni["mLines"][bni["mLines"].index(pLine) - 1]
    # should implement IsMaskedOut
    return line

endianDict = {
    "little": 0,
    "big": 1
}

def main():
    args = sys.argv[1:]
    if len(args) < 3:
        print("Usage:\nRequired: BNI Filepath, Out Filepath, Endian: 'Big' or 'Little'\nPS2 and Xbox: 'little', GC and Wii: 'big'")
        return
    global endian
    endian = endianDict[args[2].lower()]
    if os.path.exists(args[0]):
        with open(args[0], "rb") as fd:
            bni = ReadBNI(fd)
            #print("Hash Table: %d\n" % bni["unk8"])
            with open(args[1], "wt") as out_fd:
                for line in bni["mLines"]:
                    """if line["unk8"] != -1:
                        line = BNI_GetPrevLine(bni, line)
                        print(line, bni["mLines"][line["unk8"]])
                        print("\n\n")
                        print(line, bni["mLines"][line["unk8"] + 1])
                        print("\n\n")"""
                    if line["unk0"] == -1:
                        out_fd.write('\n---------------\n')
                    if line["sectionName"] != "":
                        out_fd.write('\n' + line["sectionName"] + '\n')
                    if line["fieldName"] != "":
                        out_fd.write(line["fieldName"] + ' ')
                        for text in line["strings"]:
                            out_fd.write(text)
                            if (len(line["strings"]) > 1) and text != line["strings"][-1]:
                                # if there are multiple elements on the line
                                # add a comma after each except for the last element
                                out_fd.write(', ')
                        out_fd.write('\n')
                    #out_fd.write('\n')
                    
            #print(ReadBNI(fd))

if __name__ == "__main__":
    main()