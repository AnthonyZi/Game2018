import sys
import skimage.io as skiio
import numpy as np

if __name__ == "__main__":
    infile,outfile = sys.argv[1:3]

    img = skiio.imread(infile)
    out = np.zeros((128,128,4), dtype=np.uint8)
    out[:,32:,:] = img
    out[:,0:32,:] = img[:,32:64,:]

    skiio.imsave(outfile,out)
