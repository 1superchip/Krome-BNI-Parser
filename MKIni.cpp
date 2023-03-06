// this file is a partial decomp of MKIni.cpp from Ty the Tasmanian Tiger 3

// ty 3 was not compiled with 1.3.2
// most likely compiled with 2.0 - 2.7

typedef signed char s8;
typedef signed short s16;
typedef signed long s32;
typedef signed long long s64;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned long u32;
typedef unsigned long size_t;
typedef unsigned long long u64;

typedef unsigned short ushort;
typedef unsigned int uint;

typedef volatile u8 vu8;
typedef volatile u16 vu16;
typedef volatile u32 vu32;
typedef volatile u64 vu64;
typedef volatile s8 vs8;
typedef volatile s16 vs16;
typedef volatile s32 vs32;
typedef volatile s64 vs64;

typedef float f32;
typedef double f64;
typedef volatile f32 vf32;
typedef volatile f64 vf64;

typedef int BOOL;

#define nullptr 0
#define NULL 0

extern "C" int strlen(const char*);

struct MKIni;

struct MKIniLine {
    short nmbrOfStrings;
    u16 unk2; // section name index
    u16 unk4; // field name index
    u16 unk6; // string table index
    s16 unk8; // subline index
    u16 unkA; // mask name index
    MKIni* pIni;
	char* GetSectionName(void);
	char* GetFieldName(void);
	char* GetMaskName(void);
	char* GetString(int);
	bool GetBool(int);
	bool GetFlag(int);
	int GetInt(int);
	float GetFloat(int);
    bool IsField(const char*);
	int GetNmbrOfSubLines(void);
};

struct INI_FileData {
    char name[0x24];
    int mLineCount;
    int mUnused28;
    int stringTableOffset;
    int unk30;
    int mSectionIndexTableOffset;
    uint unk38;
    int unk3C;
    int unk40;
};

struct MKIni {
    char* mpStrings; // string table
    u16* unk4;
    u16* unk8; // section name index array
    uint unkC; // section count?
    MKIniLine* mpLines;
    void* mpFile; // ini file pointer
	int unk18;
    char unk[0x20];
    int lineCount;
    int unk40;
    void* unk44;
    void* unk48;
    void* unk4C;
	void Init(const char*, int, const char*);
	void Deinit(void);
	void Warning(const char*);
	void* GotoLine(const char*, const char*);
	
	bool IsSection(const char*);
	MKIniLine* GetFirstLine(void);
	MKIniLine* GetNextLine(MKIniLine*);
	MKIniLine* GetPrevLine(MKIniLine*);
	MKIniLine* GetSubLine(MKIniLine*);
	void ReadBinary(const char*);
	bool IsMaskedOut(MKIniLine*);
	bool Exists(const char*);
};

static MKIniLine* pIni_CurrentLineArray;

// Case Insensitive Hash Function
static uint StringHash(const char* str, int div) {
    uint hash = 0;
    uint len = strlen(str);
    int idx = 0;
    for(int i = 0; i < len; i++) {
        hash = (hash * 0x11) + (str[i] | 0x20);
    }
    return hash % div;
}


static int iniSectionCompare(const void* s1, const void* s2) {
    MKIniLine* pLine = &pIni_CurrentLineArray[*(u16*)s2];
    return stricmp((char*)s1, pLine->GetSectionName());
}

// MKIni::Init(const char*, int, const char*)

// MKIni::Deinit()

void MKIni::Warning(const char* str) {}

MKIniLine* MKIni::GotoLine(const char* s1, const char* s2) {
    if (!mpLines || mpLines[0].unk0 == -1)
        return 0;
    if (!s1 && !s2)
        return mpLines;
    MKIniLine* line = mpLines;
    bool r3 = 0;
    if (s1 && unkC && unk4C) {
        int strHash = StringHash(s1, unkC);
        u16 sectionIdx = unk8[strHash];
        if (unk8[strHash] == 0xFFFF || stricmp(mpLines[sectionIdx].GetSectionName(), (char*)s1) != 0) {
            pIni_CurrentLineArray = mpLines;
            u16* searchLine =
                (u16*)Util_BinarySearch((const void*)s1, unk48, unk4C, 2, iniSectionCompare);
            pIni_CurrentLineArray = NULL;
            if (searchLine == 0) {
                return 0;
            }
            line = &mpLines[*searchLine];
        } else {
            line = &mpLines[unk8[strHash]];
        }
        r3 = 1;
    }
    if (s2) {
        if (!s1) {
            while (line > mpLines && !line->GetSectionName()) {
                line--;
            }

            if (line->GetSectionName()) {
                line++;
            }
        } else if (r3) {
            line++;
        }
        while (line->unk0 != -1) {
            if (line->GetSectionName()) {
                return 0;
            }
            if (line->GetFieldName()) {
                if (stricmp((char*)s2, line->GetFieldName()) == 0) {
                    break;
                }
            }
            line++;
        }
        
        if (line->unk0 == -1) {
            return 0;
        }
    }
    
    if (line->unk0 == -1) {
        return 0;
    }
    
    return line;
}

