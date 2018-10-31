import sys

if __name__ == "__main__":
    sheet_size = (2048,3040)
    argx,argy = [int(val) for val in sys.argv[1:3]]

    row_offset = int((3040-argy)/32)*int(sheet_size[0]/32)
    col_offset = int(argx/32)

    print(row_offset+col_offset)