char* MKIniLine::GetSectionName(void) {
    if (unk2 == 0xFFFF)
        return 0;
    return (char*)&pIni->mpStrings[unk2];
}

char* MKIniLine::GetFieldName(void) {
    if (unk4 == 0xFFFF)
        return 0;
    return (char*)&pIni->mpStrings[unk4];
}

char* MKIniLine::GetMaskName(void) {
    if (unkA == 0xFFFF)
        return 0;
    return (char*)&pIni->mpStrings[unkA];
}

char* MKIniLine::GetString(int stringIndex) {
    if (stringIndex >= nmbrOfStrings)
        return 0;
    return &pIni->mpStrings[pIni->unk4[unk6 + stringIndex] * 4];
}








bool MKIniLine::IsField(const char* str) {
    bool ret = false;
    if (unk4 != 0xFFFF) {
        if (stricmp((char*)&pIni->mpStrings[unk4], (char*)str) == 0) {
            ret = true;
        }
    }
    return ret;
}


MKIniLine* MKIni::GetNextLine(MKIniLine* pLine) {
    MKIniLine* nextLine;
    if (!pLine || (nextLine = pLine + 1) == &mpLines[lineCount] || nextLine->nmbrOfStrings == -1) {
        nextLine = 0;
    }
    if (nextLine) {
        if (IsMaskedOut(nextLine)) {
            nextLine = nextLine->pIni->GetNextLine(nextLine); // -inline on instead of -inline auto?
        }
    }
    return nextLine;
}

MKIniLine* MKIni::GetPrevLine(MKIniLine* pLine) {
    MKIniLine* prevLine;
    if (!pLine || pLine == mpLines || pLine->nmbrOfStrings == -1) {
        prevLine = 0;
    } else {
        prevLine = pLine - 1;
    }
    if (prevLine) {
        if (IsMaskedOut(prevLine)) {
            prevLine = prevLine->pIni->GetPrevLine(prevLine); // -inline on instead of -inline auto?
        }
    }
    return prevLine;
}

MKIniLine* MKIni::GetSubLine(MKIniLine* pLine) {
    MKIniLine* subLine;
    if (!pLine || pLine->unk8 == -1) {
        subLine = 0;
    } else {
        subLine = &mpLines[pLine->unk8];
    }
    if (subLine) {
        if (IsMaskedOut(subLine)) {
            subLine = subLine->pIni->GetNextLine(subLine);
        }
    }
    return subLine;
}

int MKIniLine::GetNmbrOfSubLines(void) {
    int subline_count = 0;
    MKIniLine* subLine = pIni->GetSubLine(this);
    while (subLine != NULL) {
        subLine = pIni->GetNextLine(subLine);
        subline_count++;
    }
    return subline_count;
}

void* FileSys_Load(const char*, int*, void*, int);

// https://decomp.me/scratch/A4KTZ
void MKIni::ReadBinary(const char* iniName) {
    INI_FileData* iniFile = (INI_FileData*)FileSys_Load(iniName, &unk40, 0, -1);
    int fileData = (int)iniFile + 0x44;
    mpLines = (MKIniLine*)fileData;
    mpStrings = (char*)(fileData + iniFile->stringTableOffset);
    unk4 = (u16*)(fileData + iniFile->unk30);
    unk8 = (u16*)(fileData + iniFile->mSectionIndexTableOffset);
    unkC = iniFile->unk38;
    unk48 = (u16*)(fileData + iniFile->unk3C);
    unk4C = (u16*)iniFile->unk40;
    mpFile = iniFile;
    lineCount = iniFile->mLineCount;
    for(int i = 0; i < lineCount; i++) {
        mpLines[i].pIni = this;
    }
}

